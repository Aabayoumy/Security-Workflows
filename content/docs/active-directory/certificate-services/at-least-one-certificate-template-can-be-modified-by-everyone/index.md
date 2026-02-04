---
title: "At least one certificate template can be modified by everyone"
date: 2026-02-03T08:51:11
draft: false
authors: ["ahmed"]
weight: 200
---
| Name                |
| ------------------- |
| Machine             |
| EFS                 |
| RemoteDesktopSecure |
| RDPSecure           |



![20250123093654.png](20250123093654.png)

The purpose of this rule is to ensure that there is no certificate template that can be edited by anyone.

**Advised solution:**
Review the security permissions of this certificate template and remove the write access to everyone-like groups such as Domain Users, Domain Computers, Everyone, Authenticated Users.

1. Open `Certificate Authority` and Navigate to `Certificate Templates` and click `Manage`
2. locate the vuln template then  `Properties > Security` and remove unneeded permission 

![20250122163008.png](20250122163008.png)
