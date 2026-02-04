---
title: "SID Filtering"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
weight: 200
---
However, the SID history is only necessary when migrated users must have access to resources in their previous domain(s). If no user has this requirement, SID filtering can be applied 

```
([System.DirectoryServices.ActiveDirectory.Forest]::GetCurrentForest()).GetAllTrustRelationships()
```


[Security Considerations for Trusts: Domain and Forest Trusts | Microsoft Learn](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc755321\(v=ws.10\)?redirectedfrom=MSDN#disabling-sid-filter-quarantining-on-external-trusts)

[SID Filtering during AD Migrations - Active Directory FAQ](https://activedirectoryfaq.com/2015/10/active-directory-sid-filtering/)
