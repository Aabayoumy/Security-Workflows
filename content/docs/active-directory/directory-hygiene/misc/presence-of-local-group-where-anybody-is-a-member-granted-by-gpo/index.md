---
title: "Presence of local group where anybody is a member granted by GPO"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
weight: 200
---
The purpose is to identify if there are local groups such as local administrators, terminal server access, where Authenticated Users or Everyone is being granted access by a GPO

**Technical explanation:**

It is possible that a GPO adds local membership using a GPO.  
In this case the rule triggers if one is found with "Everyone" or "Authenticated Users" or "Domain Users", ... as members.  
It basically means that the local Group has no restriction on belongs to it. This represents a security risk as Local Group are supposed to have more accesses or rights.  
The GPO configuration is located in Computer Configuration / Policies / Windows Settings / Security Settings / Restricted Group  
  
This rule checks also the membership set in Computer Configuration / Preferences / Control Panel Settings / Local Users and group.

**Advised solution:**

In order to correct the issue, you should edit the GPO and change the local group assignation. Another solution is to change the group to a more targeted one containing a limited set of users.
