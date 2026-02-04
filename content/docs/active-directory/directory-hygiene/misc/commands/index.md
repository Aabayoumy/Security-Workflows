---
title: "Commands"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
---

repadmin /syncall /force /ADdPe
dcdiag
`nltest /dsgetdc:domainname`
This command will return the domain controller information for the specified domain
`repadmin /showobjmeta <dc> <distinguished name>`
This command helps you understand the history of changes to an object's attributes, which can be useful for troubleshooting replication problems. 

`Get-ADObject -Filter {UserAccountControl -band 0x200000 -or msDs-supportedEncryptionTypes -band 3}`
get VMs using weak encryption

`Get-ADServiceAccount -Identity <account> -Properties *`
This command will output all available details about the specified service account.

`icm -ComputerName dc1,dc2 -ScriptBlock {cpmmand}`
to run command to DCs using PowerShell remoting 

Repadmin /syncall /force /APed             
repadmin /showrepl *   /csv > c:\showrepl.csv       
Import-Csv c:\showrepl.csv | ogv
