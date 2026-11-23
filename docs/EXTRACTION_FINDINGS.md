# First extraction: YES MITC, IDFC MITC, IDFC Nov 2026 offers booklet

Date: 2026-11-23. Files in `catalog/`. All validated with `python scripts/validate_catalog.py`.

## What was extracted
| File | Coverage |
|---|---|
| `catalog/yes_bank/mitc_yes_v18_2026-10-05.json` | Fees per variant, finance charges, forex, general fees, category surcharges (rent, wallet, education, utility, fuel, tolls, railways), utility reward caps, fuel surcharge waiver, lounge spend gates |
| `catalog/idfc_first/mitc_idfc_2026-11.json` | Same sections for IDFC FIRST |
| `catalog/idfc_first/offers_idfc_nov2026_pages3-5_sample.json` | 18 offers from booklet pages 3 to 5 only (of 23 pages) |

## What these documents do NOT contain
- **CVP**: reward earn rates, milestones, lounge counts, welcome benefits. MITCs only cover fees and restrictions. You need the card feature pages or brochures for each variant.
- **Network per variant**: the MITCs mostly don't say which cards are RuPay, Visa or Mastercard. Only the YES "RuPay Virtual" names and the IDFC Digital RuPay card are identifiable. A BIN or product list is needed.
- **EMI economics**: both MITCs say EMI fees are quoted at the time of the transaction. Whether EMI earns rewards or counts toward waivers is not stated.

## Findings that changed the design
1. **MITCs are issuer-wide, not per card.** One document covers 30+ variants with tables that group variants differently for each rule. The MITC schema was rewritten (v2) around that shape: a variants list plus rules that name the variants they apply to.
2. **Rules change on dates.** YES raised forex, cash advance, auto-debit, cash deposit and replacement fees from 15 Jun 2026, and changed fuel waiver ranges. The catalog stores the current value and the previous value where both appear.
3. **Offers booklet merchant names are logos.** The PDF text layer has no merchant names (and has a stale "May'25" validity string under the Zomato tile). Offers must be read from page images. Pages 3 to 5 were done this way; pages 6 to 23 are not extracted.
4. **Offers rarely say Full Swipe vs EMI.** Only some tiles are tagged. The schema now allows `payment_mode: ANY` for untagged offers, and eligible cards are often missing, so the offer-to-card join needs a manual step.
5. **Fee tiers differ a lot between the two banks.** YES charges category fees per transaction or per calendar month with variant-specific thresholds; IDFC charges per statement cycle with almost uniform thresholds (INR 20,000 utility, 30,000 fuel, 25,000 railways, 10,000 tolls; Gaj utility 50,000; none for FIRST Private). This is exactly the MITC-friction input the Simulator needs.

## Needs a human check
- YES utility fee: rule text says "previous calendar month", worked examples use the same month.
- YES RuPay Virtual cards marked as UPI credit cards by inference from the name.
- IDFC MITC has no version or effective date; the date used is the PDF creation date.
- IDFC cash advance fee reads "INR 199"; the worked example (INR 235) is consistent with 199 plus GST.
- Offers marked MEDIUM confidence (bigbasket iPhone, District, Zepto electronics, Croma EMI stacking).
- Sections after the Schedule of Charges in both MITCs were searched for pricing terms, not read line by line.

## Next
1. Offers booklet pages 6 to 23 (travel, furniture, lifestyle, laptops, mobiles, EMI categories, UPI offers).
2. YES: any offers documents; CVP documents for both banks.
3. BIN and product list per variant so the catalog joins to Trino.

## 2026-11-23 scrape feasibility (IDFC CVP, firstrewards offers)
- IDFC card pages (/credit-card/<card>) render as plain text with sections Eligibility/Reward points/Fees/Deals/FAQ. ~30 card links on the listing page.
- Pages contradict themselves (forex, bonus %, fuel waiver caps, lounge gates, fee headers). Store every contradiction in `page_conflicts`; MITC wins for fees.
- First extraction used WebFetch + LLM summary. Production scraper must store raw page text + hash and extract from that.
- firstrewards.in: list page gives title, FS/EMI tag, expiry. Detail page adds nothing (no min txn, cap, eligibility, T&C). No data API seen in network log. Booklet remains the source for conditions.

## 2026-11-23 YES Bank CVP scrape
- yes.bank.in needs JavaScript: WebFetch gets nothing; use a real browser. Card sections load only after scrolling (lazy render), so scroll before reading text.
- Reward-rate pages change materially effective 15 Jun 2026 (extra excluded categories, higher forex markup, narrower select-category MCC lists); pages show both "prior" and "effective" text. Store both with the effective date.
- Prosperity Rewards, Cashback and Cashback Plus are discontinued for new issuance (existing cardholders reissued on expiry). Select = formerly Prosperity Edge; ACE = formerly Prosperity Rewards Plus; Elite+ = formerly YES Premia.
- Co-brand pages (AI Inside, Uni, Niyo) are thin: tiers and caps are not on the card page, so use the MITC / partner T&C.

## 2026-11-23 YES offers (public Card Offers page)
- Page: yes.bank.in/.../yes-privileges/yes-privileges-offers (public). Live list = 55 cards; about 12 credit-card offers, rest debit/business-debit.
- Backing data is an Oracle Content JSON API (type ybl-offers-page-asset-new). It returns 200+ records all marked draft/unpublished, so it must be filtered against what the live page shows.
- Card CSS classes are unreliable for credit offers (default brand tag 'ajio'). Take brand from the offer text.
- Each offer's T&C is a PDF at yes.bank.in/pdf?name=<file>. It opens in the browser PDF viewer (readable only as images through the browser tool). At least one (Goibibo) is a dead link.
- creditrewardz.yes.bank.in is login-only (mobile + captcha + OTP); not scrapable.

## 2026-11-23 re-run
- IDFC booklet: all pages extracted (123 offers). Pages 6-20 are EMI-only ("EMIfy" header). Brand names are logos only: read visually. Pages 21-22 are UPI coupon-code offers.
- Reconciliation against MITCs: 69 matches, 4 conflicts (see docs/RECONCILIATION_2026-11-23.md).
- Scraping moves to AiNxt Web Agent jobs (`ainxt/web_agent_jobs/jobs.md`) with hash-diff via `r360_source_check`.
