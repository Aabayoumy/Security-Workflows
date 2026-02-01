---
title: "Enterprise Access Model (Tiered Admin)"
date: 2026-02-01
author: "Ahmed Bayoumy"
tags: ["Security", "Active Directory", "Privileged Access"]
weight: 30
---

# 🏰 Enterprise Access Model (Tiered Admin)

The **Enterprise Access Model** (formerly known as the "Tier Model") is the standard for securing administrative access to Active Directory. It prevents the escalation of privileges by ensuring that high-privilege credentials (like Domain Admins) are never exposed on lower-trust systems (like standard workstations).

## 🏢 The Three Tiers

| Tier | Description | Systems | Accounts |
| :--- | :--- | :--- | :--- |
| **Tier 0** | Direct Control of the Forest | Domain Controllers, PKI, ADFS, Azure AD Connect | Domain Admins, Enterprise Admins |
| **Tier 1** | Enterprise Servers & Apps | Web Servers, SQL Servers, Exchange | Server Admins |
| **Tier 2** | End-User Devices | Windows Workstations, Laptops | Helpdesk, Local Admins |

## 🛡️ Enforcement via GPO

To enforce this model, you must use Group Policy to restrict where specific accounts can sign in.

### 1. "Allow Log on Locally" Restrictions
- **Tier 0 Admins:** Only allowed on Tier 0 systems.
- **Tier 1 Admins:** Only allowed on Tier 1 systems.

### 2. "Deny Log on through Remote Desktop Services"
- **Tier 0 Admins:** Denied on all Tier 1 and Tier 2 systems.
- **Tier 1 Admins:** Denied on Tier 2 systems.

## 🔑 Protected Users Group
For Tier 0 admins, membership in the **Protected Users** group provides automated hardening:
- Disables NTLM authentication.
- Disables DES/RC4 in Kerberos pre-authentication.
- Limits Kerberos TGT lifetime to 4 hours.

---
