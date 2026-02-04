---
title: "TLS"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
weight: 200
tags: ["tls"]
---
[TLS GPO]({{< relref "docs/active-directory/protocol-hardening/tls-gpo" >}})
# TLS Registry Configuration for Group Policy

## Overview
Group Policy can be configured to disable TLS 1.0 and 1.1 while enabling TLS 1.2 through **registry settings** that should be applied to **all computers** in the domain, not just domain controllers.

## Registry Configuration

### Base Registry Path
```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols
```

### Required Registry Keys

| TLS Version | Component | Registry Path                                                                          | Settings                                                         |
| ----------- | --------- | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| **TLS 1.0** | Client    | `SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.0\Client` | `Enabled = 0` (REG_DWORD)<br>`DisabledByDefault = 1` (REG_DWORD) |
| **TLS 1.0** | Server    | `SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.0\Server` | `Enabled = 0` (REG_DWORD)<br>`DisabledByDefault = 1` (REG_DWORD) |
| **TLS 1.1** | Client    | `SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.1\Client` | `Enabled = 0` (REG_DWORD)<br>`DisabledByDefault = 1` (REG_DWORD) |
| **TLS 1.1** | Server    | `SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.1\Server` | `Enabled = 0` (REG_DWORD)<br>`DisabledByDefault = 1` (REG_DWORD) |
| **TLS 1.2** | Client    | `SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.2\Client` | `Enabled = 1` (REG_DWORD)<br>`DisabledByDefault = 0` (REG_DWORD) |
| **TLS 1.2** | Server    | `SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.2\Server` | `Enabled = 1` (REG_DWORD)<br>`DisabledByDefault = 0` (REG_DWORD) |

## Client vs Server Registry Keys

The registry structure includes separate **Client** and **Server** subkeys because:

- **Server keys** → Control TLS behavior when the machine **receives** connections
- **Client keys** → Control TLS behavior when the machine **makes** connections to other systems

> **Note:** Both are needed because computers often function as both clients and servers in different scenarios.

## GPO Linking Strategy

### ✅ Recommended: Link to Domain Level
- **All computers** need TLS configuration (workstations, servers, domain controllers)
- Ensures consistent TLS settings across all machines
- Domain controllers are just one type of computer that needs secure TLS configuration

### ❌ Not Recommended: Domain Controllers OU Only
- Would only apply TLS settings to domain controllers
- Leaves workstations and member servers with default (potentially insecure) TLS settings
- Creates inconsistent security posture across the environment

## Implementation Steps

1. **Create GPO** with registry preferences
2. Navigate to: `Computer Configuration → Preferences → Windows Settings → Registry`
3. Create registry items for all the TLS keys mentioned above
4. **Link GPO to the domain level** for organization-wide application
5. **Restart systems** after GPO application for changes to take effect

## Important Considerations

- ⚠️ **Test thoroughly** before production deployment as legacy applications may rely on older TLS versions
- 🔄 **System restart required** for TLS registry changes to take effect
- 🔧 Consider creating separate GPOs for different server versions if running mixed environments
- 🔗 The settings affect both **incoming and outgoing** TLS connections due to the Client/Server key structure

## Summary

The TLS registry configuration should be applied to **all computers** in the domain through domain-level GPO linking, ensuring consistent security standards across your entire Active Directory environment.

## Sources

https://support.microsoft.com/en-us/topic/kb5017811-manage-transport-layer-security-tls-1-0-and-1-1-after-default-behavior-change-on-september-20-2022-e95b1b47-9c7c-4d64-9baf-610604a64c3e


-------------------------
