---
title: "Presence of delegation where anybody can act"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
weight: 200
---
| DN                                     | delegation          | right                                                                                       |
| -------------------------------------- | ------------------- | ------------------------------------------------------------------------------------------- |
| CN=Configuration,DC=bojdomain,DC=local | Authenticated Users | GenericAll, GenericWrite, WriteDacl, WriteOwner, All extended right, DSSelf, Write all prop |
The purpose is to verify that there is no delegation granted to "Everyone" or to "Authenticated Users"

**Technical explanation:**

To delegate control to a OU, access checks can be modified. In case of a misconfiguration, access can be granted to the group "Everyone" or "Authenticated Users".

**Advised solution:**

Review the delegation to remove this permission and if needed, set a more targeted group as recipient of the delegation.
