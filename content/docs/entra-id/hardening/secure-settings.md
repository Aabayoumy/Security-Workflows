---
title: "Security Hardening Settings"
date: 2026-02-01T06:00:00
authors: ["ahmed"]
tags: ["entraid", "Security"]
draft: false
---

This guide outlines critical configuration changes to harden a Microsoft Entra ID tenant against common attack vectors, following CIS and Microsoft security best practices.

## 1. Tenant Governance & Administration

### Restrict Access to Admin Portals
By default, standard users can access the Entra ID administration portal and browse directory data. This should be restricted.
- **Action:** Set **Restrict access to Microsoft Entra admin center** to **Yes**.
- **Path:** `Microsoft Entra ID -> Users -> User settings`
- **Reference:** [Microsoft Learn - Default user permissions](https://learn.microsoft.com/en-us/entra/identity/users/users-default-permissions)

### Restrict Tenant Creation
Prevent standard users from creating shadow IT environments by spinning up their own tenants.
- **Action:** Set **Restrict non-admin users from creating tenants** to **Yes**.
- **Path:** `Microsoft Entra ID -> Users -> User settings`

### Enable Directory Timeout
Enforce session hygiene for the Azure portal to prevent unauthorized access from unattended workstations.
- **Action:** Set directory-level idle timeout to **1 hour or less**.
- **Path:** `Azure portal -> Settings -> Directory + subscription -> Change the directory timeout setting`

## 2. User & Group Management

### Restrict Security Group Creation
Limit the ability to create security groups to administrators only to maintain directory structure integrity.
- **Action:** Set **Users can create security groups in Azure portals, API or PowerShell** to **No**.
- **Path:** `Microsoft Entra ID -> Groups -> General settings`

### Self-Service Password Reset (SSPR)
Enabling SSPR allows users to reset their passwords without helpdesk intervention, but it must be configured securely.
- **Configuration:** 
  - **Enablement:** Set to **All** or a specific **Selected** group.
  - **Methods:** Require at least **2 methods** (e.g., Microsoft Authenticator + Phone).
- **Path:** `Microsoft Entra ID -> Protection -> Password reset`

## 3. External Collaboration & App Security

### Guest Invite Restrictions
Limit who can invite external guests to your tenant to prevent unauthorized data sharing.
- **Action:** Set **Guest invite restrictions** to **Only users assigned to specific admin roles can invite guest users**.
- **Path:** `Microsoft Entra ID -> Users -> External collaboration settings`
- **Reference:** [CISA ScubaGear Msaad8.2v1](https://github.com/cisagov/ScubaGear/blob/main/PowerShell/ScubaGear/baselines/aad.md#msaad82v1)

### App Registration & Consent
Prevent users from registering their own applications or granting permissions to 3rd party apps (a common vector for consent phishing).
- **App Registration:** Set **Users can register applications** to **No**.
- **User Consent:** Set **User consent settings** to **Do not allow user consent** (Admin consent required for all apps).
- **Path:** `Microsoft Entra ID -> Enterprise applications -> User consent settings`

## 4. Monitoring & Branding

### Enable Unified Auditing
Entra ID activity must be recorded for forensic analysis and compliance.
- **Action:** Turn on auditing in the Microsoft Purview compliance portal.
- **Path:** `Purview -> Solutions -> Audit -> Start recording user and admin activity`
- **Reference:** [Microsoft Learn - Turn on auditing](https://learn.microsoft.com/en-us/purview/audit-log-enable-disable)

### Custom Branding
Apply MCIT-specific branding (logos and backgrounds) to help users distinguish your official sign-in page from phishing attempts.
- **Path:** `Microsoft Entra ID -> Company branding`
