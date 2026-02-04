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

---
