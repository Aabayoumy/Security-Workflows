---
title: "Active Directory Hardening"
weight: 10
bookCollapseSection: false
authors: ["ahmed"]
---

This is the original action plan, sorted by execution order.

## Execution Order

1. [AD Assessment]({{< relref "baseline-and-audit/ad-assessment" >}})
2. [Audit & Disable NTLM]({{< relref "protocol-hardening/audit-disable-ntlm" >}})
3. [Audit LDAP & Enable LDAPS settings]({{< relref "protocol-hardening/ldap-ldaps/audit-ldap-enable-ldaps-settings" >}})
4. [Audit SMBv1]({{< relref "protocol-hardening/audit-smbv1" >}})
5. [Export inactive users and computers & users with never-expire passwords]({{< relref "baseline-and-audit/account-hygiene-exports" >}})
6. [Export non-supported OS]({{< relref "baseline-and-audit/export-unsupported-os" >}})
7. [Windows LAPS]({{< relref "directory-hygiene/laps/windows-laps" >}})
8. [Kerberoasting]({{< relref "directory-hygiene/misc/kerberoasting" >}})
9. [Kerberos Armoring]({{< relref "kerberos-armoring" >}})
10. [Reset KRBTGT password]({{< relref "operations-and-recovery/reset-krbtgt-password" >}})
11. AzureAD SSO: [AzureADSSO reset (every 30 days)]({{< relref "docs/entra-id/azureadsso-reset" >}})
12. [Certificate misconfigurations]({{< relref "certificate-services" >}})
13. [Baseline DCs, servers & workstations]({{< relref "baseline-and-audit/baseline" >}})
14. [DNS]({{< relref "protocol-hardening/dns" >}})
15. [Tiering]({{< relref "tiered-administration" >}})

## Topics

- [Privileged Access]({{< relref "privileged-access" >}})
- [Baseline & Audit]({{< relref "baseline-and-audit" >}})
- [Protocol Hardening]({{< relref "protocol-hardening" >}})
- [Domain Controllers]({{< relref "domain-controllers" >}})
- [Directory Hygiene]({{< relref "directory-hygiene" >}})
- [Certificate Services]({{< relref "certificate-services" >}})
- [Operations & Recovery]({{< relref "operations-and-recovery" >}})
- [Applications & Services]({{< relref "applications-and-services" >}})
- [Vulnerabilities & Mitigations]({{< relref "vulnerabilities-and-mitigations" >}})

---
