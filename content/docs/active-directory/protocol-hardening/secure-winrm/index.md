---
title: "Secure WinRM"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
tags: ["Winrm"]
---

## Introduction
Windows Remote Management (WinRM) is a powerful tool for managing Windows servers remotely, but by default, it uses unencrypted communication. For a secure environment, it's crucial to configure WinRM to use HTTPS. This post will guide you through securing WinRM using a custom certificate template and Group Policy in an Active Directory environment.
## Step 1: Create a Custom Certificate Template
First, we need a certificate template for our WinRM servers.
1. **Open the Certificate Authority Console:** On your CA server, open the `certsrv.msc` console.
2. **Manage Templates:** Right-click on **Certificate Templates** and select **Manage**.
3. **Duplicate Template:** Right-click the **Computer** template and select **Duplicate Template**.
4. **Configure Template Properties:**
	* **General Tab:** Give the template a descriptive name like `WinRM SSL` and set a validity period that aligns with your security policies.
	* **Subject Name Tab:** Select **Build from this Active Directory information** and choose `DNS name` for the subject name format.
	* **Cryptography Tab:** Ensure the key size is adequate (e.g., `2048` bits or higher).
	* **Extensions Tab:**
	* Select **Application Policies** and click **Edit**.
	* Remove **Client Authentication** and ensure **Server Authentication** is present.
	* **Security Tab:**
	* Add the **Domain Computers** group and grant them **Read**, **Enroll** and **Auto Enroll** permissions.
5. **Issue the Template:**
	* Back in the Certificate Authority console, right-click **Certificate Templates**, go to **New**, and select **Certificate Template to Issue**.
	* Choose the `WinRM SSL` template you just created.

## Step 2: Configure Certificate Auto-Enrollment via Group Policy
Now, let's configure our domain computers to automatically request and renew this certificate.
 
1. **Open Group Policy Management:** Open `gpmc.msc`.
2. **Create or Edit a GPO:** Create a new GPO or edit an existing one that is linked to the Organizational Unit (OU) containing the computers you want to configure.
3. **Configure Auto-Enrollment:**
	* Navigate to `Computer Configuration -> Policies -> Windows Settings -> Security Settings -> Public Key Policies`.
	* Double-click on **Certificate Services Client - Auto-Enrollment**.
	* Set the **Configuration Model** to **Enabled**.
	* Check the boxes for `Renew expired certificates...` and `Update certificates that use certificate templates`.

## Step 3: Configure WinRM and Firewall using Group Policy
The final step is to configure the WinRM listener and firewall settings on each machine. We will use Group Policy to run commands and set firewall rules.
1. **Configure WinRM Listeners via Scheduled Tasks:** In your GPO, navigate to `Computer Configuration -> Preferences -> Control Panel Settings -> Scheduled Tasks`. Create new **Immediate Task (At least Windows 7)** task with 3 Actions to ensure WinRM is configured correctly.
	* **Task 1: Quick-configure WinRM for HTTPS**
		* **Name:** `WinRM Quick-Config HTTPS`
		* **Program/script:** `C:\Windows\System32\winrm.cmd`
		* **Arguments:** `quickconfig -transport:https -quiet`
	* **Task 2: Ensure HTTPS Listener Exists**
		* **Name:** `WinRM Create HTTPS Listener`
		* **Program/script:** `C:\Windows\System32\winrm.cmd`	
		* **Arguments:** `create winrm/config/Listener?Address=*+Transport=HTTPS`		
	* **Task 3: Remove the Insecure HTTP Listener**	
		* **Name:** `WinRM Delete HTTP Listener`	
		* **Program/script:** `C:\Windows\System32\winrm.cmd`	
		* **Arguments:** `delete winrm/config/Listener?Address=*+Transport=HTTP`  

2. **Configure Firewall Rules:** In the same GPO, navigate to `Computer Configuration -> Policies -> Windows Settings -> Security Settings -> Windows Firewall with Advanced Security -> Inbound Rules`. 
	* **Allow WinRM HTTPS (Port 5986):**
		* Right-click **Inbound Rules** and select **New Rule...**.	
		* Select **Port**, click **Next**.	
		* Select **TCP** and specify port `5986`. Click **Next**.	
		* Select **Allow the connection**. Click **Next**.	
		* Choose the profiles (Domain, Private, Public) that match your security policy. Click **Next**.	
		* Give the rule a name, like `Allow WinRM HTTPS (5986)`. Click **Finish**.  

	* **Block WinRM HTTP (Port 5985):**
		* Create another new rule.
		* Select **Port**, click **Next**.
		* Select **TCP** and specify port `5985`. Click **Next**.
		* Select **Block the connection**. Click **Next**.
		* Choose the profiles that match your security policy. Click **Next**.
		* Give the rule a name, like `Block WinRM HTTP (5985)`. Click **Finish**.  

3. **Enable WinRM Service:**
	* In the same GPO, navigate to `Computer Configuration -> Policies -> Administrative Templates -> Windows Components -> Windows Remote Management (WinRM) -> WinRM Service`.
	* Enable the **Allow remote server management through WinRM** policy. For enhanced security, you can specify IP address ranges in the IPv4 and IPv6 filters instead of using `*`.
## Conclusion
After applying the GPO, your computers will automatically enroll for the WinRM certificate and configure a secure HTTPS listener. This significantly improves the security of your remote management infrastructure. Remember to test the connection using `Test-WSMan` from another machine, ensuring you use the `-UseSSL` switch.

  
> Disclaimer: This post was created with the assistance of Google's Gemini.
