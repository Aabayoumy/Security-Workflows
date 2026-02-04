---
title: "Test LDAP event 2889"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
weight: 200
tags: ["LDAP"]
---
Use LDP to connect to the DC on port 389 (LDAP, not 636 for LDAPS) and perform a simple bind. This should trigger an insecure bind, and event 2889 should now appear in the Directory Service log.

![20250512174158.png](20250512174158.png)

![20250512174219.png](20250512174219.png)

![20250512174231.png](20250512174231.png)

![20250512174300.png](20250512174300.png)
