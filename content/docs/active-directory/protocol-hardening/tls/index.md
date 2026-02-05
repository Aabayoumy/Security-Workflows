---
title: "TLS"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
weight: 200
tags: ["tls"]
---
This topic is consolidated into the Active Directory-focused guide:

- [Disable TLS 1.0/1.1 and enforce TLS 1.2 (Active Directory)]({{< relref "docs/active-directory/directory-hygiene/misc/disable-tls-1-0-1-1-force-tls-1-2" >}})

That guide includes:

- audit workflow (what is negotiated today)
- Schannel EventLogging (audit-first)
- GPO registry settings (Client + Server)
- verification commands (LDAPS/StartTLS/3269)
- rollback plan

Sources:

https://learn.microsoft.com/en-us/windows-server/security/tls/tls-registry-settings
