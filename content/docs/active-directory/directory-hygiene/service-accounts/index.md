---
title: "Service Accounts"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
weight: 200
---
To set custom password policy for service accounts:
1. Open Active Directory Administrative Center
2. From right-bar navigate to `<your_domain> > system > Password Setting Container`
3. Click `New > Password Settings`
4. Set `Minimum password length` to `26` 
5. Set `Precedence` to `1` 
6. Uncheck `Enforce Minimun password age`
7. Set `Enforce account lockout policy` to `30`
8. Add your service accounts group to `Directly Applies To`




`Get-ADServiceAccount -Identity <account> -Properties *`
This command will output all available details about the specified service account.
