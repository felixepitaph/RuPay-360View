# Wiki: source-facts (what we know about each source; read before scraping or extracting)

## YES BANK
- Card pages: yes.bank.in/personal-banking/yes-individual/cards/credit-cards/<card>. Need JavaScript; sections (rewards, fees, T&C) load only after scrolling. Raw page text is reliable.
- Pages show "prior to 15 June 2026" and "effective 15 June 2026" values side by side. Store both with the date.
- Old names: Select = Prosperity Edge; ACE = Prosperity Rewards Plus; Elite+ = YES Premia. Prosperity Rewards, Cashback, Cashback Plus closed to new customers.
- Network is rarely stated on card pages; take it from the MITC or BIN data.
- Offers page: yes.bank.in/personal-banking/yes-individual/yes-privileges/yes-privileges-offers (public). About 55 live offers, ~12 for credit cards. Card markup tags are unreliable (credit offers tagged "ajio"); read brand from the text.
- Offer T&Cs: PDFs at yes.bank.in/pdf?name=<file>. Some are dead links (Goibibo Nov 2026). The content API behind the page returns unpublished drafts; filter to what the live page shows.
- creditrewardz.yes.bank.in: login with mobile + captcha + OTP. Do not scrape.
- MITC: CMITC_V18_05102026 (version 18, 5 Oct 2026) is in the catalog.

## IDFC FIRST Bank
- Card pages: idfcfirst.bank.in/credit-card/<card>. Plain text; ~30 card links on the listing page. Pages contradict themselves (forex 0% vs 1.5% in FAQ on Wealth; Mayura "1.0% forex" heading). Record contradictions.
- MITC has no version or effective date; use the PDF date.
- Offers: monthly booklet PDF (e.g. Diwali Booklet Nov 2026 V3) has caps, minimum spend and days; firstrewards.in has the FS/EMI tag and expiry only (no API, detail pages add nothing).

## Data (fill in Phase 0)
- Trino access: AiNxt needs a JWT / API token for a read-only service account. Store it in Profile > API Token Vault, never in the repo.
- Semantic-layer views expected: agg_weekly_issuer_merchant, txn_weekly_card_merchant (card_key salted hash), and the agg_* tables in docs/reference/03.
