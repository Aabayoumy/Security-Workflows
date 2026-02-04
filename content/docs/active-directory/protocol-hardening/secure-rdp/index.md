---
title: "Secure RDP"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
weight: 200
tags: ["RDP"]
---
# Secure RDP Configuration with Certificate Templates and Group Policy

This comprehensive guide covers the essential steps for securing Remote Desktop Protocol (RDP) connections using certificate templates and Group Policy Objects (GPO). By implementing these security measures, you can eliminate certificate warnings and establish trusted RDP connections throughout your Active Directory environment.

## Prerequisites

Before implementing secure RDP configurations, ensure you have[1][2]:

- **Active Directory Certificate Services (AD CS)** installed and configured with an enterprise CA
- **Domain Administrator privileges** or equivalent permissions
- **Windows Server 2016 or later** for the certificate authority
- **Group Policy Management Console (GPMC)** access
- **Remote Server Administration Tools (RSAT)** installed on management workstations

## Part 1: Creating the RDP Certificate Template

### Step 1: Access Certificate Templates Console

1. On your Certificate Authority server, open **Server Manager**
2. Navigate to **Tools** → **Certification Authority**
3. Right-click on **Certificate Templates** and select **Manage**[1][3]

### Step 2: Duplicate the Computer Template

1. In the Certificate Templates console, locate the **Computer** template
2. Right-click the **Computer** template and select **Duplicate Template**[1][3]
3. Choose the appropriate compatibility level (Windows Server 2016 or later recommended)[4]

### Step 3: Configure Template Properties

#### General Tab
- **Template display name**: `RDPAuthentication` or `RemoteDesktopComputer`
- **Template name**: Must match the display name exactly (no spaces)[3]
- **Validity period**: Set according to your organization's policy (typically 1-2 years)[1]

#### Extensions Tab
This is the most critical configuration step[1][5]:

1. Click **Edit** next to **Application Policies**
2. **Remove** the existing **Client Authentication** policy
3. Click **Add** → **New** to create a new application policy
4. **Name**: `Remote Desktop Authentication`
5. **Object Identifier (OID)**: `1.3.6.1.4.1.311.54.1.2`[1][5][6]
6. Remove all other application policies except:
   - **Remote Desktop Authentication** (OID: 1.3.6.1.4.1.311.54.1.2)
   - **Server Authentication** (OID: 1.3.6.1.5.5.7.3.1) - optional but recommended[7]

#### Security Tab
Configure enrollment permissions[1][5]:

1. Add **Domain Computers** group with **Enroll** and **Autoenroll** permissions
2. If domain controllers need RDP certificates, add **Domain Controllers** group with **Enroll** and **Autoenroll** permissions
3. Ensure **Authenticated Users** has **Read** permissions

#### Cryptography Tab
- **Minimum key size**: 2048 bits (4096 bits recommended for enhanced security)[1]
- **Request hash**: SHA-256 or higher

### Step 4: Issue the Certificate Template

1. Return to the **Certification Authority** console
2. Right-click **Certificate Templates** → **New** → **Certificate Template to Issue**
3. Select your newly created RDP certificate template
4. Click **OK** to publish the template[1][3]

## Part 2: Configuring Group Policy for Certificate Deployment

### Step 1: Create or Edit a Group Policy Object

1. Open **Group Policy Management Console (GPMC)**
2. Create a new GPO or edit an existing one (e.g., "RDP Certificate Deployment")
3. Right-click the GPO and select **Edit**[8][9]

### Step 2: Configure Certificate Template Setting

Navigate to the following path in the Group Policy Management Editor[8][9]:

**Computer Configuration** → **Policies** → **Administrative Templates** → **Windows Components** → **Remote Desktop Services** → **Remote Desktop Session Host** → **Security**

1. Double-click **Server authentication certificate template**
2. Select **Enabled**
3. In the **Certificate Template Name** field, enter the exact template name: `RDPAuthentication`
4. Click **OK**[8][9]

### Step 3: Configure Additional RDP Security Settings

#### Enable Network Level Authentication
Navigate to the same security folder and configure[10][11]:

1. **Require user authentication for remote connections by using Network Level Authentication**
   - Set to **Enabled**
   - This adds an additional authentication layer before establishing the RDP session

#### Configure Security Layer
1. **Require use of specific security layer for remote (RDP) connections**
   - Set to **Enabled**
   - Select **SSL (TLS 1.0)** or **Negotiate** (recommended)[12][13]

#### Set Encryption Level
1. **Set client connection encryption level**
   - Set to **Enabled**
   - Select **High Level** encryption[12]

## Part 3: Access Control and User Rights Assignment

### Step 1: Configure Remote Desktop Access

Navigate to[14][15][16]:

**Computer Configuration** → **Policies** → **Windows Settings** → **Security Settings** → **Local Policies** → **User Rights Assignment**

1. Double-click **Allow log on through Remote Desktop Services**
2. Click **Add User or Group**
3. Add the appropriate security groups (e.g., "Domain Admins", "RDP Users")
4. Click **OK**[14][15]

### Step 2: Configure Local Group Membership

Navigate to[17]:

**Computer Configuration** → **Preferences** → **Control Panel Settings** → **Local Users and Groups**

1. Right-click and select **New** → **Local Group**
2. Select **Remote Desktop Users (built-in)** from the dropdown
3. Add the domain security groups that should have RDP access
4. Set action to **Update**[17]

### Step 3: Enable Remote Desktop Service

Navigate to[15]:

**Computer Configuration** → **Policies** → **Administrative Templates** → **Windows Components** → **Remote Desktop Services** → **Remote Desktop Session Host** → **Connections**

1. **Allow users to connect remotely by using Remote Desktop Services**
   - Set to **Enabled**

## Part 4: Firewall Configuration

### Step 1: Configure Windows Firewall Rules

Navigate to[17]:

**Computer Configuration** → **Policies** → **Windows Settings** → **Security Settings** → **Windows Firewall with Advanced Security**

1. Right-click **Inbound Rules** → **New Rule**
2. Select **Port** → **TCP** → **Specific local ports**: `3389`
3. Allow the connection for **Domain** and **Private** profiles
4. Name the rule: "Remote Desktop - User Mode (TCP-In)"[18]

## Part 5: Additional Security Hardening

### Step 1: Implement Additional Security Measures

Configure these additional security settings for enhanced protection[19][20]:

#### Session Management
- **Set time limit for disconnected sessions**: 15 minutes
- **Set time limit for active but idle Remote Desktop Services sessions**: 60 minutes
- **End session when time limits are reached**: Enabled

#### Device Redirection Control
Disable unnecessary device redirections[19][20]:
- **Do not allow COM port redirection**: Enabled
- **Do not allow LPT port redirection**: Enabled  
- **Do not allow supported Plug and Play device redirection**: Enabled
- **Do not allow drive redirection**: Enabled
- **Do not allow clipboard redirection**: Enabled

#### Access Restrictions
- **Restrict Remote Desktop Users to a single Remote Desktop Services session**: Enabled
- **Limit number of connections**: Set appropriate limit based on licensing

### Step 2: Configure Account Lockout Policies

Navigate to[19]:

**Computer Configuration** → **Policies** → **Windows Settings** → **Security Settings** → **Account Policies** → **Account Lockout Policy**

1. **Account lockout threshold**: 5 attempts
2. **Account lockout duration**: 30 minutes
3. **Reset account lockout counter after**: 30 minutes

## Part 6: Deployment and Testing

### Step 1: Link the Group Policy Object

1. In **Group Policy Management Console**, right-click the target Organizational Unit (OU)
2. Select **Link an Existing GPO**
3. Choose your RDP certificate deployment GPO
4. Click **OK**[8]

### Step 2: Force Group Policy Update

On target computers, run[8]:
```cmd
gpupdate /force
```

### Step 3: Verify Certificate Deployment

1. On a target computer, open **Certificate Manager** (certmgr.msc)
2. Navigate to **Personal** → **Certificates**
3. Verify that the RDP certificate has been issued and is valid
4. Check that the certificate has the correct **Enhanced Key Usage** (Remote Desktop Authentication)[1]

### Step 4: Test RDP Connection

1. Attempt to connect to a target computer using Remote Desktop Connection
2. Verify that no certificate warning appears
3. Confirm that the connection uses the trusted certificate
4. Test that Network Level Authentication is working properly[11]

## Troubleshooting

### Common Issues and Solutions

#### Certificate Not Appearing
- Verify the certificate template is published on the CA[1]
- Check that the computer account has **Enroll** permissions
- Ensure the Group Policy has been applied and updated

#### RDP Connection Fails
- Verify the user has **Allow log on through Remote Desktop Services** right[14][15]
- Check that the user is a member of the Remote Desktop Users group
- Confirm Windows Firewall allows RDP traffic[18]

#### Certificate Warnings Still Appear
- Verify the certificate template name matches exactly in Group Policy[8][9]
- Check that the certificate contains the correct OID (1.3.6.1.4.1.311.54.1.2)[1][5]
- Ensure the certificate is valid and not expired

## Best Practices

### Security Recommendations

1. **Use dedicated certificate templates** specifically for RDP authentication with the Remote Desktop Authentication OID[1][5]
2. **Implement Network Level Authentication** to prevent unauthorized access attempts[10][11]
3. **Regularly rotate certificates** according to your organization's security policy
4. **Monitor certificate expiration** and implement automated renewal processes[1]
5. **Restrict RDP access** to only necessary users and groups[14][15]
6. **Enable comprehensive logging** for RDP connections and certificate events[19]

### Operational Considerations

1. **Test in a lab environment** before deploying to production
2. **Implement gradual rollout** to minimize impact on users
3. **Monitor certificate deployment** across all target systems
4. **Maintain documentation** of certificate templates and Group Policy settings
5. **Regular security audits** of RDP access permissions and certificate usage[19][20]

By following this comprehensive guide, you will have implemented a robust, secure RDP infrastructure that eliminates certificate warnings while maintaining strong authentication and encryption standards. The combination of properly configured certificate templates and Group Policy ensures consistent security across your entire Active Directory environment.

Sources
[1] Managed Certificates for Remote Desktop Protocol https://directaccess.richardhicks.com/2025/02/20/managed-certificates-for-remote-desktop-protocol/
[2] Use certificates in Remote Desktop Services - Learn Microsoft https://learn.microsoft.com/en-us/windows-server/remote/remote-desktop-services/remote-desktop-services-certificates
[3] Trusted Remote Desktop Services SSL Certs for Win10/2019 - Derek Seaman's IT Blog https://www.derekseaman.com/2018/12/trusted-remote-desktop-services-ssl-certs-for-win10-2019.html
[4] Using SSL/TLS Certificates for Remote Desktop (RDP) | Windows OS Hub https://woshub.com/securing-rdp-connections-trusted-ssl-tls-certificates/
[5] Configuring a certificate template for Remote Desktop (RDP ... https://www.gradenegger.eu/en/configuring-a-certificate-template-for-remote-desktop-rdp-certificates/
[6] ADCS – Create a Template for Remote Desktop Certificate via (AD CS) https://www.chader.fr/en/adcs-create-a-template-for-remote-desktop-certificate-via-ad-cs/
[7] Should Remote Desktop use a dedicated certificate template? https://serverfault.com/questions/1039615/should-remote-desktop-use-a-dedicated-certificate-template
[8] 05. Create and Deploy RDP TLS Certificate with GPO - YouTube https://www.youtube.com/watch?v=-TECgemk_88
[9] How to Create RDP Certificate Enrollment GPO? - Ask Garth https://askgarth.com/blog/how-to-create-rdp-certificate-enrollment-gpo/
[10] Enforce NLA (Network Level Authentication) for improved RDS and ... https://www.linkedin.com/pulse/enforce-nla-network-level-authentication-improved-rds-valentin-xfoje
[11] Network Level Authentication https://rmm.datto.com/help/de/Content/5AGENT/NetworkLevelAuthentication.htm
[12] Tutorial GPO - Configure Remote Desktop security level to TLS https://techexpert.tips/windows/gpo-configure-remote-desktop-security-level-tls/
[13] Forcing RDP to use TLS Encryption - Dispel https://dispel.com/blog/forcing-rdp-to-use-tls-encryption
[14] How to Add Users and Grant RDP Permissions on Windows Server https://lizardsystems.com/terminal-services-manager/articles/how-to-add-users-and-grant-rdp-permissions-on-windows-server-a-step-by-step-guide/
[15] Configure Users & Groups to Log on with Remote Desktop | Ninja One https://www.ninjaone.com/blog/log-on-with-remote-desktop-in-windows/
[16] Deny user or group logon via RDP - Windows Server - Learn Microsoft https://learn.microsoft.com/en-us/troubleshoot/windows-server/remote/deny-user-permissions-to-logon-to-rd-session-host
[17] Edit "Remote Desktop Users" through group policy https://serverfault.com/questions/292944/edit-remote-desktop-users-through-group-policy
[18] How To Enable Remote Desktop Via Group Policy Objects (GPO) https://www.helpwire.app/blog/remote-desktop-group-policy/
[19] Hardening RDP if you have to use it https://www.cert.govt.nz/information-and-advice/guides/hardening-rdp-if-you-have-to-use-it/
[20] Hardening RDP if you have to use it | CERT NZ https://www.cert.govt.nz/it-specialists/guides/hardening-rdp-if-you-have-to-use-it/
[21] Best practices to prevent RDP security issues | TechTarget https://www.techtarget.com/searchvirtualdesktop/tip/Best-practices-to-prevent-RDP-security-issues
[22] RDP - Configure the certificate for remote desktop session host server license part- 3 https://www.youtube.com/watch?v=4P4EoJVHABc
[23] Using Group Policy to Enable Remote Desktops - Trio MDM https://www.trio.so/blog/group-policy-enable-remote-desktop/
[24] Deploy RDP Certificates with GPO: Secure Guide - TheSecMaster https://thesecmaster.com/blog/step-by-step-procedure-to-deploy-rdp-certificates-using-gpo
[25] Allow security group to rdp to certain computer OU only - Super User https://superuser.com/questions/1398797/allow-security-group-to-rdp-to-certain-computer-ou-only
[26] Creating RDP Certificates - PKI Solutions https://www.pkisolutions.com/creating-rdp-certificates/
[27] Remote Desktop listener certificate configurations - Windows Server https://learn.microsoft.com/en-us/troubleshoot/windows-server/remote/remote-desktop-listener-certificate-configurations
[28] How to Use Trusted Certificates with Remote Desktop Services - Dell https://www.dell.com/support/kbdoc/en-eg/000273687/windows-server-how-to-configure-certificates-for-remote-desktop-services
[29] Create custom Group Policy to control RDP access to VMs https://serverfault.com/questions/1011311/create-custom-group-policy-to-control-rdp-access-to-vms
[30] How do I install an SSL Certificate onto RDP for Windows Server ... https://knowledge.digicert.com/quovadis/ssl-certificates/ssl-installation/how-do-i-install-an-ssl-certificate-onto-rdp-for-windows-server-2008
[31] Securing RDP Connections with Trusted SSL-TLS Certificates https://intranetssl.net/blog/securing-rdp-connections-with-trusted-ssl-tls-certificates
[32] Managing RPD Server certificates in Windows Server - Fudo Security https://download.fudosecurity.com/documentation/fudo/5_4/online_help/en/main/en/uc_rdp_cert.html
[33] Improvements to configuring Remote Desktop Service Host certificates in Windows 8, Windows 8.1, Windows Server 2012 and Windows Server 2012 R2 https://techcommunity.microsoft.com/t5/security-compliance-and-identity/improvements-to-configuring-remote-desktop-service-host/ba-p/248741
[34] Configure the Server Certificate Template for Network Remote Access https://learn.microsoft.com/th-th/windows-server/networking/core-network-guide/cncg/server-certs/configure-server-certificate-template-remote-access-network-policy-server
[35] Configure the Server Certificate Template for Network Remote Access https://learn.microsoft.com/en-us/windows-server/networking/core-network-guide/cncg/server-certs/configure-server-certificate-template-remote-access-network-policy-server
[36] Certificate template concepts in Windows Server https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certificate-template-concepts
[37] How to Create RDP Certificates. - YouTube https://www.youtube.com/watch?v=kihc8GJw9ME
[38] Remote Desktop Services enrolling for TLS certificate from an ... https://techcommunity.microsoft.com/blog/askds/remote-desktop-services-enrolling-for-tls-certificate-from-an-enterprise-ca/4137437
[39] Active Directory Certificate Services CA Integration for RDP https://www.strongdm.com/docs/admin/secrets-management/certificate-authorities/adcs-ca/
[40] Create RDP Certificate Template in Local CA - TheSecMaster https://thesecmaster.com/blog/how-to-create-a-template-for-rdp-certificate
[41] How can I get an OID for a certificate template? https://serverfault.com/questions/610024/how-can-i-get-an-oid-for-a-certificate-template
[42] Manage certificate templates in Windows Server https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/manage-certificate-templates
[43] Manually requesting a Remote Desktop (RDP) certificate https://www.gradenegger.eu/en/manual-application-for-a-remotedesktop-rdp-certificate/
[44] Configure Active Directory Certificate Services User Templates https://www.youtube.com/watch?v=_--B3FYH7WI
[45] Object Identifiers (OID) in PKI https://www.pkisolutions.com/object-identifiers-oid-in-pki/
[46] AD CS Certificate Templates: Best Practices https://www.securew2.com/blog/ad-cs-certificate-templates-security-best-practices
[47] RDP and GPO setting Server Authentication certificate template (Microsoft Windows Server 2016) https://serverfault.com/questions/1059058/rdp-and-gpo-setting-server-authentication-certificate-template-microsoft-window
[48] How to configure RDP settings via GPO - TruGrid Help https://help.trugrid.com/en/article/how-to-configure-rdp-settings-via-gpo-1b8hn6g/
[49] ARCHIVED: How can I use a GPO to force NTLMv2? https://kb.iu.edu/d/atcd
[50] One Identity Safeguard for Privileged Sessions 6.9.3 - Administration Guide https://support.oneidentity.com/technical-documents/safeguard-for-privileged-sessions/6.9.3/administration-guide/rdp-specific-settings/enabling-tls-encryption-for-rdp-connections/
[51] Group Policy | Enable Remote Desktop on PC's | Select allowed users. https://learn.microsoft.com/en-us/answers/questions/1659509/group-policy-enable-remote-desktop-on-pcs-select-a
[52] What is network level authentication? | Atera's Blog https://www.atera.com/blog/what-is-network-level-authentication/
[53] One Identity Safeguard for Privileged Sessions 6.0.2 - Administration Guide https://support.oneidentity.com/technical-documents/safeguard-for-privileged-sessions/6.0.2/administration-guide/rdp-specific-settings/enabling-tls-encryption-for-rdp-connections/
[54] What is network level authentication? And how to enhance it with zero trust – GoTo Resolve https://www.goto.com/it/blog/what-is-network-level-authentication-and-how-to-enhance-it-with-zero-trust
[55] One Identity Safeguard for Privileged Sessions 6.0.3 - Administration Guide https://support.oneidentity.com/technical-documents/safeguard-for-privileged-sessions/6.0.3/administration-guide/rdp-specific-settings/enabling-tls-encryption-for-rdp-connections/
[56] Remote Desktop Services Security Settings https://docs.vmware.com/en/VMware-Horizon-7/7.13/horizon-remote-desktop-features/GUID-611FBE11-3D42-411F-9F2B-6AA3D86401DC.html
[57] What is Network Level Authentication? - Portnox https://www.portnox.com/cybersecurity-101/network-level-authentication-nla/
[58] One Identity Safeguard for Privileged Sessions 6.0.1 - Administration Guide https://support.oneidentity.com/technical-documents/safeguard-for-privileged-sessions/6.0.1/administration-guide/rdp-specific-settings/enabling-tls-encryption-for-rdp-connections/
[59] Remote Desktop Secuirty for Windows 7 client via GPO Part 1 Getting Started https://www.youtube.com/watch?v=al1ayUsU0io
[60] What Is Network Level Authentication? - SecurityFirstCorp.com https://www.youtube.com/watch?v=Hl4FsFBsTvw
[61] User Rights Assignment - Windows 10 | Microsoft Learn https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/user-rights-assignment
[62] Allow or Deny Users to Logon with Remote Desktop in Windows 10 https://winaero.com/allow-deny-users-logon-remote-desktop-windows-10/
[63] Allow log on through Remote Desktop Services - Windows 10 https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/allow-log-on-through-remote-desktop-services
[64] User Rights Assignment: RDP | CptJesus's Blog https://blog.cptjesus.com/posts/userrightsassignment/
[65] Allow Logon through Remote Desktop Services Add User Greyed Out https://www.anyviewer.com/how-to/allow-logon-through-remote-desktop-services-add-user-greyed-out-2578.html
[66] Add a user to Services RDP permissions - Windows Server https://learn.microsoft.com/en-us/troubleshoot/windows-server/remote/add-user-services-rdp-permissions
[67] “Allow Logon through Terminal Services” group policy and “Remote Desktop Users” group. | Microsoft Community Hub https://techcommunity.microsoft.com/blog/askperf/8220allow-logon-through-terminal-services8221-group-policy-and-8220remote-deskto/374961
[68] Allow log on through Remote Desktop Services https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-R2-and-2012/dn221985(v=ws.11)
[69] Set access privileges for Remote Desktop https://support.apple.com/guide/remote-desktop/set-access-privileges-apdfab787da/mac
[70] Allow log on through Remote Desktop Services | Microsoft Learn https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn221985(v=ws.11)
