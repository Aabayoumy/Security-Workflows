---
title: "Active Directory Hardening"
bookCollapseSection: false
weight: 10
authors: ["ahmed"]
---

This is the practical rollout plan to harden Active Directory in phases (audit -> enforce), with verification steps and rollback notes.

## Phase 0 - Foundations

- Confirm backups, break-glass access, and a tested restore path.
- Capture baseline: GPO reports, DC health, authentication usage, and protocol telemetry.

## Phase 1 - Privileged Access

- [Privileged Access]({{< relref "privileged-access" >}})

## Phase 2 - Protocol Hardening

- [Protocol Hardening]({{< relref "protocol-hardening" >}})

## Phase 3 - Domain Controller Hardening

- [Domain Controllers]({{< relref "domain-controllers" >}})

## Phase 4 - Directory Hygiene

- [Directory Hygiene]({{< relref "directory-hygiene" >}})

## Phase 5 - PKI / AD CS

- [Certificate Services]({{< relref "certificate-services" >}})

## References

- [Microsoft security baseline for Windows / AD](https://learn.microsoft.com/)

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
