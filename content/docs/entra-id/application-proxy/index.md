---
title: "Microsoft Entra ID Application Proxy"
date: 2026-02-18T10:00:00
authors: ["opencode"]
tags: ["entraid", "appproxy", "security", "hybrid"]
draft: false
---

# 🛡️ Microsoft Entra ID Application Proxy

Microsoft Entra ID Application Proxy provides secure remote access to on-premises web applications. After a single sign-on to Entra ID, users can access both cloud and on-premises applications through an external URL or an internal client portal.

## 🏗️ How it Works (Architecture)

Unlike traditional VPNs or DMZ implementations, Application Proxy does **not** require opening any inbound ports in your firewall. 

1.  **Connector:** A lightweight service (Connector) is installed on a Windows Server on-premises.
2.  **Outbound Connection:** The Connector establishes an outbound persistent connection to the Entra ID service in the cloud.
3.  **Request Flow:** When a user accesses the app via the external URL, Entra ID authenticates the user and passes the request through the secure outbound tunnel to the Connector, which then forwards it to the internal application.

---

## 🔍 Is your App SSO Compatible?

Not all applications support Single Sign-On (SSO) automatically. Use the guide below to identify the authentication method of your internal application and determine the best SSO strategy.

### How to Identify the App's Auth Method:
1.  **Check the Login Page:** If it’s a browser-native popup (Basic/NTLM), it likely uses **IWA**.
2.  **Check the Form:** If it's a web page with username/password fields, it's **Form-based**.
3.  **Check Documentation:** Look for mention of Headers, SAML, or Kerberos.

### SSO Selection Matrix

| Internal Auth Method | App Proxy SSO Mode | Requirement |
| :--- | :--- | :--- |
| **Integrated Windows Auth (IWA)** | Kerberos Constrained Delegation (KCD) | Service Principal Name (SPN) in AD |
| **Header-based** | Header-based SSO | Requires Entra ID P1/P2 |
| **Forms-based** | Password-based SSO | User credentials stored in Entra ID |
| **SAML / OAuth** | Entra ID (Native) | App must be configured as a Gallery/Non-Gallery app |
| **No SSO Support** | **Passthrough** | Users will be prompted to login twice (Entra ID + App) |

---

## 🚀 Implementation Steps

### 1. Install the Connector
- Download the **Microsoft Entra Private Network Connector** from the Entra admin center.
- Install it on a Windows Server 2012 R2 or later.
- **Firewall:** Ensure outbound access to `*.msappproxy.net` on ports 80 and 443.

### 2. Configure the Application in Entra ID
- Go to **Enterprise Applications** -> **New application** -> **Add an on-premises application**.
- **Internal URL:** The URL used to access the app inside the network (e.g., `http://hr-portal/`).
- **External URL:** The URL users will use from the internet (e.g., `https://hr-portal-tenant.msappproxy.net/`).
- **Pre-authentication:** Select **Microsoft Entra ID** (Recommended for security).

### 3. Assign Users and Policies
- Assign the specific users or groups who need access.
- **Conditional Access:** Since the app is now managed by Entra ID, you can (and should) require **MFA** and **Compliant Devices** for access.

---

## ⚠️ App Proxy vs. Private Access
This guide focuses on **Application Proxy**, which is designed specifically for **HTTP/HTTPS** web applications. For non-web traffic (RDP, SSH, SMB), consider **Microsoft Entra Private Access**, which uses a different ZTNA (Zero Trust Network Access) architecture.

---

## 🛠️ Troubleshooting
- **Connector Status:** Check the "Application Proxy" blade in the portal to ensure the connector is "Active".
- **Internal DNS:** Ensure the server hosting the Connector can resolve the Internal URL.
- **KCD Errors:** Verify the SPN is correctly set on the service account running the internal app.
