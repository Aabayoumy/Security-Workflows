---
title: "Audit & Disable NTLM"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
weight: 20
---

Steps to configure NTLMv2:
1. Enable Audit.
2. Change Log size.
3. Collect NTLMv1 events.
4. Enforce NTLMv2.
5. Disable Audit.



##### Enable Audit 
Audit with GPO:
1. Create new GPO named Audit NTLM
2. Edit and Go to  `Computer Configuration > Policies > Windows Settings > Security Settings > Local Policies > Security Options`
3. Configure this settings:

| Setting                                                                   | Value                            |
| ------------------------------------------------------------------------- | -------------------------------- |
| Network security: Restrict NTLM: Audit Incoming NTLM Traffic              | Enable auditing for all accounts |
| Network security: Restrict NTLM: Audit NTLM authentication in this domain | Enable all                       |
| Network security: Restrict NTLM: Outgoing NTLM traffic to remote servers  | Audit all                        |
[Network security Restrict NTLM Audit incoming NTLM traffic - Windows 10 | Microsoft Learn](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/network-security-restrict-ntlm-audit-incoming-ntlm-traffic)
[Network security Restrict NTLM Audit NTLM authentication in this domain | Microsoft Learn](https://learn.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/network-security-restrict-ntlm-audit-ntlm-authentication-in-this-domain)
[Network security Restrict NTLM Outgoing traffic (Windows 10) | Microsoft Learn](https://learn.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/network-security-restrict-ntlm-outgoing-ntlm-traffic-to-remote-servers)



##### Change Log size 
1. Navigate to `Event viewer > Windows Logs > Security` 
2. Right-click  `Properties > Maximum log size > 2,097,152 (2G)` 
3. repeat on all DCs.


##### Collect NTLMv1 events 

To see LDAP logs open `Event viewer > Windows Logs > Security` and search for eventID 4624
02- NTLM Audit (TODO: link: 02- NTLM Audit)

**Old Script:**
```powershell
#collect ntlm logs and export to csv,run on each dc
if (!([Security.Principal.WindowsIdentity]::GetCurrent().Groups -contains 'S-1-5-32-544')) { clear-host; Read-Host "Please run PowerShell As Administrator and rerun this commands, Press any key to exit"; exit }
Import-Module activedirectory
$OutputPath = "C:\_GB\"; If(!(test-path -PathType container $OutputPath)){ MKDIR $OutputPath }
$OutputFile = "$OutputPath\NTLM_$($env:computername)_$((Get-Date).ToString('dd-MMMM-yyyy')).csv"
$Events = Get-WinEvent -Logname security -FilterXPath "Event[System[(EventID=4624)]]and (Event[EventData[Data[@Name='LmPackageName']='NTLM V2']] or Event[EventData[Data[@Name='LmPackageName']='NTLM V1']])" | Select-Object `
@{Label='Time';Expression={$_.TimeCreated.ToString('g')}},
@{Label='UserName';Expression={$_.Properties[5].Value}},
@{Label='WorkstationName';Expression={$_.Properties[11].Value}},
@{Label='WorkstationIP';Expression={$_.Properties[18].Value}},
@{Label='LogonType';Expression={$_.properties[8].value}},
@{Label='LmPackageName';Expression={$_.properties[14].value}},
@{Label='ImpersonationLevel';Expression={$_.properties[20].value}}
$Events | Export-Csv $OutputFile -NoTypeInformation
Start-Process -FilePath $OutputPath
```


##### Enforce NTLMv2
Using GPO:
4. Edit Default Domain Controllers policy and navigate to:
`Computer Configuration > Policies > Windows Settings > Security Settings > Local Policies > Security Options`
5. Apply this setting:

| Setting                                            | Value                     |
| -------------------------------------------------- | ------------------------- |
| Network security: LAN Manager authentication level | Send NTLMv2 response only |
**Policy Options:**

| Setting                                                    | Description                                                                                                                                                                                                              | Registry security level |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------- |
| Send LM & NTLM responses                                   | Client devices use LM and NTLM authentication, and they never use NTLMv2 session security. Domain controllers accept LM, NTLM, and NTLMv2 authentication.                                                                | 0                       |
| Send LM & NTLM – use NTLMv2 session security if negotiated | Client devices use LM and NTLM authentication, and they use NTLMv2 session security if the server supports it. Domain controllers accept LM, NTLM, and NTLMv2 authentication.                                            | 1                       |
| Send NTLM response only                                    | Client devices use NTLMv1 authentication, and they use NTLMv2 session security if the server supports it. Domain controllers accept LM, NTLM, and NTLMv2 authentication.                                                 | 2                       |
| Send NTLMv2 response only                                  | Client devices use NTLMv2 authentication, and they use NTLMv2 session security if the server supports it. Domain controllers accept LM, NTLM, and NTLMv2 authentication.                                                 | 3                       |
| Send NTLMv2 response only. Refuse LM                       | Client devices use NTLMv2 authentication, and they use NTLMv2 session security if the server supports it. Domain controllers refuse to accept LM authentication, and they'll accept only NTLM and NTLMv2 authentication. | 4                       |
| Send NTLMv2 response only. Refuse LM & NTLM                | Client devices use NTLMv2 authentication, and they use NTLMv2 session security if the server supports it. Domain controllers refuse to accept LM and NTLM authentication, and they'll accept only NTLMv2 authentication. | 5                       |
[Network security LAN Manager authentication level - Windows 10 | Microsoft Learn](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/network-security-lan-manager-authentication-level) 



6. **Edit the GPO:**
    
    - Right-click the GPO and select "Edit."
    - In the Group Policy Management Editor, navigate to:
        
        `Computer Configuration -> Policies -> Windows Settings -> Security Settings -> Local Policies -> Security Options`
        
7. **Configure NTLMv1 Restriction:**
    
    - Find the policy named **Network security: LAN Manager authentication level**.
    - Double-click this policy to edit it.
    - Set it to **Send NTLMv2 response only. Refuse LM & NTLM**. This setting ensures that only NTLMv2 is used, effectively blocking NTLMv1 and LM (LAN Manager) responses.
    -


Common NTLM audit event IDs include 4624 (logon) and 4776 (NTLM authentication)

[HOWTO: Detect NTLMv1 Authentication - The things that are better left unspoken](https://dirteam.com/sander/2022/06/15/howto-detect-ntlmv1-authentication/)



## Check Security Log Event 4624
```
Sample Event ID: 4624  
Source: Microsoft-Windows-Security-Auditing  
Event ID: 4624  
Task Category: Logon  
Level: Information  
Keywords: Audit Success  
Description:  
An account was successfully logged on.  
Subject:  
Security ID: NULL SID  
Account Name: -  
Account Domain: -  
Logon ID: 0x0  
Logon Type: 3  

New Logon:  
Security ID: ANONYMOUS LOGON  
Account Name: ANONYMOUS LOGON  
Account Domain: NT AUTHORITY  
Logon ID: 0xa2226a  
Logon GUID: {00000000-0000-0000-0000-000000000000}

Process Information:  
Process ID: 0x0  
Process Name: -  
Network Information:  
Workstation Name: Workstation1  
Source Network Address:\<ip address>  
Source Port: 49194

Detailed Authentication Information:  
Logon Process: NtLmSsp  
Authentication Package: NTLM  
Transited Services: -  
Package Name (NTLM only): NTLM V1  
Key Length: 128
```


[Network security LAN Manager authentication level - Windows 10 | Microsoft Learn](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/network-security-lan-manager-authentication-level) 
[Farewell NTLM - It is time to disable NTLM](https://www.scip.ch/en/?labs.20210909)

[NTLM Blocking and You: Application Analysis and Auditing Methodologies in Windows 7 | Microsoft Community Hub](https://techcommunity.microsoft.com/blog/askds/ntlm-blocking-and-you-application-analysis-and-auditing-methodologies-in-windows/397191)
[The evolution of Windows authentication | Windows IT Pro Blog](https://techcommunity.microsoft.com/blog/windows-itpro-blog/the-evolution-of-windows-authentication/3926848)
[Deprecating NTLM is Easy and Other Lies We Tell Ourselves](https://syfuhs.net/deprecating-ntlm-is-easy-and-other-lies-we-tell-ourselves)



We enabled auditing for LDAP on all Domain Controllers using the GPO (Audit LDAP).
We found that NTLM auditing is already enabled in the (Default Domain Controller)  GPO.
We increased the size of the event log for NTLM to 2GB and for LDAP to 100MBon one Domain Controller, please apply these changes to all Domain Controllers.
