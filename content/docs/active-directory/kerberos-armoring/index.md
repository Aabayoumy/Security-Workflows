---
title: "Kerberos Armoring"
date: 2026-01-30T21:47:18
draft: false
weight: 10
authors: ["ahmed"]
---

New GPO for **DCs** with this settings: (Link to DCs OU)

 **Configuring Armoring for the KDC:**
 Computer Configuration -> Policies -> Administrative Templates -> System -> KDC
 
![20250624175046.png](20250624175046.png)

![20250624180158.png](20250624180158.png)

Another new GPO for **Clients** with this setting: (Link to domain root)

**Configuring Armoring for the clients:**
Computer Configuration -> Policies -> Administrative Templates -> System -> Kerberos

![20250624180232.png](20250624180232.png)'
![20250624180201.png](20250624180201.png)

**Test:**
you need to `gpupdate` the logoff and login again

without armoring:

notice `Cashe Flags: 0`

![20250624180845.png](20250624180845.png)

with armoring:

![20250624181313.png](20250624181313.png)

**Resources:**
- [It’s Time to Deploy Kerberos Armoring (enowsoftware.com)](https://www.enowsoftware.com/solutions-engine/azure-active-directory-center/its-time-to-deploy-kerberos-armoring#:~:text=To%20enable%20Kerberos%20Armoring%20on%20all%20domain%20members%2C,Armoring.%205%20Expand%20the%20domain%20name.%20More%20items)
- [TrustedSec | I Wanna Go Fast, Really Fast, like (Kerberos) FAST](https://www.trustedsec.com/blog/i-wanna-go-fast-really-fast-like-kerberos-fast)
- [What's New in Kerberos Authentication | Microsoft Learn](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/hh831747\(v=ws.11\))
- [Securing The Chink in Kerberos’ Armor, FAST! Understanding The Need For Kerberos Armoring](https://www.hub.trimarcsecurity.com/post/securing-the-chink-in-kerberos-armor-fast-understanding-the-need-for-kerberos-armoring)
- [Kerberos FAST Armoring](https://syfuhs.net/kerberos-fast-armoring)