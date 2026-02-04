---
title: "Enable Recycle Bin"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
---

To enable:
`Enable-ADOptionalFeature -Identity 'Recycle Bin Feature' -Scope ForestOrConfigurationSet -Target 'lab.local'`

to check:
1. `Get-ADOptionalFeature -Filter {name -like "Recycle Bin Feature"} | Select-Object Name, EnabledScopes`
