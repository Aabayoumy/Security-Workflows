---
title: "DC misconfigured privilege access"
date: 2026-02-03T08:51:11
draft: false
authors: ["ahmed"]
weight: 200
tags: ["DC", "gpo"]
---
|GPO|Account|Privilege|
|---|---|---|
|Default Domain Controllers Policy|Authenticated Users|SeRemoteInteractiveLogonRight|

!Pasted image 20250522114240.png (TODO: link: Pasted image 20250522114240.png)

Locate the GPO specified in Details and remove the privilege "Allow log on locally" or "Allow log on through Remote Desktop Services" to "Everyone", "Authenticated Users", "Domain Users" or "Domain Computers".  


The settings are located in :  
Computer configuration -> Policies -> Windows Settings ->Security Settings -> Local Policies -> User Rights Assignment.  
As an alternative, the file GptTmpl.inf can be manually edited.


| GPO                               | Account             | Privilege                     |
| --------------------------------- | ------------------- | ----------------------------- |
| Default Domain Controllers Policy | Authenticated Users | SeAssignPrimaryTokenPrivilege |
| Default Domain Controllers Policy | Authenticated Users | SeTcbPrivilege                |

!Pasted image 20250522140649.png (TODO: link: Pasted image 20250522140649.png)

!Pasted image 20250522114741.png (TODO: link: Pasted image 20250522114741.png)

SeTcbPrivilege is the privilege used to "Act on behalf the operating system". This is the privilege reserved to the SYSTEM user. This procedure allows any user to act as SYSTEM.


SeAssignPrimaryTokenPrivilege is a powerful privilege that allows attackers abuse it to make a lower-privileged process act like it's running with administrator or SYSTEM-level permissions.

Locate the GPO specified in Details and remove the privilege.  
Most of the settings are located in :  
Computer configuration -> Policies -> Windows Settings ->Security Settings -> Local Policies -> User Rights Assignment.  
As an alternative, the file GptTmpl.inf can be manually edited.
