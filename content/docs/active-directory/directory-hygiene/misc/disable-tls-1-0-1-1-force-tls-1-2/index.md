---
title: "Disable TLS 1.0/1.1 and enforce TLS 1.2 (Active Directory)"
date: 2026-02-05T09:00:00
draft: false
authors: ["ahmed"]
weight: 200
tags: ["TLS", "Schannel", "Windows", "Active Directory", "LDAPS", "LDAP"]
---

Goal: disable TLS 1.0 and TLS 1.1 on Domain Controllers (Schannel) while keeping TLS 1.2 enabled, without breaking AD-related dependencies (LDAPS / LDAP StartTLS).

## Scope (what this change impacts)

This is OS-level (Schannel). On Domain Controllers it affects any service that uses Schannel, especially:

- LDAPS (TCP/636)
- LDAP StartTLS (TCP/389)
- Global Catalog over SSL (TCP/3269) (if used)
- AD CS enrollment endpoints hosted on Windows (if present)

Not impacted:

- SMB (TCP/445) does not use TLS; it uses SMB dialect negotiation (SMB2/SMB3) and optional SMB3 encryption.

## GPO linking strategy (DC-only vs domain-wide)

You can deploy Schannel TLS protocol settings in two common ways:

- Domain Controllers OU (AD services focus)
  - Best when the goal is to harden AD endpoints (LDAPS/StartTLS/3269) while minimizing blast radius.
  - Still validate any applications and devices that bind to AD over LDAPS/StartTLS.
- Domain root / all computers (organization-wide hardening)
  - Best when you want consistent TLS posture for all Windows clients and servers.
  - Higher risk of breaking legacy line-of-business apps and third-party agents.

If you are unsure, start with DC-only (pilot), then expand to a broader scope after you confirm there are no TLS 1.0/1.1 dependencies.

## Audit first (confirm what is working today)

Do both: (1) check server configuration, (2) confirm real client traffic/protocol negotiation.

### 0) Enable Schannel logging (audit first)

Schannel can log TLS handshake problems and protocol/cipher mismatches to the System event log.

Registry:

- Key: `HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL`
- Value: `DWORD EventLogging`

Logging levels:

| Value | Schannel logging events |
| ----- | ---------------------- |
| 0     | No events              |
| 1     | Error events           |
| 2     | Warning events         |
| 3     | Error and Warning events |
| 4     | Informational and Success events |
| 5     | Error, Informational, and Success events |
| 6     | Warning, Informational, and Success events |
| 7     | Error, Warning, Informational, and Success events |

Recommended for an audit window: set `EventLogging` to `7`, reproduce/monitor, then return it to a lower level (commonly `1` or `3`).

PowerShell (local):

```powershell
New-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL' -Name 'EventLogging' -PropertyType DWord -Value 7 -Force | Out-Null
Write-Host 'Schannel EventLogging set to 7. Reboot required for full effect.'
```

Note: you must reboot after changing the Schannel logging level.

### Collect Schannel logs and export (with TLS version column)

Use this during your audit window (before and after the GPO change) to export Schannel events from the System log and extract the TLS version from the event message when present.

PowerShell script:

```powershell
param(
  [string[]]$ComputerName = @($env:COMPUTERNAME),
  [int]$Days = 7,
  [string]$OutDir = (Join-Path $PWD 'schannel-audit')
)

$start = (Get-Date).AddDays(-[math]::Abs($Days))
New-Item -ItemType Directory -Path $OutDir -Force | Out-Null

foreach ($c in $ComputerName) {
  Write-Host "Collecting Schannel events from $c since $start ..."

  $events = Get-WinEvent -ComputerName $c -FilterHashtable @{ LogName='System'; ProviderName='Schannel'; StartTime=$start } -ErrorAction Stop

  $rows = foreach ($e in $events) {
    $msg = [string]$e.Message

    # Best-effort extraction; not all Schannel events include a TLS version string.
    $tls = if ($msg -match '(TLS\s*1\.[0-3])') { $matches[1] } else { '' }

    [pscustomobject]@{
      Computer     = $c
      TimeCreated  = $e.TimeCreated
      Level        = $e.LevelDisplayName
      EventId      = $e.Id
      TLSVersion   = $tls
      Message      = $msg
    }
  }

  $safe = ($c -replace '[^A-Za-z0-9_.-]','_')
  $csv  = Join-Path $OutDir "$safe-schannel.csv"
  $json = Join-Path $OutDir "$safe-schannel.json"
  $sum  = Join-Path $OutDir "$safe-schannel-summary.csv"

  $rows | Sort-Object TimeCreated | Export-Csv -NoTypeInformation -Encoding UTF8 $csv
  $rows | Sort-Object TimeCreated | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 $json

  $rows |
    Group-Object TLSVersion,EventId,Level |
    Select-Object @{n='Computer';e={$c}},Name,Count |
    Sort-Object Count -Descending |
    Export-Csv -NoTypeInformation -Encoding UTF8 $sum
}

Write-Host "Done. Output: $OutDir"
```

Notes:

- For remote collection, `Get-WinEvent -ComputerName` requires permissions and RPC/event log access; run from an admin host.
- Not every Schannel event includes a TLS version in the message; the `TLSVersion` column is best-effort.

### 1) Check current protocol settings on a server

Schannel protocol registry paths:

`HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\<TLS version>\Server`

and

`HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\<TLS version>\Client`

Quick PowerShell (local):

```powershell
$base = 'HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols'
'TLS 1.0','TLS 1.1','TLS 1.2' | ForEach-Object {
  $p = Join-Path $base $_
  [pscustomobject]@{
    Protocol = $_
    ServerEnabled = (Get-ItemProperty -Path "$p\Server" -Name Enabled -ErrorAction SilentlyContinue).Enabled
    ServerDisabledByDefault = (Get-ItemProperty -Path "$p\Server" -Name DisabledByDefault -ErrorAction SilentlyContinue).DisabledByDefault
    ClientEnabled = (Get-ItemProperty -Path "$p\Client" -Name Enabled -ErrorAction SilentlyContinue).Enabled
    ClientDisabledByDefault = (Get-ItemProperty -Path "$p\Client" -Name DisabledByDefault -ErrorAction SilentlyContinue).DisabledByDefault
  }
} | Format-Table -AutoSize
```

Interpretation notes:

- Missing keys often means "Windows default" (varies by OS version and patch level).
- For a controlled rollout, explicitly set the values rather than relying on defaults.

### 2) Confirm which TLS versions clients are actually using (recommended)

From a management host (not the server), test each AD endpoint/port you care about.

OpenSSL examples (AD-focused):

```bash
# LDAPS
openssl s_client -connect dc01.example.com:636 -tls1
openssl s_client -connect dc01.example.com:636 -tls1_1
openssl s_client -connect dc01.example.com:636 -tls1_2

# Global Catalog over SSL (if used)
openssl s_client -connect dc01.example.com:3269 -tls1_2
```

Nmap example (quick visibility into enabled protocols/ciphers):

```bash
nmap -Pn -p 636,3269 --script ssl-enum-ciphers dc01.example.com
```

What you want to see before change:

- TLS 1.2 succeeds.
- TLS 1.0 and TLS 1.1 may still succeed today (this is what you plan to remove).

### SMB 445 test (separate from TLS)

If you want to validate SMB on DCs (TCP/445), test SMB dialect/encryption (TLS versions do not apply).

From a Windows client:

```powershell
Test-NetConnection dc01.example.com -Port 445

# Shows the negotiated SMB dialect and encryption in-use for current connections
Get-SmbConnection | Where-Object ServerName -match '^dc01' | Select-Object ServerName,Dialect,Encrypted,Signed
```

From a Linux/macOS host with nmap:

```bash
nmap -Pn -p 445 --script smb-protocols dc01.example.com
```

### 3) Identify legacy dependencies before enforcing

Common "break" sources when disabling TLS 1.0/1.1:

- Old Windows (Win7/2008/2008 R2) without TLS 1.2 support enabled/updated
- Old Java runtimes (older defaults) and embedded appliances
- Old .NET apps that hardcode TLS versions (need "system default" / strong crypto)
- Third-party agents that talk LDAPS/HTTPS with legacy stacks

If you have a load balancer/WAF/reverse proxy, prefer auditing there first (it can usually report TLS versions per client).

## Safe rollout workflow (minimize production impact)

1. Inventory endpoints
   - For AD: list all DCs and where LDAPS/StartTLS/3269 are used.
2. Baseline tests
   - Run `openssl` / `nmap ssl-enum-ciphers` against each DC and record results.
3. Monitor for legacy clients
   - Watch for LDAPS/StartTLS handshake failures (app logs first; Schannel failures are a fallback).
4. Pilot group
   - Apply to a small subset (one DC per site if you have multiple sites).
5. Validate
   - Re-test LDAPS/3269 (TLS 1.2 works; TLS 1.0/1.1 fails).
   - Validate directory-dependent apps (SSO, VPN auth, MFA/NPS, PAM, identity sync, Linux auth, printers/scanners, etc.).
6. Roll forward in batches
   - Expand site-by-site; avoid changing all DCs at once.
7. Rollback plan (must be ready)
   - Keep a GPO/registry rollback prepared to re-enable TLS 1.0/1.1 temporarily if a critical legacy dependency appears.

## Implement via Group Policy (Windows Schannel)

Recommended values (set both Server and Client):

- TLS 1.0: `Enabled=0`, `DisabledByDefault=1`
- TLS 1.1: `Enabled=0`, `DisabledByDefault=1`
- TLS 1.2: `Enabled=1`, `DisabledByDefault=0`

### GPO (recommended)

Use a Computer GPO and set Registry Preferences for these keys:

- `HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.0\Server`
- `HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.0\Client`
- `HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.1\Server`
- `HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.1\Client`
- `HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.2\Server`
- `HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.2\Client`

Create DWORD values in each key:

- `Enabled` (0 or 1)
- `DisabledByDefault` (0 or 1)

Suggested targeting:

- Link to the `Domain Controllers` OU.
- Pilot with Security Filtering (apply to a small set of DC computer accounts).

### Create the GPO via PowerShell (optional)

This creates/updates a GPO and writes the required Schannel registry values (both Client and Server).

```powershell
$GpoName = 'Disable-TLS1.0-1.1_Enable-TLS1.2'

if (-not (Get-GPO -Name $GpoName -ErrorAction SilentlyContinue)) {
  New-GPO -Name $GpoName -Comment 'Disable TLS 1.0/1.1; ensure TLS 1.2 enabled (Schannel). Reboot required.' | Out-Null
}

$settings = @(
  @{ Proto='TLS 1.0'; Enabled=0; DisabledByDefault=1 }
  @{ Proto='TLS 1.1'; Enabled=0; DisabledByDefault=1 }
  @{ Proto='TLS 1.2'; Enabled=1; DisabledByDefault=0 }
)

foreach ($s in $settings) {
  foreach ($side in 'Client','Server') {
    $key = "HKLM\\SYSTEM\\CurrentControlSet\\Control\\SecurityProviders\\SCHANNEL\\Protocols\\$($s.Proto)\\$side"
    Set-GPRegistryValue -Name $GpoName -Key $key -ValueName 'Enabled' -Type DWord -Value $s.Enabled
    Set-GPRegistryValue -Name $GpoName -Key $key -ValueName 'DisabledByDefault' -Type DWord -Value $s.DisabledByDefault
  }
}

Write-Host "Created/updated GPO: $GpoName"
Write-Host 'Link it to the Domain Controllers OU (pilot with security filtering), then reboot targeted DCs.'
```

### Local PowerShell (single DC)

```powershell
$base = 'HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols'

$targets = @(
  @{ Proto='TLS 1.0'; Enabled=0; DisabledByDefault=1 }
  @{ Proto='TLS 1.1'; Enabled=0; DisabledByDefault=1 }
  @{ Proto='TLS 1.2'; Enabled=1; DisabledByDefault=0 }
)

foreach ($t in $targets) {
  foreach ($side in 'Server','Client') {
    $p = Join-Path $base (Join-Path $t.Proto $side)
    New-Item -Path $p -Force | Out-Null
    New-ItemProperty -Path $p -Name 'Enabled' -PropertyType DWord -Value $t.Enabled -Force | Out-Null
    New-ItemProperty -Path $p -Name 'DisabledByDefault' -PropertyType DWord -Value $t.DisabledByDefault -Force | Out-Null
  }
}

Write-Host 'Done. Reboot recommended for full effect.'
```

Notes:

- A reboot is the safest way to ensure all services pick up Schannel protocol changes.
- If rebooting is hard, schedule role-by-role maintenance windows and verify after each batch.

## App compatibility (avoid "TLS 1.2 is enabled but client still fails")

Even after enabling TLS 1.2, some apps may still attempt TLS 1.0/1.1 unless configured.

### .NET (common)

For older .NET Framework apps, consider enabling system-default TLS and strong crypto (test first; apply via GPO if needed):

- `HKLM\SOFTWARE\Microsoft\.NETFramework\v4.0.30319` `SchUseStrongCrypto`=1
- `HKLM\SOFTWARE\WOW6432Node\Microsoft\.NETFramework\v4.0.30319` `SchUseStrongCrypto`=1
- `HKLM\SOFTWARE\Microsoft\.NETFramework\v4.0.30319` `SystemDefaultTlsVersions`=1
- `HKLM\SOFTWARE\WOW6432Node\Microsoft\.NETFramework\v4.0.30319` `SystemDefaultTlsVersions`=1

## Verify and document

After applying (and rebooting):

- TLS 1.0 test should fail: `openssl s_client ... -tls1`
- TLS 1.1 test should fail: `openssl s_client ... -tls1_1`
- TLS 1.2 test should succeed: `openssl s_client ... -tls1_2`

Keep a small evidence table per server/endpoint (date, tester host, port, result). This makes it safe to roll out broadly.

## Rollback (temporary)

If a critical legacy dependency is found, temporarily re-enable TLS 1.0/1.1 by setting:

- TLS 1.0/1.1: `Enabled=1`, `DisabledByDefault=0`

Then schedule remediation of the legacy client (patch/upgrade/configure) and re-disable TLS 1.0/1.1.

## Sources

https://learn.microsoft.com/en-us/windows-server/security/tls/tls-registry-settings
