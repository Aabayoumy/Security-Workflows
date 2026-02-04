---
title: "Reset KRBTGT Password"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
---

1. Use this script [Microsoft KRBTGT Reset script - https://gallery.technet.microsoft.com/Reset-the-krbtgt-account-581a9e51](https://gist.github.com/mubix/fd0c89ec021f70023695) 
2. Choose mode number `3`.
3. Entre `y` to reset the password.


1.   
    Why does KRBTGT need to be reset twice?  
    KRBTGT keeps a password history of 2, hence we reset it twice to invalidate all tickets issued from old KRBTGT password.

2. What happens when you reset KRBTGT account password once?
    1. After 1st reset the new KRBTGT password replicates to all the DC’s in the Domain.
    2. All new Tickets will use the new password (KRB1).
    3. Old tickets issued by old KRBTGT password (KRBOLD) should continue to work as password history is 2.
    4. Post old tickets expiry they should renew tickets with new KRBTGT password (KRB1).
    5. Present KRBTGT passwords will be KRB1 & KRBOLD.

[FAQs from the Field on KRBTGT Reset - Microsoft Community Hub](https://techcommunity.microsoft.com/t5/core-infrastructure-and-security/faqs-from-the-field-on-krbtgt-reset/ba-p/2367838)
