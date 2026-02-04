---
title: "Audit and disable RC4"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
weight: 200
tags: ["kerberoasting", "rc4"]
---
## Required Advanced Audit Policy Setting
The specific advanced audit policy you need to enable is: **Audit Kerberos Service Ticket Operations**
This policy is located under the **Account Logon category** in Advanced Audit Policy Configuration. When enabled, it generates the following events:
	•	4769: A Kerberos service ticket was requested
	•	4770: A Kerberos service ticket was renewed
	•	4773: A Kerberos service ticket request failed


```powershell
<#
.SYNOPSIS
    Export all Kerberos service-ticket events (4769) that were encrypted with RC4 (0x17)
    from every domain controller in the current forest.

.DESCRIPTION
    1. Discovers all DCs with Get-ADDomainController.
    2. On each DC, queries the Security log for Event ID 4769 **where
       TicketEncryptionType = 0x17** (RC4-HMAC).
    3. Extracts TimeCreated, TargetUserName, and the DC that logged the event.
    4. Writes the combined results to a CSV.

.PARAMETER DaysBack
    How many days of logs to examine (default = 1).

.PARAMETER CsvPath
    Full path for the CSV (default = .\RC4-4769.csv).

.EXAMPLE
    .\Get-RC4Tickets.ps1 -DaysBack 7 -CsvPath C:\Logs\RC4-ServiceTickets.csv
#>

param(
    [int]$DaysBack = 1,
    [string]$CsvPath = ".\RC4-4769.csv"
)

# Requires ActiveDirectory module
Import-Module ActiveDirectory

# Build time window
$start = (Get-Date).AddDays(-$DaysBack)

# Container for results
$events = @()

Write-Host "Enumerating domain controllers..."
$DCs = Get-ADDomainController -Filter *

foreach ($dc in $DCs) {

    Write-Host "Querying $($dc.HostName)..."

    # XPath: 4769 events whose TicketEncryptionType equals 0x17 (RC4)
    $xpath = "*[System[(EventID=4769) and TimeCreated[@SystemTime>='$($start.ToUniversalTime().ToString("o"))']]] and EventData[Data[@Name='TicketEncryptionType']='0x17']"

    try {
        Get-WinEvent -ComputerName $dc.HostName -LogName Security -FilterXPath $xpath |
        ForEach-Object {
            $xml   = [xml]$_.ToXml()
            $user  = ($xml.Event.EventData.Data | Where-Object {$_.Name -eq 'TargetUserName'}).'#text'
            $time  = $_.TimeCreated

            # Add to array as PSCustomObject
            $events += [pscustomobject]@{
                Computer = $dc.HostName
                User     = $user
                Time     = $time
            }
        }
    }
    catch {
        Write-Warning "Failed to query $($dc.HostName): $_"
    }
}

# Export
if ($events) {
    $events | Sort-Object Time | Export-Csv -NoTypeInformation -Path $CsvPath
    Write-Host "Saved $($events.Count) events to $CsvPath"
} else {
    Write-Host "No RC4-encrypted service-ticket events found."
}

```


## Disabling RC4 & DES in an Active Directory Domain
To enhance security across your Windows domain, it is best practice to disable the legacy RC4 and DES encryption algorithms. This can be achieved through Group Policy and registry settings. Disable RC4 and DES for Kerberos Authentication
### Using Group Policy (Recommended)
	1.	Open Group Policy Management Console (GPMC):
	•	Go to `Computer Configuration` > `Policies` > `Windows Settings` > `Security Settings` > `Local Policies` > `Security Options`.
	2.	Edit the Policy:
	•	Find **Network security: Configure encryption types allowed for Kerberos**.
	•	Set it to only allow:
	•	`AES128_HMAC_SHA1`
	•	`AES256_HMAC_SHA1`
	•	`Future encryption types`
	•	Ensure RC4_HMAC_MD5 and any DES types are unchecked.
	3.	Apply the Policy:
	•	Link this GPO at the domain level to apply to all domain controllers and member servers.
	•	Run `gpupdate /force` on affected systems to apply changes.
	

### Registry Method (Advanced/Complementary)
	On each domain controller, set the following registry key to allow only AES:
	Path: HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa\Kerberos\Parameters
	Value Name: SupportedEncryptionTypes
	•	Value (DWORD): `0x18` (24 decimal) for AES128 and AES256 only
	For additional hardening, you may also set: HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\services\KDC 
	Value Name: `DefaultDomainSupportedEncTypes`
	•	Value: `24` (AES only).

### Disable RC4 & DES for SCHANNEL (TLS/SSL)
	•	Use Group Policy or registry edits to disable weak ciphers for all Windows systems:
	•	Path: HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Ciphers\RC4 128/128
	Value Name: `Enabled`
	•	Value: `0` (DWORD)
	•	Repeat for:
	•	`RC4 40/128`
	•	`RC4 56/128`
	•	`DES 56/56`
	•	`DES 40/56`
	•	Alternatively, use Group Policy:
	•	`Computer Configuration` > `Administrative Templates` > `Network` > `SSL Configuration Settings` > `SSL Cipher Suite Order`
	•	Remove all cipher suites containing `RC4` or `DES`.
