---
title: "At least one domain controller is not owned correctly"
date: 2026-02-03T08:51:11
draft: false
authors: ["ahmed"]
---

The purpose is to perform a review of which accounts have ownership rights on a domain controller and can then modify their permissions

**Technical explanation:**

By default, the "Domain Administrators" group or the "Enterprise Administrators" group are set as owners for "Domain Controllers". Nonetheless, in some cases (for instance when the server has been promoted from an existing server), the owner can be a non-admin person which joined the server to the domain. If this person has still rights over this account, it can be used to take ownership over the whole domain. A chain of compromising events can be designed to take control of the domain by including this account.

**Advised solution:**

To solve this security issue, you should change the ownership of the domain controller to match the "Domain Administrators" group.  
To control the ownership of domain controller objects, you can use the following PowerShell command:  
`Get-ADComputer -server my.domain.to.check -LDAPFilter "(&(objectCategory=computer)(|(primarygroupid=521)(primarygroupid=516)))" -properties name, ntsecuritydescriptor | select name,{$_.ntsecuritydescriptor.Owner}`.

First, locate the DC object then right click to select properties. Open the security tab and press the advanced button. You then have a new dialog with an owner tab. Select the owner and change it for the domain administrators group. You are done (no reboot needed).
