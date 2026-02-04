---
title: "AD Assessment"
draft: false
authors: ["ahmed"]
weight: 10
---

Starter checklist to assess Active Directory security posture before enforcing changes.

## Collect

- AD inventory (domains/forests, trusts, sites/subnets, DC list).
- GPO inventory + reports (domain + DC OU + key server/workstation OUs).
- Auth telemetry: NTLM, LDAP simple binds/unsigned, SMBv1, RC4 usage.
- Privileged group membership + delegation review.
- Backup/restore readiness (system state + authoritative restore runbook).

## Outputs

- Findings + risk-ranked remediation backlog.
- Compatibility list (apps/clients that will break under enforcement).
