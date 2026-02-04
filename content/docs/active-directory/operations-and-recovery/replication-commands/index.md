---
title: "Replication commands"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
tags: ["replication"]
---

To replicate and check the summary of **Active Directory replication**, you can use **Repadmin**, **Dcdiag**, and PowerShell.
##### Force Replication
Use **Repadmin** to manually trigger replication:
```powershell
repadmin /syncall /AdeP
```
- `/A` – Replicates all partitions.
- `/d` – Displays detailed output.
- `/e` – Replicates across all domain controllers.
- `/P` – Pushes changes outward.

##### Check Replication Summary
Run this command to get a **quick overview** of replication health:
```powershell
repadmin /replsummary
```
This will show:
- **Largest replication delay** between domain controllers.
- **Failures and success rates** for inbound/outbound replication.

##### Verify Replication Status
Check replication details per domain controller:
```powershell
repadmin /showrepl
```
This displays:
- **Last successful replication** timestamps.
- **Errors or delays** in replication.

##### Use Dcdiag for Health Checks
Run a **diagnostic test** on replication:
```powershell
dcdiag /test:replications
```
This will highlight:
- **Replication failures**.
- **Connectivity issues** between domain controllers.

##### PowerShell Alternative
For a **PowerShell-based** check:
```powershell
Get-ADReplicationFailure -Server DC01
```
This lists replication failures for **DC01**.

For more details, check out [this guide](https://activedirectorypro.com/repadmin-how-to-check-active-directory-replication/) on **Active Directory replication troubleshooting**.
