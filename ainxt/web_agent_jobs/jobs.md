# Web Agent jobs (paste into Web Agent, or call from W2)

General: open the page, scroll to the bottom, wait for sections to load, then copy the full visible text. Do not log in anywhere. Do not solve captchas. Return the text with the URL and time.

## J1 YES card pages
For each URL in catalog/sources/registry.json with issuer "YES BANK" and type "cvp_page": open, scroll fully, copy text. Then call r360_source_check. If changed, hand to the Document Agent with skill extract-catalog.

## J2 YES offers page
Open https://www.yes.bank.in/personal-banking/yes-individual/yes-privileges/yes-privileges-offers. Scroll. For each offer card that says "Credit card(s)": copy headline, description, "Offer valid from", "Expires on", and the TnC link file name. Open each TnC link (yes.bank.in/pdf?name=...). If it shows a PDF, read all pages; if it is blank or 404, record "T&C link broken". Offers already in the catalog with an unchanged T&C file need no re-read.

## J3 IDFC card pages
Open https://www.idfcfirst.bank.in/credit-card and list every /credit-card/<card> link. For each card in the registry: open, copy full text including the FAQ. Hand changed pages to the Document Agent.

## J4 firstrewards.in offers (IDFC)
Open https://firstrewards.in/deal?category=all. Copy each offer's merchant, description (FS or EMI tag, "up to Rs X") and expiry. Do not log in.

## J5 Monthly booklets and MITCs (manual drop)
When a new IDFC offers booklet or a new MITC PDF is saved in the project's document folder, read it and hand it to the Document Agent. Note the document version and date.

## Never
creditrewardz.yes.bank.in (login only). Any page that asks for a mobile number, OTP or password.
