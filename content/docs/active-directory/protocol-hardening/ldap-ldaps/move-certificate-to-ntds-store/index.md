---
title: "Move Certificate to NTDS Store"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
tags: ["LDAPS"]
---

## Move Certificate to NTDS Store (DOMAIN CONTROLLER)

**Server Location**: Each Domain Controller

1. **Export Certificate from Local Machine Store**
    
    - In Certificates MMC, navigate to **Personal** → **Certificates**
        
    - Find your LDAPS certificate
        
    - Right-click → **All Tasks** → **Export**
        
    - Export with private key as .PFX file[](https://www.sectigo.com/resource-library/install-certificates-microsoft-active-directory-ldap-2008)
        
    - Set strong password
        
2. **Import to NTDS Store**
    
    - In same MMC, add another Certificates snap-in
        
    - Choose **Service account** → **Active Directory Domain Services**[](https://mobile2.managed.entrust.com/csp/1.1.0/Installing-the-Active-Directory-server-certificate.html)
        
    - Navigate to **Certificates - Service (Active Directory Domain Services)** → **NTDS** → **Personal**
        
    - Right-click **Certificates** → **All Tasks** → **Import**[](https://www.sectigo.com/resource-library/install-certificates-microsoft-active-directory-ldap-2008)
        
    - Import the .PFX file
        
3. **Restart NTDS Service**
 ```powershell
    net stop ntds 
    net start ntds
    ```
