---
title: "SID History auditing group & Removing"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
weight: 200
tags: ["SIDHistory", "trust"]
---
**Technical explanation:**
To migrate accounts to another domain, the attribute SID History should be added to the new account. Despite the fact that numerous hacking tools such as mimikatz allows the creation of the SID History attribute, its official creation requires the presence of a special auditing group named `DOMAIN-$$$`, for example `LAB-$$$` for the `LAB.com` domain.

**Advised solution:**
If a migration is in progress, declare it in PingCastle so this rule won't be triggered. Else, remove this auditing group. You can locate it by using this script:
```powershell
Import-Module ActiveDirectory
# Define the LDAP query filter for groups
$groupFilter = "(sAMAccountName=*$$$)"
# Perform the LDAP query for groups
$groupResults = Get-ADGroup -LDAPFilter $groupFilter -Properties * | Select-Object Name, GroupScope, DistinguishedName
```

```powershell
# List all objects
Get-ADObject -Filter {sidHistory -like '*'} -Properties sidHistory,objectClass -Server (Get-ADDomain).DNSRoot | Select-Object Name,ObjectClass,DistinguishedName,SIDHistory | Format-Table -AutoSize

# Clear all object
Get-ADObject -Filter {sidHistory -like '*'} -Properties sidHistory,objectClass -Server (Get-ADDomain).DNSRoot | Select-Object Name,ObjectClass,DistinguishedName,SIDHistory | Tee-Object -Variable objects | ForEach-Object {Set-ADObject $_ -Remove @{sidHistory=$_.sidHistory.Value}}
```

```powershell
#to list users account having SID history
Get-ADUser -SearchBase "DC=lab,DC=local" -Filter {sidhistory -like '*'} -properties sidhistory
#to remove SID history
Get-ADUser -SearchBase "DC=lab,DC=local" -Filter {sidhistory -like '*'} -properties sidhistory | foreach {Set-ADUser $_ -remove @{sidhistory=$_.sidhistory.value}}
```
