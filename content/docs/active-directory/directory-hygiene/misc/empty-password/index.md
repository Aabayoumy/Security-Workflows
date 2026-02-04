---
title: "Empty Password"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
weight: 200
---
check all the accounts that need to be worked on using the following PowerShell command: 
```powershell
get-adobject -ldapfilter "(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=32))" -properties useraccountcontrol 
```

change `useraccountcontrol` value to `512` which is the default value

!Pasted image 20250522141655.png (TODO: link: Pasted image 20250522141655.png)

pass not req:

!Pasted image 20250522141731.png (TODO: link: Pasted image 20250522141731.png)
