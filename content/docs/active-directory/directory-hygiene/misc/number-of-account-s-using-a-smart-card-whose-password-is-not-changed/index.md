---
title: "Number of account(s) using a smart card whose password is not changed"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
weight: 200
---
| Name   | Creation             | Last logon           | Pwd Last Set | Distinguished name                       |
| ------ | -------------------- | -------------------- | ------------ | ---------------------------------------- |
| Admin1 | 2024-08-18 09:51:19Z | 2024-09-05 10:38:54Z | Never        | CN=Admin1,CN=Users,DC=bojdomain,DC=local |
The purpose is to make sure the requirement of Smart Cards doesn't degrade password rotation

**Technical explanation:**

Using smart cards to protected sensitive accounts is a good thing. Nevertheless, when the "Smart Card required" flag is set, the password of the account is not changed anymore by default. The rule is triggered 90 days after the last change of the attribute unicodePwd. This value is collected using the replication metadata of the attribute 589914

**Advised solution:**

There are a few solutions to fix this issue, the most obvious being to change the user password on a regular basis.  

Another possibility, instead of changing the password, is to disable the flag "this account requires a smart card" then re-enable it, which will trigger an internal password hash change.

[Security Focus: Resetting 'Smart card is required for interactive logon' | Microsoft Learn](https://learn.microsoft.com/en-us/archive/blogs/poshchap/security-focus-resetting-smart-card-is-required-for-interactive-logon)
