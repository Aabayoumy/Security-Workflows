---
title: "Required Conditional Access Policies"
date: 2026-02-01T06:05:00
authors: ["ahmed"]
tags: ["entraid", "ca", "Security"]
draft: false
---

Conditional Access (CA) is the "Zero Trust" engine of Entra ID. Below are the essential "Day 1" policies required to establish a secure identity perimeter.

## Important: Global Exclusions
For all policies below, ensure you exclude:
1. **Break-Glass Accounts:** Emergency "Cloud-only" accounts to prevent tenant lockout.
2. **Service Accounts:** Specifically for policies that may break non-interactive authentications.

---

## 1. Multi-Factor Authentication (MFA) Baselines

### Require MFA for All Users
The single most effective defense against credential theft.
- **Target:** All users.
- **Grant:** Require multi-factor authentication.
- **Reference:** [MFA for all users](https://learn.microsoft.com/en-us/entra/identity/conditional-access/howto-conditional-access-policy-all-users-mfa)

### Require MFA for Administrators
Privileged roles must be protected with the highest level of assurance.
- **Target:** Directory roles (Global Admin, Security Admin, etc.).
- **Grant:** Require multi-factor authentication.

### Require MFA for Guests
Ensure external collaborators meet your security standards before accessing data.
- **Target:** All guest and external users.

---

## 2. Attack Surface Reduction

### Identify Legacy Authentication Usage
Before blocking legacy authentication, it is crucial to identify which users or service accounts are currently using these protocols to avoid business disruption.
- **Path:** `Microsoft Entra ID -> Monitoring -> Sign-in logs`
- **Filter:** 
    1. Click **Add filters** and select **Client App**.
    2. Under the **Client App** filter, check all options under **Legacy Authentication Clients** (e.g., Authenticated SMTP, IMAP4, POP3, etc.).
    3. Review the list of users and applications to determine if they can be migrated to Modern Authentication or if they require a specific exclusion.

### Block Legacy Authentication
Legacy protocols (POP, IMAP, SMTP) do not support MFA and are the primary targets for password spraying.
- **Action:** Block access.
- **Client Apps:** Select "Legacy authentication clients".
- **Strategy:** Configure in **Audit Mode** first to identify legitimate SMTP service accounts.
- **Exclusions:** Service accounts using authenticated SMTP.

### Restrict Admin Portal Access
Ensure management interfaces are only accessible to those who need them.
- **Target Apps:** Microsoft Admin Portals and Windows Azure Service Management API.
- **Target Users:** All users (Exclude authorized Admins and Break-glass).
- **Grant:** Block access.

---

## 3. Location & Trust

### Geofencing (Egypt Only)
Restrict the login perimeter to known business locations.
- **Action:** Block access.
- **Locations:** Include "All locations" and exclude "Egypt" (configured via Named Locations).

### Secure Info Registration
Restrict where users can register their MFA and security information to prevent attackers from hijacking the setup process.
- **Target Action:** "Register security information".
- **Locations:** Restrict to trusted locations (e.g., Egypt or Corporate IP ranges).

---

## 4. Identity Protection (Risk-Based)
*Requires Entra ID P2 Licensing.*

### User Risk: Forced Password Reset
- **Condition:** User risk is **High**.
- **Grant:** Require password change.

### Sign-in Risk: MFA Challenge
- **Condition:** Sign-in risk is **Medium** or **High**.
- **Grant:** Require multi-factor authentication.
