---
title: "Kerberos RC4 audit and remediation"
date: 2026-02-05T10:00:00
draft: false
authors: ["ahmed"]
weight: 200
tags: ["kerberos", "rc4", "kerberoasting"]
aliases:
  - /docs/active-directory/kerberos_rc4_audit_cve-2026-20833/
  - /docs/active-directory/protocol-hardening/rc4/
  - /docs/active-directory/protocol-hardening/kerberos/audit-and-disable-rc4/
---

RC4-HMAC in Kerberos is weak and commonly abused (for example via Kerberoasting). Microsoft is also moving toward deprecating RC4 in KDC ticket issuance.

Keep this workflow safe:

- Audit first (find what still uses RC4)
- Remediate (enable AES keys / update clients)
- Enforce (disable RC4 via policy)
- Re-audit and monitor

## Background: timeline (reference)

Reference: CVE-2026-20833 (Microsoft deprecating RC4 usage in Kerberos KDC ticket issuance).

Example timeline noted in the original guidance:

- Jan 13, 2026: initial deployment; audit events enabled; `RC4DefaultDisablementPhase` override available.
- April 2026: enforcement mode (default); KDC prefers AES-SHA1; vulnerable connections blocked unless explicitly allowed.
- July 2026: full enforcement; registry override removed; RC4 blocked.

## 1) Audit current RC4 usage

Before enforcing changes, identify any service accounts or clients still relying on RC4.

Do all three audits if possible:

- A) DC event logs (KDC warnings)
- B) Security logs (RC4-encrypted service tickets)
- C) AD object inventory (who is configured to allow RC4/DES)

### A) DC event logs: KDC warning events (System log)

This queries each Domain Controller System log for Kerberos KDC warnings related to insecure encryption and AES enforcement mismatches.

Target events:

- **201:** Client only supports insecure encryption (RC4).
- **202:** Service account only has insecure keys (RC4).
- **205:** Warning about `DefaultDomainSupportedEncTypes` configuration.
- **206:** Service forced to AES, but client doesn't support it.
- **207:** Service forced to AES, but service account doesn't have AES keys.

```powershell
param(
  [int]$DaysBack = 30,
  [string]$ExportPath = ("C:\\Temp\\Kerberos_RC4_Audit_{0}.csv" -f (Get-Date -Format "yyyy-MM-dd"))
)

$StartTime = (Get-Date).AddDays(-[math]::Abs($DaysBack)).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
$XPathFilter = "*[System[(EventID=201 or EventID=202 or EventID=205 or EventID=206 or EventID=207) and Provider[@Name='Microsoft-Windows-Kerberos-Key-Distribution-Center'] and TimeCreated[@SystemTime >= '$StartTime']]]"

Import-Module ActiveDirectory
if (-not (Test-Path 'C:\Temp')) { New-Item -ItemType Directory -Force -Path 'C:\Temp' | Out-Null }

$AllDCs = (Get-ADDomainController -Filter *).HostName

$Results = foreach ($DC in $AllDCs) {
    Write-Host "Querying $DC..."
    try {
        $Events = Get-WinEvent -ComputerName $DC -LogName System -FilterXPath $XPathFilter -ErrorAction Stop
        
        foreach ($Event in $Events) {
            # Create a custom object to include the DC Name and cleaned up message
            [PSCustomObject]@{
                TimeCreated      = $Event.TimeCreated
                DomainController = $DC
                EventID          = $Event.Id
                Message          = $Event.Message
            }
        }
    } catch {
        Write-Host "No events found or unreachable on $DC"
    }
}

if ($Results) {
    $Results | Export-Csv -Path $ExportPath -NoTypeInformation
    Write-Host "Audit complete. Results saved to: $ExportPath"
} else {
    Write-Host "No RC4 warning events found across any Domain Controllers."
}
```

### B) Security logs: RC4-encrypted service tickets (4769)

This exports Kerberos service-ticket requests where `TicketEncryptionType = 0x17` (RC4-HMAC) from every domain controller.

Prerequisite: enable Advanced Audit Policy "Audit Kerberos Service Ticket Operations" (generates 4769/4770/4773).

```powershell
<#{
.SYNOPSIS
  Export Kerberos service-ticket events (4769) encrypted with RC4 (0x17).

.NOTES
  Run as an admin with permission to read DC Security logs.
#}>

param(
  [int]$DaysBack = 7,
  [string]$CsvPath = "C:\\Temp\\RC4-4769.csv"
)

Import-Module ActiveDirectory
if (-not (Test-Path 'C:\Temp')) { New-Item -ItemType Directory -Force -Path 'C:\Temp' | Out-Null }

$start = (Get-Date).AddDays(-[math]::Abs($DaysBack))
$dcs = Get-ADDomainController -Filter *

$events = foreach ($dc in $dcs) {
  Write-Host "Querying $($dc.HostName)..."
  $xpath = "*[System[(EventID=4769) and TimeCreated[@SystemTime>='$($start.ToUniversalTime().ToString('o'))']]] and EventData[Data[@Name='TicketEncryptionType']='0x17']"
  try {
    Get-WinEvent -ComputerName $dc.HostName -LogName Security -FilterXPath $xpath -ErrorAction Stop | ForEach-Object {
      $xml = [xml]$_.ToXml()
      $user = ($xml.Event.EventData.Data | Where-Object { $_.Name -eq 'TargetUserName' }).'#text'
      [pscustomobject]@{
        TimeCreated = $_.TimeCreated
        DomainController = $dc.HostName
        TargetUserName = $user
      }
    }
  } catch {
    Write-Warning "Failed to query $($dc.HostName): $_"
  }
}

if ($events) {
  $events | Sort-Object TimeCreated | Export-Csv -NoTypeInformation -Path $CsvPath
  Write-Host "Saved $($events.Count) events to $CsvPath"
} else {
  Write-Host "No RC4-encrypted service-ticket events found."
}
```

### C) AD inventory: find accounts/computers that allow RC4/DES

This identifies computer accounts that may still allow weak encryption types by checking:

- explicit flags on `msDS-SupportedEncryptionTypes` (RC4 = 0x4)
- DES-only `userAccountControl` flag 0x200000 (often implies legacy behavior)
- objects where encryption types are not defined (defaults may vary)

```powershell
Import-Module ActiveDirectory

(Get-ADComputer -Filter 'msDS-SupportedEncryptionTypes -band 0x1 -or msDS-SupportedEncryptionTypes -band 0x2 -or msDS-SupportedEncryptionTypes -band 0x4 -or userAccountControl -band 0x200000' -Properties Name,SamAccountName,msDS-SupportedEncryptionTypes,ServicePrincipalName |
  Select-Object @{N='Type';E={'Computer'}},Name,SamAccountName,msDS-SupportedEncryptionTypes,ServicePrincipalName) |
  Export-Csv ".\\WeakEncryption_Export.csv" -NoTypeInformation
```

You can run similar queries for users/service accounts if you manage `msDS-SupportedEncryptionTypes` there.

## 2) Check effective Kerberos encryption policy (GPO/registry)

This checks the registry value that corresponds to the policy: "Network security: Configure encryption types allowed for Kerberos".

```powershell
param(
  [string]$RegPath = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\Kerberos\\Parameters",
  [string]$Name = "SupportedEncryptionTypes"
)

try {
  $value = Get-ItemPropertyValue -Path $RegPath -Name $Name -ErrorAction Stop
  Write-Host "SupportedEncryptionTypes: $value"

  if ($value -band 1)  { Write-Host " - DES-CBC-CRC (insecure)" }
  if ($value -band 2)  { Write-Host " - DES-CBC-MD5 (insecure)" }
  if ($value -band 4)  { Write-Host " - RC4-HMAC (insecure)" }
  if ($value -band 8)  { Write-Host " - AES128-HMAC-SHA1" }
  if ($value -band 16) { Write-Host " - AES256-HMAC-SHA1" }
} catch {
  Write-Host "SupportedEncryptionTypes is not explicitly set via policy/registry. Windows defaults apply."
}
```

## 3) Remediation (move to AES)

Recommended encryption types:

- Enable: AES128_HMAC_SHA1, AES256_HMAC_SHA1 (and Future encryption types)
- Disable: RC4_HMAC_MD5, DES

Key points:

- Don’t enable RC4 globally as a workaround.
- When enabling AES for a service account, you may need to reset the account password to generate AES keys.
- Use the audit outputs to identify the exact clients/services that still rely on RC4.

### Enforce via GPO (recommended)

1. Open Group Policy Management Console.
2. Edit a dedicated hardening GPO applied to the intended scope (pilot first).
3. Navigate to:
   `Computer Configuration` -> `Policies` -> `Windows Settings` -> `Security Settings` -> `Local Policies` -> `Security Options`
4. Policy: "Network security: Configure encryption types allowed for Kerberos"
5. Check only:
   - AES128_HMAC_SHA1
   - AES256_HMAC_SHA1
   - Future encryption types
6. Ensure RC4_HMAC_MD5 and DES options are unchecked.

### Handling legacy dependencies

If the audit reveals legacy clients/services that cannot support AES:

1. Identify the specific application and account.
2. Remediate by upgrading/configuring the client/service to support AES.
3. Keep exceptions as narrow and time-bound as possible.

## 4) Verify

- Re-run the 4769 export and confirm RC4 (0x17) stops appearing.
- Re-run the KDC warning query and confirm Event ID 201/202 stop appearing.
- Validate business flows that depend on Kerberos (SSO, app auth, file access, scheduled tasks, etc.).

## Related (TLS cipher RC4)

Kerberos RC4 is separate from RC4 cipher suites in TLS/Schannel. If you’re also hardening TLS and ciphers, see:

- [TLS hardening (disable TLS 1.0/1.1, enforce TLS 1.2)]({{< relref "docs/active-directory/protocol-hardening/tls" >}})
