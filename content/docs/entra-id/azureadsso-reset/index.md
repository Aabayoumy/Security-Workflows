---
title: "Azureadsso Reset"
date: 2026-01-30T21:57:14
draft: false
authors: ["ahmed"]
---

#trust #AZUREADSSO  #reset 

[Reset AZUREADSSO password](https://learn.microsoft.com/en-us/entra/identity/hybrid/connect/how-to-connect-sso-faq#how-can-i-roll-over-the-kerberos-decryption-key-of-the--azureadsso--computer-account-)

## How can I roll over the Kerberos decryption key of the `AZUREADSSO` computer account?

It's important to frequently roll over the Kerberos decryption key of the `AZUREADSSO` computer account (which represents Microsoft Entra ID) created in your on-premises AD forest.

 Important

We highly recommend that you roll over the Kerberos decryption key at least every **30 days** using the `Update-AzureADSSOForest` cmdlet. When using the `Update-AzureADSSOForest` cmdlet, ensure that you _don't_ run the `Update-AzureADSSOForest` command more than once per forest. Otherwise, the feature stops working until the time your users' Kerberos tickets expire and are reissued by your on-premises Active Directory.

Follow these steps on the on-premises server where you're running Microsoft Entra Connect:

 Note

You need domain administrator and Hybrid Identity Administrator credentials for the steps. If you're not a domain admin and you were assigned permissions by the domain admin, you should call `Update-AzureADSSOForest -OnPremCredentials $creds -PreserveCustomPermissionsOnDesktopSsoAccount`

**Step 1. Get list of AD forests where Seamless SSO is enabled**

1. Navigate to the `$env:programfiles"\Microsoft Azure Active Directory Connect"` folder.
2. Import the Seamless SSO PowerShell module using this command: `Import-Module .\AzureADSSO.psd1`.
3. Run PowerShell as an Administrator. In PowerShell, call `New-AzureADSSOAuthenticationContext`. This command should give you a popup to enter your tenant's Hybrid Identity Administrator credentials.
4. Call `Get-AzureADSSOStatus | ConvertFrom-Json`. This command provides a list of AD forests (look at the "Domains" list) on which this feature has been enabled.

**Step 2. Update the Kerberos decryption key on each AD forest that it was set up on**

1. Call `$creds = Get-Credential`. When prompted, enter the Domain Administrator credentials for the intended AD forest.

 **Note:**
	 - The domain administrator credentials username must be entered in the **SAM account name** format (**contoso\johndoe or contoso.com\johndoe**).  We use the domain portion of the username to locate the Domain Controller of the Domain Administrator using DNS.
	 - The **domain administrator** account used must not be a member of the **Protected Users** group. If so, the operation fails.

2. Call `Update-AzureADSSOForest -OnPremCredentials $creds`. This command updates the Kerberos decryption key for the `AZUREADSSO` computer account in this specific AD forest and updates it in Microsoft Entra ID.
    
3. Repeat the preceding steps for each AD forest that you’ve set up the feature on.
    

 **Note:**
	 If you're updating a forest, other than the Microsoft Entra Connect one, make sure connectivity to the global catalog server (TCP 3268 and TCP 3269) is available.

 **Important:** This doesn't need to be done on servers running Microsoft Entra Connect in staging mode.