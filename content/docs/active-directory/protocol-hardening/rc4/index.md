---
title: "RC4"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
weight: 200
tags: ["kerberoasting", "rc4"]
---
Key Features
The script identifies Computers that support RC4 encryption through several methods:
	•	Explicit RC4 configuration: Objects with `msDS-SupportedEncryptionTypes` attribute containing the RC4 flag (0x4)
	•	DES-only flag: Objects with userAccountControl flag 0x200000 (which defaults to RC4)
	•	Default behavior: Computers without explicit encryption types (RC4 is used by default)
Important Notes
	•	Security Risk: RC4 encryption is considered weak and vulnerable to attacks like Kerberoasting
	•	Bitwise Operations: The script uses bitwise operations to check encryption type flags
	•	Default Behavior: When `msDS-SupportedEncryptionTypes` is not set, RC4 is used by default
	•	Migration Planning: Use this export to plan migration from RC4 to AES encryption
	

```powershell 
Import-Module ActiveDirectory; 

(Get-ADComputer -Filter 'msDS-SupportedEncryptionTypes -band 0x1 -or msDS-SupportedEncryptionTypes -band 0x2 -or msDS-SupportedEncryptionTypes -band 0x4 -or userAccountControl -band 0x200000' -Properties Name,SamAccountName,msDS-SupportedEncryptionTypes,ServicePrincipalName | Select @{N='Type';E={'Computer'}},Name,SamAccountName,msDS-SupportedEncryptionTypes,ServicePrincipalName) | 
Export-Csv ".\WeakEncryption_Export.csv" -NoTypeInformation
```
