---
title: "Check if DNS zones are configured with zone transfers"
date: 2026-02-03T08:51:11
draft: false
authors: ["ahmed"]
---

| Zone            |
| --------------- |
| bojdomain.local |





**Steps:**
Go to the DNS console and select a zone in the "Forward Lookup Zones".  
Right click on it and switch to the "Zone Transfers" tab.  
Then ensure "Allow zone transfers" is not enabled "To any server".  
You can also run: dnscmd /zoneresetsecondaries zone /noxfr

![20250109143602.png](20250109143602.png)
