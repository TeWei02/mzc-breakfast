# Mei Zhi Chen · Online Ordering System

A self-hosted ordering platform for **Mei Zhi Chen (美之晨)**, a breakfast shop in Yongkang, Tainan. Customers order online → the shop receives orders in a back-office panel → delivery stops are automatically sorted into the shortest route over the real road network → online payment (ECPay) settles automatically. No commission, no dependence on food-delivery platforms.

[![繁體中文](https://img.shields.io/badge/README-繁體中文-6e7781?style=flat-square)](README.md) [![English](https://img.shields.io/badge/README-English-2f81f7?style=flat-square)](README.en.md)

## Live URLs

| Entry point | URL |
|---|---|
| Customer ordering | https://tewei02.github.io/mzc-breakfast/ |
| Shop back office | https://tewei02.github.io/mzc-breakfast/admin.html |

## Features

| Area | Details |
|---|---|
| Ordering | Toast / burger / egg pancake / scallion pancake / Danish / club sandwich — pick the flavor first, then the base determines the price; drinks in 550 ml (small) and 750 ml (large) |
| Delivery | Minimum order NT$150, free over NT$300, otherwise NT$30 surcharge; coverage: Yanxing, Daqiao, Liujiating; 05:30–10:30 |
| Pickup | Choosing pickup automatically hides the delivery condition card and zeroes the shipping fee |
| Product | House-made chili sauce 750 ml / NT$150, available for in-store pickup or home delivery (7-ELEVEN 賣貨便 / Black Cat) |
| Route planning | One-click optimal stop order in the back office (nearest-first / farthest-first / most efficient / manual), re-planning all delivery orders at once |
| Payments | ECPay: credit card, Apple Pay, Google Pay, ATM virtual account, convenience-store payment code; orders are settled automatically once paid |
| Payment codes | ATM / convenience-store code callbacks automatically write into the order note and set the status to "awaiting payment (code issued)" |
| Food labeling | `sauce.html`: legal label, nutrition label and calculator, bottle sticker, shipping packaging notes |
| Order management | Permanently delete a single order in the back office (with double confirmation), change the admin password online (no redeploy needed) |

## Architecture

```
Customer  index.html ─┐
                      ├─ POST ─→ Google Apps Script (/exec) ─→ Google Sheets (orders)
Back office admin.html ┘                    │
                                            └─→ ECPay (create order / payment callback)
```

- Frontend: pure static single-file HTML, images inlined, hostable directly on GitHub Pages (https)
- Backend: Google Apps Script, data stored in Google Sheets, no server cost
- Payments: ECPay server-side order creation plus two callbacks (payment result / payment-code info)

## Repository layout

| File | Purpose |
|---|---|
| `index.html` | Customer ordering page (single file, inlined images) |
| `admin.html` | Shop back office: order list, route planning, payment status, ECPay settings panel |
| `sauce.html` | Chili sauce food labeling page: legal label, nutrition calculator, printable bottle sticker, shipping packaging |
| `route.png` | Delivery coverage map (currently unreferenced, kept as a spare) |
| `上線操作說明.md` | Deployment and payment integration notes (Chinese) |
| `README.md` | Chinese README (traditional Chinese) |

## Backend API

Every request is a `POST` to the Apps Script `/exec` endpoint, dispatched by `action`. Admin actions require a `token`.

| action | Purpose | Token required |
|---|---|---|
| `order` | Create a new order | No |
| `list` | Read the order list | Yes |
| `shipped` | Mark as dispatched and notify | Yes |
| `paid` | Mark as paid | Yes |
| `route` | Compute the road-network distance matrix | Yes |
| `plan` | Sort stops by the matrix and write back | Yes |
| `ecpay` | Create an ECPay payment order | No |
| `ecpayCfg` | Read / save ECPay settings (keys in Script Properties) | Read: no / Write: yes |
| `deleteOrder` (POST) | Permanently delete that row in the sheet (whole row, irreversible) | Yes |
| `setToken` (POST) | Change the admin password, written to script property `ADMIN_TOKEN` | Yes (old password required) |

## Deployment

### Frontend (GitHub Pages)

```bash
git add .
git commit -m "Update docs"
git push origin main
```

Pages goes live about a minute after the push (branch `main`, repository root).

### Backend (Apps Script)

```bash
clasp push          # upload Code.gs
clasp deploy        # create a new version
```

> If the frontend has the `/exec` URL hard-coded, redeploy with `clasp deploy --deploymentId <old ID>` to update the same deployment; otherwise the frontend URL must be updated as well.

### CI

`.github/workflows/ci.yml` runs on every push and pull request:

- checks that the required static files (`index.html`, `admin.html`, `sauce.html`, `README.md`, `README.en.md`, `LICENSE`) exist
- resolves every local `href` / `src` reference and fails on broken links
- validates that the HTML can be parsed and warns about unclosed tags
- scans for accidentally committed secrets (ECPay keys, Apps Script deployment URLs, admin tokens)

A separate `deploy` job is available through manual dispatch (`workflow_dispatch`) to publish the site with the official GitHub Pages actions; it requires **Settings → Pages → Source = GitHub Actions**.

## Payment go-live (ECPay)

1. Apply for an ECPay individual seller account (ID card, bank passbook cover, 3 photos of the business premises, a reachable sales URL)
2. After approval, get the store number, HashKey and HashIV from the merchant portal
3. In `admin.html` → payment settings → switch to "production" → paste the three values → save
4. The next order uses production, and payments are written back to the sheet automatically

> The test environment uses ECPay's public test store `2000132`; payments there are not real, so the full flow can be tested safely.

## Chili sauce food labeling

`sauce.html` follows Article 22 of the Act Governing Food Safety and Sanitation and contains:

1. **Mandatory label items**: product name, ingredients (descending by amount), food additives, net weight, expiration date and shelf life, storage conditions, country of origin, allergen warning, manufacturer name / phone / address, food business registration number, directions for use
2. **Nutrition label**: two columns (per 100 g and per serving); includes a calculator for ingredient weights and nutrition values (enter recipe weights and ingredient nutrition to get batch and per-serving figures)
3. **Bottle sticker**: roughly 6 × 8 cm, printable and cut-to-fit
4. **Shipping packaging**: outer-box labeling, bubble-wrap cushioning, sealing and leak handling, customer service info

> Every field on the labeling page is editable in the browser and saved to the device's localStorage; press "Print / Save as PDF" afterwards.
> Nutrition values should come from a lab report or a food composition database; the built-in calculator is only a first estimate.

## Security notes

- ECPay keys live in Apps Script **Script Properties**, are **never committed to the repo**, and never appear in URLs
- This repo is public; personal order data (name, phone, address) stays in the sheet only — never upload it
- The admin password is defined by the Apps Script property `ADMIN_TOKEN`; the back-office settings page can change it online (8+ characters, letters and digits), effective immediately without redeploying
- Before `ADMIN_TOKEN` is set, the code falls back to a built-in default; the real password is not written in any document — set it yourself on the settings page
- A transfer-fraud warning is shown on the customer page to reduce the risk of impostors changing account numbers

## Roadmap

- [x] Chili sauce food labeling page (`sauce.html`) and shipping packaging notes
- [x] Delete a single order in the back office, change the admin password online
- [ ] Apply for the ECPay production store number and set the three keys
- [ ] Fill in the food business registration number in `sauce.html`
- [ ] Fill in nutrition values from a lab test or composition database
- [ ] Decide whether to keep the legacy delivery map (`route.png`)
- [ ] LINE official account (start with the free light tier)
- [x] Test orders (T1115001540, T1115001606C) removed from the sheet (2026-11-25, 14 records left)

## License

This is a private system for the shop; all rights reserved. Copying, modification or commercial use without permission is not allowed.

---

*Maintained by 柯德瑋 (TeWei02)*
