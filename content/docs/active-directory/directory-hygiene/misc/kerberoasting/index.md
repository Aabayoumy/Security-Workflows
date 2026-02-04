---
title: "Kerberoasting"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
weight: 80
tags: ["18", "kerberoasting"]
---

Any account having the attribute SPN populated is considered as a service account.
so an attacker car request TGS for this service and then crack account password


list of domain/forest user accounts that have an associated SPN.  
```powershell
get-aduser -filter {serviceprincipalname -like "*"} -prop serviceprincipalname
```



Kerberoast mitigation is simple: use long, complex passwords (>30 characters) for all service accounts or preferably, use [**Managed Service Accounts**](https://blogs.technet.microsoft.com/askds/2009/09/10/managed-service-accounts-understanding-implementing-best-practices-and-troubleshooting/). If an attacker is using this technique to persist, changing service account passwords at least once a year to something long & complex will help mitigate.



[Sneaky Persistence Active Directory Trick : Dropping SPNs on Admin Accounts for Later Kerberoasting – Active Directory Security](https://adsecurity.org/?p=3466)
