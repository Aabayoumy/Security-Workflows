---
title: "Active Directory Hardening"
weight: 10
bookCollapseSection: false
authors: ["ahmed"]
---

This is the original action plan, sorted by execution order.

## Defaults & Misconfigurations

- [AD Assessment]({{< relref "baseline-and-audit/ad-assessment" >}})
- [Export inactive users and computers & users with never-expire passwords]({{< relref "baseline-and-audit/account-hygiene-exports" >}})
- [Export non-supported OS]({{< relref "baseline-and-audit/export-unsupported-os" >}})
- [Certificate misconfigurations]({{< relref "certificate-services" >}})
- [Vulnerabilities & Mitigations]({{< relref "vulnerabilities-and-mitigations" >}})
- [Domain Controllers]({{< relref "domain-controllers" >}})

## Secure Default Protocols

- [Audit & Disable NTLM]({{< relref "protocol-hardening/audit-disable-ntlm" >}})
- [Audit LDAP & Enable LDAPS settings]({{< relref "protocol-hardening/ldap-ldaps/audit-ldap-enable-ldaps-settings" >}})
- [Audit SMBv1]({{< relref "protocol-hardening/audit-smbv1" >}})
- [DNS]({{< relref "protocol-hardening/dns" >}})
- [Protocol Hardening]({{< relref "protocol-hardening" >}})

## Actions To Enhance Security

- [Baseline DCs, servers & workstations]({{< relref "baseline-and-audit/baseline" >}})
- [Windows LAPS]({{< relref "directory-hygiene/laps/windows-laps" >}})
- [Tiering]({{< relref "tiered-administration" >}})
- [Privileged Access]({{< relref "privileged-access" >}})
- [Kerberos Armoring]({{< relref "kerberos-armoring" >}})
- [Kerberoasting]({{< relref "directory-hygiene/misc/kerberoasting" >}})
- [Reset KRBTGT password]({{< relref "operations-and-recovery/reset-krbtgt-password" >}})
- [Operations & Recovery]({{< relref "operations-and-recovery" >}})
- [Directory Hygiene]({{< relref "directory-hygiene" >}})
- [Applications & Services]({{< relref "applications-and-services" >}})

---
