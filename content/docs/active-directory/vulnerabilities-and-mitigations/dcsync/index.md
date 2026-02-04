---
title: "DCSync"
date: 2026-02-03T08:51:11
draft: false
authors: ["ahmed"]
weight: 200
---
```powershell
# list users that can perform DCsync
$DN=(Get-ADDomain).DistinguishedName
Get-ACL "AD:\$DN" | Select-Object -ExpandProperty Access | Where-Object {($_.ObjectType -eq '89e95b76-444d-4c62-991a-0facbeda640c' -or $_.ObjectType -eq '1131f6aa-9c07-11d1-f79f-00c04fc2dcd2')} | select IdentityReference
```
