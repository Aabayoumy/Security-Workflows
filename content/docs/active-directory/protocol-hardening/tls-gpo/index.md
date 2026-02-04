---
title: "TLS GPO"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
weight: 200
tags: ["TLS"]
---
[TLS]({{< relref "docs/active-directory/protocol-hardening/tls" >}})

```powershell
$GPO = "Disable-TLS1.0&1.1_Enable-TLS1.2"
    New-GPO -Name $GPO -Comment "Link it to Doamin Controllers OU"
    # Disable TLS1.0
        Set-GPRegistryValue -Name $GPO -Key "HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.0\Client" -ValueName "Enabled" -Type Dword -Value 0
        Set-GPRegistryValue -Name $GPO -Key "HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.0\Client" -ValueName "DisabledByDefault" -Type Dword -Value 1
    # Disable TLS1.1
        Set-GPRegistryValue -Name $GPO -Key "HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.1\Client" -ValueName "Enabled" -Type Dword -Value 0
        Set-GPRegistryValue -Name $GPO -Key "HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.1\Client" -ValueName "DisabledByDefault" -Type Dword -Value 1
    # Enable TLS1.1
        Set-GPRegistryValue -Name $GPO -Key "HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.2\Client" -ValueName "Enabled" -Type Dword -Value 1
        Set-GPRegistryValue -Name $GPO -Key "HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.2\Client" -ValueName "DisabledByDefault" -Type Dword -Value 0

write-Host "Dont forget to link new GPO Disable-TLS1.0&1.1_Enable-TLS1.2 to Doamin Controllers OU"

```


SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.0\Client
Enabled   0
DisabledByDefault   1

SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.0\Server
Enabled   0
DisabledByDefault   1


SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.1\Client
Enabled   0
DisabledByDefault   1

SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.1\Server
Enabled   0
DisabledByDefault   1



SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.2\Client
Enabled   1
DisabledByDefault   0

SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.2\Server
Enabled   1
DisabledByDefault   0
