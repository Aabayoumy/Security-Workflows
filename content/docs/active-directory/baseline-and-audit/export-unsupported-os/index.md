---
title: "Export Unsupported OS"
draft: false
authors: ["ahmed"]
weight: 60
---

Export computers running unsupported operating systems (example: Windows 7/2008R2-era).

```powershell
Get-ADComputer -Filter * -Properties OperatingSystem, OperatingSystemVersion |
  Select-Object Name, OperatingSystem, OperatingSystemVersion |
  Export-Csv .\computers-os-inventory.csv -NoTypeInformation

# Example: filter older Windows (adjust to your environment)
Import-Csv .\computers-os-inventory.csv |
  Where-Object { $_.OperatingSystem -match 'Windows 7|2008|2003|XP' } |
  Export-Csv .\unsupported-os.csv -NoTypeInformation
```
