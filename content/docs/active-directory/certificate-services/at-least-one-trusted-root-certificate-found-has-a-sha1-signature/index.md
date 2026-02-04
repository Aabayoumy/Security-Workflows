---
title: "At least one trusted ROOT certificate found has a SHA1 signature"
date: 2026-02-03T08:51:11
draft: false
authors: ["ahmed"]
weight: 200
---
The purpose is to ensure that no Root Certificates use the deprecated SHA-1 hashing algorithm

**Technical explanation:**

The SHA1 hashing algorithm is not considered as safe. There are design flaws inherent to the algorithm that allow an attacker to generate a hash collision in less than a brute-force time

**Advised solution:**

To solve the matter, the certificate should be removed from the GPO and if needed, certificates depending on it should be reissued.
