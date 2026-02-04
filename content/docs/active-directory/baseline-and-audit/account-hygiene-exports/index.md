---
title: "Account Hygiene Exports"
draft: false
authors: ["ahmed"]
weight: 50
---

Exports used early in the hardening plan to identify high-risk accounts/computers.

## Inactive users and computers

```powershell
# Users inactive for 90 days
Search-ADAccount -AccountInactive -UsersOnly -TimeSpan 90.00:00:00 |
  Select-Object Name, SamAccountName, Enabled, LastLogonDate |
  Export-Csv .\inactive-users.csv -NoTypeInformation

# Computers inactive for 90 days
Search-ADAccount -AccountInactive -ComputersOnly -TimeSpan 90.00:00:00 |
  Select-Object Name, Enabled, LastLogonDate |
  Export-Csv .\inactive-computers.csv -NoTypeInformation
```

## Users with passwords that never expire

```powershell
Get-ADUser -LDAPFilter "(userAccountControl:1.2.840.113556.1.4.803:=65536)" -Properties PasswordNeverExpires |
  Select-Object Name, SamAccountName, Enabled, PasswordNeverExpires |
  Export-Csv .\password-never-expires.csv -NoTypeInformation
```
