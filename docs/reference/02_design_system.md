# 01 — Design System, Application Shell & Filter Taxonomy

> **Scope:** UI contract for `apps/shell/` and `packages/shared-ui/`. Every monthly tab built by internal Claude or ChatGPT models must import tokens, formatters, and primitives from this specification so visual drift never occurs across build cycles.

---

## 1. Shell Geometry & Collapsible Navigation

* **Left Navigation Rail:**
  * **Expanded Width:** `224px` (shows workspace group headers, icons, tab names, and sub-tab count badges).
  * **Collapsed Width:** `56px` (icon-only rail with hover tooltips) toggled via a persistent header button or keyboard shortcut (`[`).
  * **Purpose:** Guarantees 100% viewport width when inspecting wide Deal Model phasing tables, 4-card cross-network CVP matrices, interactive India/World maps, or 16-variant Sparkline Anomaly Matrices.
* **Top Utility Bar (Persistent across all workspaces):**
  * Left: Sidebar collapse toggle, active module title, workspace pill badge, and one-line subtitle.
  * Right: **Data Freshness Badge** (e.g., `Trino T+1 · 23 Nov 2026`), Global Search (`Cmd+K` to jump to any BIN, Bank, Card, or Merchant), **Proactive Alerts Drawer** button (badge count), **Copilot Drawer** trigger, Theme Switcher (`Dark Terminal` ↔ `Light Editorial`), and Export button.

---

## 2. Strict Workspace Filter Isolation Rules

Do **not** force one global filter bar onto every tab. The platform is partitioned into three workspaces with distinct scoping:

| Workspace | Tabs Included | Filter Bar Behavior |
| :--- | :--- | :--- |
| **Workspace 1: Telemetry & Economics** | `Command Center`, `Card Economics`, `Wallet Share` | **Shares one persistent Global Context Filter Bar** docked beneath the top header. Switching between these three tabs preserves the exact active bank, segment, rail, and payment-mode cohort. |
| **Workspace 2: Proposition Control Plane** | `Proposition Hub` (`Matrix`, `Spend Simulator`, `Offers Hub`, `Telemetry Overlay`) | **Does NOT inherit the Workspace 1 global bar.** Renders its own local page-level filter bar (adding `Network: RuPay / Visa / Mastercard` and cross-network tier equivalence so competitor cards outside RuPay's Trino lake can be analyzed). |
| **Workspace 3: Commercial Agreements** | `Deal Performance` (`Overview`, `Projections`, `Revenue`, `Scenarios`, `Configure`, `Performance`) | **Does NOT inherit the Workspace 1 global bar.** Scoped by its own **Deal Project Switcher**, **Role Perspective Toggle (`Network A` Edit vs. `Issuer B` Read-Only)**, and pinned **Net BPS Corridor Gauge**. |

---

## 3. The 3-Tier Cascading Filter Taxonomy

Used in Workspace 1 (global bar) and mirrored with a `Network` selector in Workspace 2 (local bar). Filters must visually separate parent filters from child sub-filters so users never get silently locked out of a universal view.

### Tier 1 — Portfolio & Card Scope
* **Issuer Bank:** Multi-select (`All Banks` by default; supports selecting 1, multiple, or all issuers).
* **Cardholder Profile:** Multi-select (`Mass`, `Mass Affluent`, `Affluent`, `Super Premium`).
* **Variant Tier:** Multi-select (`Platinum`, `Select`, `EKAA` — mapped via Tier Equivalence Ladder in Workspace 2).
* **Collateral Type:** Toggle/Multi (`All` | `Unsecured` | `Secured / FD-Backed`).
* **Issuance Type:** Toggle/Multi (`All` | `Proprietary` | `Co-Brand`).
  * **Cascading Sub-Filter (`↳ Co-Brand Focus`):** `All` | `Discretionary` | `Non-Discretionary`. Must render visually indented inside a left-bordered child container directly adjacent to `Co-Brand`, remaining dimmed/disabled unless `Co-Brand` is active.

### Tier 2 — Transaction Rail
* **Rail:** Multi-select (`Domestic POS`, `Domestic E-Com`, `UPI CC`, `International`).
  * **Cascading Sub-Filter (`↳ UPI Merchant Tier`):** `All` | `Small Offline ≤ ₹2K` | `Small Offline > ₹2K` | `Large Offline` | `Online`. Enables visually indented beneath `UPI CC` only when `UPI CC` is selected.

### Tier 3 — Payment / Settlement Mode (Orthogonal to Rail)
* **Payment Mode:** Segmented toggle (`All` | `Regular / Full Swipe (FS)` | `EMI`).
* Keeps EMI volume, EMI offers, and MITC EMI reward exclusions cleanly separated from regular full-swipe behavior across POS and E-Com.

### Active Scope Breadcrumb & Reset Bar
Always render a compact summary strip beneath the filter tiers:
* Displays either a green `Universal View` badge (when no restrictive filters are active) or structured chips showing parent → child hierarchy (e.g., `HDFC Bank, IDFC FIRST • Co-Brand ↳ Discretionary • UPI CC ↳ Large Offline • EMI`).
* Includes a permanent one-click **`↺ Reset to Universal View`** button.

---

## 4. Dual-Theme Design Tokens (CSS Custom Properties)

Build with **Tailwind CSS + `shadcn/ui` primitives + Recharts/Tremor + TanStack Table**. Avoid inline style blocks in feature tabs.

| Token | Dark Terminal (Default — Extends V1.1) | Light Editorial (Stripe / Mercury Mode) |
| :--- | :--- | :--- |
| `--bg-canvas` | `#070810` (with faint dot-grid) | `#F8FAFC` |
| `--bg-panel` | `#0C0E18` | `#FFFFFF` |
| `--bg-surface` | `#10131E` | `#F1F5F9` |
| `--bg-card` | `#141826` (subtle glass/border) | `#FFFFFF` |
| `--border` / `--border-hi` | `#1B1F38` / `#2D3559` | `#E2E8F0` / `#CBD5E1` |
| `--text-primary` / `--text-muted` | `#EBEDF4` / `#868DA8` | `#0F172A` / `#64748B` |
| `--accent` / `--accent-2` | `#635BFF` / `#8B6AFF` | `#4F46E5` / `#6366F1` |
| `--state-green` (Positive / Ceiling) | `#3ECF8E` | `#059669` |
| `--state-amber` (Corridor / Caution) | `#FFB224` | `#D97706` |
| `--state-red` (Negative / Floor / Risk) | `#FF6166` | `#DC2626` |

---

## 5. Non-Negotiable Financial UI Rules

1. **Typography & Tabular Numerals:** Use `Inter` for labels/prose and `JetBrains Mono` with `font-variant-numeric: tabular-nums` on every KPI, table cell, chart axis, and badge so columns align vertically.
2. **State-Only Traffic Light Colors:** Reserve green, amber, and red strictly for variance, corridor pass/fail, MITC exclusions, and anomaly alerts—never for arbitrary series coloring.
3. **Reusable `InfoCard` with `?` Audit Popover:** Every top-level KPI card across all three workspaces must include a `?` trigger (carried over from Deal Model V1.1) that expands to show:
   * Exact SQL aggregation or mathematical formula.
   * Numerator, denominator, and component breakdown rows.
   * Data source table and freshness timestamp.
4. **Centralized Indian Number Formatters (`packages/shared-ui/src/formatters.ts`):**

| Function | Rule | Example Output |
| :--- | :--- | :--- |
| `f0(v)` | `>= 1 Cr`: `x.xxx Cr`; `>= 1 L`: `x.xx L`; `>= 1K`: `x.xxK`; else 2 dp | `16,596.000 Cr` |
| `fR(v)` | Rupee prefix; Cr (3 dp), L (2 dp), else 2 dp | `₹65.672 Cr` |
| `fP(v)` | Percentage to 2 dp | `15.40%` |
| `fB(v)` | Basis points to 2 dp (or 3 dp for Deal reference checks) | `15.996 bps` |
| `fVol(v)` | Volume counts without `₹`: `Cr`, `Mn`, `L`, `K`, else integer | `18.74 Mn` |

---

## 6. Standardized View Templates (Mix & Match)

* **Executive Bento + Right Slide-Over Inspector:** Used in `Command Center` and `Wallet Share`. Clicking any BIN, Bank, or Merchant row opens a right drawer showing its linked CVP summary, MITC flags, and active offers without losing table scroll position.
* **Diagnostic Cliff & Matrix Split:** Used in `Card Economics` (`SLAB_D` histogram + `₹2,000` cliff marker alongside `errcode` waterfall and UPI 2×2 quadrants).
* **Multi-View Catalog + Simulator Split:** Used in `Proposition Hub` (sticky-column matrix with `Show Differences Only`, deterministic spend slider workbench, and 3-mode adaptive telemetry overlay for 1–4 vs. 5–16+ variants).
* **Financial Simulator Workbench:** Used in `Deal Performance` (pinned corridor gauge, 6 full sub-tabs matching V1.1 + Part B, interactive sensitivity heatmap, and SheetJS export controls).