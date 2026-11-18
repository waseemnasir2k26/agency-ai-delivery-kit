#!/bin/bash
# Scaffold: the three FICTIONAL client data files (synthetic) the client-report skill reads from data/.
set -e
mkdir -p data
cat > data/mehr-bakery.json <<'JSON'
{"client":"Mehr Bakery","contact_email":"owner@mehrbakery.example","week":"2026-11-02 to 2026-11-08",
 "metrics":{"site_visits":1840,"leads":37,"orders":112,"revenue_pkr":486500},
 "events":["Instagram reel on sourdough reached 9,400 views","Eid-style gift box page launched; 21 orders in 3 days","Google Business photos refreshed; 14 new reviews","Newsletter popup added; 63 signups","Checkout error on mobile fixed (was 4% of carts)"],
 "next":["Photograph winter menu","A/B test gift box price"]}

JSON
cat > data/sufi-threads.json <<'JSON'
{"client":"Sufi Threads","contact_email":"hello@sufithreads.example","week":"2026-11-02 to 2026-11-08",
 "metrics":{"site_visits":3120,"leads":58,"orders":204,"revenue_pkr":1275000},
 "events":["Winter shawl collection launched, 88 orders first weekend","WhatsApp order bot answered 412 chats","Abandoned-cart email recovered 19 orders","Size guide added; returns down to 6%","Collab post with a local weaver reached 15,200 views","Homepage speed improved from 4.1s to 2.3s"],
 "next":["Restock embroidered scarves","Add Urdu product titles"]}

JSON
cat > data/noor-dental.json <<'JSON'
{"client":"Noor Dental Clinic","contact_email":"reception@noordental.example","week":"2026-11-02 to 2026-11-08",
 "metrics":{"site_visits":960,"leads":29,"orders":0,"revenue_pkr":0,"bookings":41},
 "events":["Online booking form launched; 41 bookings in the week","Whitening offer page ranked on page 1 for a local search","Reminder SMS cut no-shows from 18% to 9%","Two negative reviews answered within 24h"],
 "next":["Add braces FAQ","Collect patient testimonials with consent"]}

JSON
