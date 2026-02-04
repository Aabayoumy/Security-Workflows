---
title: "Exchange group permission"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
tags: ["exchange"]
---

**NOTE:** this action needs to understand the exchange environment and ensure that this will not affect the customer

When Exchange is installed, a set of permissions is modified to allow a deep Windows integration. A dependency analysis has shown that the permissions, that Exchange has set, introduced a possibility for privilege escalation.  

The most basic exploitation is that a member of the group `Exchange Windows Permissions` can modify the security permission of the domain, granting itself the right Ds-Replication-Get-Changes-All.

##### To solve this issue:

###### Exchange Server 2013 or a later version
o resolve this issue on Exchange Server 2013 or a later version, customers should install the following cumulative update, as appropriate for their environment:

- Exchange Server 2019 – [Cumulative Update 1](https://support.microsoft.com/kb/4471391)
- Exchange Server 2016 – [Cumulative Update 12](https://support.microsoft.com/kb/4471392)
- Exchange Server 2013 – [Cumulative Update 22](https://support.microsoft.com/kb/4345836)

Environments in which Exchange Server 2013 or a later version is in use require the updated cumulative update package to manually execute **/PrepareAD** in any Active Directory forest in which Exchange Server is installed or in which the directory schema has been prepared to host servers that are running Exchange Server. Additionally, customers who employ multiple domains in a single forest will have to run **/PrepareDomain** in all domains in the forest to lower the permissions that are granted to Exchange Server and to Exchange administrators.

**Note** The **/PrepareDomain** operation automatically runs in the Active Directory domain in which **/PrepareAD** is run. However, it may not be able to update other domains in the forest. For this reason, a domain administrator should run **/PrepareDomain** in other domains in the forest.
###### Exchange Server 2010

Customers who are running Exchange Server 2010 should apply the following manual updates to their environment by using the LDP tool.

1. Start the LDP tool (In the **Run** box, type **ldp.exe**, and then press **Enter**).
2. Connect to the domain namespace that you want to update. (On the **File** menu, click **Connect**.)
3. Bind to the domain namespace by using Domain Admin credentials. (On the **File** menu, click **Bind**.)
4. View the tree by using the base DN that corresponds to the root of the domain context to be updated. (On the **View** menu, click **Tree**.)  
    For example:  
    ![Tree View](https://support.microsoft.com/images/en-us/77379250-825d-5388-6c4e-eacc023e9286)
5. Open Domain Access Control Lists. (Right-Click _domain_, click **Advanced**, and then click **Security Descriptor**.)  
      
    ![Domain Access Control Lists](https://support.microsoft.com/images/en-us/f304f173-46ef-2fcb-91a2-48a039689016)
    
6. Find the two "Allow" ACEs that grant "Write DACL" right to the "Exchange Windows Permissions" group on the "User" and the "INetOrgPerson" inherited object types:  
      
    ![Security descriptor](https://support.microsoft.com/images/en-us/e0de8811-7737-efa4-1d44-f5fa994a2823)  
    **Note**  Do not sort the list. This will change the ACL order.
    
7. Edit each entry to add the "Inherit Only" flag. To do this, double-click the object, select the flag, and then click **OK**.  
      
    ![Access Control Entry](https://support.microsoft.com/images/en-us/d0873642-4d76-3fe1-f8e4-fed0d635d85f)
    
8. Verify that the operation is successful on each ACE. Then, click **Update**.  
      
    ![Security descriptor](https://support.microsoft.com/images/en-us/b1eada7c-c610-02da-fcca-bdbcb0abbdc5)




Steps:
https://support.microsoft.com/en-us/topic/reducing-permissions-required-to-run-exchange-server-when-you-use-the-shared-permissions-model-e1972d47-d714-fd76-1fd5-7cdcb85408ed

[Released: February 2019 Quarterly Exchange Updates | Microsoft Community Hub](https://techcommunity.microsoft.com/blog/exchange/released-february-2019-quarterly-exchange-updates/609061)
