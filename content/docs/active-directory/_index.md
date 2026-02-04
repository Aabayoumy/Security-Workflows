---
title: "Active Directory Hardening"
bookCollapseSection: false
weight: 10
authors: ["ahmed"]
---

# 🏗️ Active Directory Hardening

Active Directory remains the primary identity store for most enterprises. Securing it requires a multi-layered approach focusing on identity isolation, protocol hardening, and continuous monitoring.

### 🎯 Key Focus Areas

{{< columns >}}
**Protocol Hardening**
- [Kerberos Armoring]({{< relref "kerberos-armoring" >}})
- [RC4 Audit & CVE-2022-37967]({{< relref "kerberos_rc4_audit_cve-2026-20833" >}})
- Disabling LLMNR/NBT-NS

<--->

**Access Control**
- [Enterprise Access Model (Tiered Admin)]({{< relref "tiered-administration" >}})
- Protected Users Group
- PAM (Privileged Access Management)
{{< /columns >}}

## Start Here

- [Hardening Implementation Plan]({{< relref "hardening-implementation-plan" >}})

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
