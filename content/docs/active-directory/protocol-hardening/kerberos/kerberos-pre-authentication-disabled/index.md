---
title: "Kerberos pre-authentication disabled"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
weight: 200
---
Some accounts have Kerberos preauthentication disabled. Without preauthentication, it is possible to acquire a ticket encrypted with one of the Kerberos keys associated with the requested account. It is then possible to carry out a brute force or dictionary guessing attack to crack an account password if it is not strong enough. 

Kerberos pre-authentication ensures that users requesting a Ticket Granting Ticket (TGT) know a given authentication secret. By default, all user accounts require pre-authentication because their `DONT_REQUIRE_PREAUTH` property is not set. That property was designed for backward compatibility with older Kerberos implementations. 

General Case:
The `DONT_REQUIRE_PREAUTH` property must be removed from these accounts. If an application is not compatible with this change, it must be upgraded. 
Specific Cases:
Any incompatible software must be upgraded. This issue can be mitigated as follows:
- defining a refined password policy through Password Settings Objects (PSO), enforcing a minimum password length of 32 characters.
- defining a refined password policy through Password Settings Objects (PSO), enforcing a maximum expiration duration of 3 years.
- changing the affected user passwords after modifying the PSO settings;
- enforcing AES usage for the affected account.

**Advised solution:**

Edit the property of the involved accounts and select the Account tab. Uncheck "Do not require Kerberos preauthentication". For computers, which don't have the Account tab, you have to manually edit the attribute useraccountcontrol. Subtract 4194304 the value of the attribute.

**Points:**

[Active Directory Security Assessment Checklist](https://www.cert.ssi.gouv.fr/uploads/ad_checklist.html#vuln_kerberos_properties_preauth)
