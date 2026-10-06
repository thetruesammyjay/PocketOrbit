# PocketOrbit — DESIGN.md

> **Your crypto, in one clear view.**

PocketOrbit is a read-only crypto portfolio companion built around clarity, provenance, and calm. The visual system should make complicated portfolio data feel understandable without making the product feel like a trading terminal, casino, or speculative dashboard.

The product should feel like **a personal financial notebook with an orbital navigation system**: quiet surfaces, precise data, a small amount of playful space-themed illustration, and strong source/timestamp cues.

---

## 1. Brand direction

### Brand idea

**Pocket + Orbit**

- **Pocket** = personal, portable, close to the user.
- **Orbit** = many assets, wallets, exchanges, and networks revolving around one understandable portfolio view.

The logo and visual language should communicate **aggregation, movement, and control** without using generic candlesticks, rockets, “to the moon” imagery, or aggressive crypto symbolism.

### Personality

PocketOrbit should feel:

- calm
- transparent
- modern
- global
- technically credible
- friendly to non-traders
- lightly playful, never childish
- security-conscious without looking like a cybersecurity product

### Product tone

Use plain language:

- “Portfolio value”
- “Last updated 4 min ago”
- “Imported from Binance CSV”
- “Price source: CoinGecko”
- “Some records could not be matched”
- “This wallet is read-only”

Avoid hype language:

- “Alpha”
- “Moon”
- “Guaranteed”
- “Winning”
- “Best coin”
- “Buy now”
- “High conviction”
- “100x”

---

## 2. Visual concept

### Design theme

> **Orbital notebook on soft mineral paper**

The base experience is light and spacious. Data cards look like precise sheets placed on a warm off-white workspace. The brand color appears as orbital paths, active navigation, chart highlights, selected states, and illustration accents.

The interface should be visually richer than a typical accounting dashboard but significantly calmer than an exchange trading UI.

### Design balance

- **80% utility:** portfolio data, balances, transactions, imports, sources.
- **15% brand:** orbital geometry, micro-illustrations, subtle decorative marks.
- **5% delight:** mascots, empty states, onboarding, success screens.

Mascots should never compete with portfolio numbers.

---

## 3. Logo system

### Primary logo

Format:

**[icon] PocketOrbit**

The icon should be based on a compact orbital mark:

- a rounded “pocket” / capsule / circular core;
- one clean tilted orbital ring;
- one small orbiting dot;
- no Bitcoin symbol;
- no currency sign;
- no candlestick chart;
- no rocket.

The wordmark should feel geometric and modern with slightly rounded forms.

### Logo variants

Create and maintain:

1. **Primary horizontal:** icon + PocketOrbit wordmark.
2. **Dark horizontal:** light wordmark on dark background.
3. **Icon only:** favicon, mobile app icon, loading state.
4. **Monochrome:** single-color mark for documents and tiny UI placements.

### Clear space

Minimum clear space around the logo = the diameter of the orbiting dot × 3.

### Minimum sizes

- Horizontal logo: 120px wide minimum.
- Icon: 20px minimum in product UI.
- Favicon: simplified icon at 16/32px.

---

## 4. Color system

### Core colors

| Token | Value | Role |
|---|---:|---|
| `--po-canvas` | `#F7F7F4` | Main page background |
| `--po-surface` | `#FFFFFF` | Cards, sheets, modals |
| `--po-surface-soft` | `#F0F1EC` | Secondary sections, inset areas |
| `--po-ink` | `#131419` | Main headings, strong controls |
| `--po-text` | `#41434A` | Body text |
| `--po-muted` | `#7B7E87` | Helper text, inactive nav |
| `--po-border` | `#E3E4DE` | Hairline borders |
| `--po-orbit` | `#6C5CE7` | Primary brand accent |
| `--po-sky` | `#56B7FF` | Secondary data accent |
| `--po-mint` | `#18C98B` | Positive / reconciled |
| `--po-sun` | `#FFC857` | Pending / attention |
| `--po-coral` | `#FF6B6B` | Error / destructive |
| `--po-violet-soft` | `#EFECFF` | Selected surfaces |
| `--po-sky-soft` | `#EAF6FF` | Informational surfaces |
| `--po-mint-soft` | `#E8FAF3` | Success surfaces |
| `--po-sun-soft` | `#FFF6D9` | Warning surfaces |
| `--po-coral-soft` | `#FFF0F0` | Error surfaces |

### Color hierarchy

**Primary CTA:** `#131419`

Use near-black for the most important action. PocketOrbit is a financial tracking product; the primary button should feel stable and deliberate.

**Brand selection / active state:** `#6C5CE7`

Use Orbit Violet for:

- active bottom-nav item
- selected portfolio filters
- selected time range
- progress markers
- orbital illustration lines
- focus rings
- small chart highlights

Do not flood large surfaces with purple.

### Portfolio charts

Charts may use:

- Orbit Violet `#6C5CE7`
- Sky `#56B7FF`
- Mint `#18C98B`
- Sun `#FFC857`
- Coral `#FF6B6B`

Never use green alone to imply “good investment” or red alone to imply “bad asset.” Green/red should represent actual positive/negative movement or status only.

---

## 5. Typography

### Recommended fonts

**Display / brand headings:** `Space Grotesk`

- 500 / 600
- slightly tightened tracking
- geometric enough to echo the orbital identity
- use only for display and strong page headings

**Product UI / body:** `Inter`

- 400 / 500 / 600
- tables, labels, controls, financial values, helper text

**Numeric data:** use Inter with `font-variant-numeric: tabular-nums`.

### Type scale

| Role | Size | Weight | Line height |
|---|---:|---:|---:|
| Display | 64px | 600 | 1.02 |
| Hero mobile | 44px | 600 | 1.06 |
| Page title | 32px | 600 | 1.15 |
| Section title | 24px | 600 | 1.2 |
| Card title | 18px | 600 | 1.3 |
| Body | 16px | 400 | 1.55 |
| Compact body | 14px | 400 | 1.5 |
| Label | 13px | 500 | 1.4 |
| Micro | 12px | 500 | 1.35 |

### Financial numbers

Portfolio totals should use:

- 32–48px on desktop depending on hierarchy
- 30–36px on mobile
- weight 600
- tabular numerals

Do not make gains/losses visually larger than total portfolio value.

---

## 6. Spacing and shape system

### Base spacing

Use a 4px base unit.

Preferred scale:

`4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96`

### Radius

| Component | Radius |
|---|---:|
| Small controls | 8px |
| Inputs | 12px |
| Cards | 16px |
| Large feature cards | 20px |
| Bottom nav | 24px |
| Modal / bottom sheet | 24px |
| Pills | 9999px |
| Mascot illustration containers | 28–40px |

PocketOrbit should feel soft, but not bubbly.

### Borders and elevation

Primary card treatment:

```css
border: 1px solid #E3E4DE;
box-shadow: 0 1px 2px rgba(19, 20, 25, 0.03);
```

Floating surfaces:

```css
box-shadow:
  0 10px 30px rgba(19, 20, 25, 0.08),
  0 1px 3px rgba(19, 20, 25, 0.06);
```

Avoid heavy glassmorphism on data-heavy dashboard surfaces.

---

## 7. Icon system — Hugeicons

Use **Hugeicons** throughout the product.

Recommended implementation:

```bash
pnpm add @hugeicons/react @hugeicons/core-free-icons
```

Create one app-level wrapper so icon sizing and stroke weight remain consistent:

```tsx
import { HugeiconsIcon } from "@hugeicons/react";

export function Icon({ icon, size = 20, ...props }) {
  return (
    <HugeiconsIcon
      icon={icon}
      size={size}
      color="currentColor"
      strokeWidth={1.6}
      {...props}
    />
  );
}
```

### Icon rules

- Default style: **Stroke Rounded**.
- Default size: 20px.
- Compact UI: 16–18px.
- Bottom nav: 22–24px.
- Empty-state feature icon: 28–32px.
- Use `currentColor`.
- Do not mix icon libraries.
- Do not use emojis as functional icons.
- Always pair ambiguous icons with labels.
- Import only the icons actually used.

### Semantic icon map

Use the closest Hugeicons equivalent available in the installed pack.

| Action | Icon intent |
|---|---|
| Overview | Home |
| Portfolio | Wallet / Coins |
| Activity | Transaction / Clock / History |
| Insights | Analytics / Chart |
| Add wallet | Wallet Add |
| Import CSV | File Import / Upload |
| Sources | Database / Link |
| Exchanges | Building / Exchange |
| Networks | Nodes / Blockchain |
| Refresh | Reload / Synchronize |
| Alerts | Notification |
| Reports | File Export / Document |
| Learn | Book / Help |
| Security | Shield |
| Settings | Settings |
| More | More Horizontal |
| Close | Cancel / X |
| Search | Search |
| Filter | Filter |
| Sort | Sorting |
| User | User |
| Admin | Dashboard / Grid |

---

## 8. Illustration and mascot system

PocketOrbit uses small, friendly space objects as guides.

### Mascot style

- flat vector illustration
- simple rounded geometry
- warm off-white negative space
- dark ink outline
- Orbit Violet, Sky, Mint, Sun, and Coral accents
- subtle paper/grain texture allowed
- expressive dot eyes and minimal facial features
- no gradients
- no 3D render
- no glossy crypto coin aesthetic
- no space helmets on human characters
- transparent PNG exports

### Mascot family

#### 1. Orbit — primary guide

A small rounded pocket-shaped satellite/orb with a tilted orbital ring and one orbiting dot.

Role:

- onboarding
- empty portfolio
- “all synced”
- general help

Personality:

- calm
- curious
- dependable

#### 2. Scout — source detective

A compact satellite / scanner mascot with a tiny antenna and a source-tag card.

Role:

- data sources
- wallet discovery
- reconciliation
- unmatched asset warnings
- stale-data explanations

#### 3. Comet — activity guide

A small star/coin-like character with a short orbital trail.

Role:

- transaction timeline
- imports
- “new activity”
- progress
- completed sync

### Mascot placement

Use mascots in:

- landing hero
- onboarding
- empty states
- import completion
- 404
- help / education
- first successful portfolio creation

Do not place mascots:

- next to every table row
- inside financial charts
- beside error text that needs immediate seriousness
- in admin incident screens

---

## 9. Landing page

### Header

Desktop:

- logo left
- Product
- How it works
- Security
- Learn
- primary CTA: **Build your portfolio**
- secondary: **Sign in**

Mobile:

- logo
- menu button
- compact CTA

### Hero

Headline:

> **Your crypto, in one clear view.**

Supporting copy should explain that users can connect public wallets or import exchange statements without giving PocketOrbit trading or withdrawal control.

Primary CTA:

**Create my portfolio**

Secondary CTA:

**See how it works**

Visual:

A composed portfolio card cluster with a subtle orbital path and one mascot. Do not imitate an exchange trading screen.

### Main marketing sections

1. One portfolio, many sources.
2. Know where every number came from.
3. Read-only by design.
4. Understand your activity.
5. Built for global portfolios.
6. Plain-language crypto education.
7. Security and privacy principles.

---

## 10. User dashboard

### Desktop shell

Use:

- left rail / sidebar: 232–248px
- top utility bar
- central max-width content
- optional right-side context drawer only on detail pages

Sidebar items:

1. Overview
2. Portfolio
3. Activity
4. Sources
5. Insights
6. Learn
7. Settings

Bottom area:

- sync status
- user avatar
- theme toggle if implemented

### Dashboard overview

Top hierarchy:

1. selected portfolio
2. total portfolio value
3. reporting currency
4. value-change summary
5. last updated
6. source-quality indicator

Core cards:

- Portfolio value
- Allocation
- Accounts & wallets
- Recent activity
- Data quality / reconciliation
- Market movement context
- Sync status

### Portfolio value card

Show:

- total value
- reporting currency
- selected time range
- absolute change
- percentage change
- line chart
- price-source note
- latest calculation timestamp

Never imply the graph is a trading recommendation.

### Allocation

Views:

- by asset
- by source
- by network

Use donut or segmented bar sparingly. Always provide a readable list beside/below the chart.

### Accounts & wallets

Each source card:

- provider/network icon
- user-defined label
- source type
- balance value
- sync status
- last updated
- warning badge if incomplete

### Transaction timeline

Each row:

- transaction type
- asset
- amount
- fiat value at recorded/available timestamp
- source
- fee
- date/time
- classification confidence/status if applicable

Use clear transfer direction:

**From Binance → Ethereum Wallet**

instead of “OUT TX”.

### Data-quality states

Supported statuses:

- Fresh
- Delayed
- Partial
- Needs review
- Unmatched
- Offline
- Import only

Every status needs a short explanation on hover/tap.

---

## 11. Mobile dashboard

The mobile experience should feel like a polished native finance app even though it is delivered in Next.js.

### Mobile page structure

- sticky compact header
- scrollable content
- safe-area spacing
- persistent bottom navigation
- bottom sheets for secondary actions
- cards become single-column
- tables become stacked rows/cards

### Mobile bottom navigation

Use **five items maximum**.

#### User mobile nav

1. **Home** — overview
2. **Portfolio** — assets and allocation
3. **Activity** — timeline
4. **Insights** — charts and explanations
5. **More** — opens action sheet

The active item uses Orbit Violet.

Inactive items use muted gray.

Each item includes:

- Hugeicon
- label
- minimum 44×44px tap area

### More button

The **More** tab opens a rounded bottom sheet rather than navigating immediately.

Sheet actions:

- Add wallet
- Import exchange CSV
- Sources
- Refresh data
- Alerts
- Reports / export
- Learn
- Security
- Settings

Group these into:

**Add & connect**
**Tools**
**Account**

Use a 2-column icon-action grid on smaller phones if needed.

### Mobile action sheet

```text
┌─────────────────────────────┐
│ ─────                       │
│ More                        │
│                             │
│ [Add Wallet] [Import CSV]   │
│ [Sources]    [Refresh]      │
│                             │
│ Tools                       │
│ [Alerts]     [Reports]      │
│ [Learn]      [Security]     │
│                             │
│ [Settings]                  │
└─────────────────────────────┘
```

The sheet should:

- respect bottom safe area
- close by swipe-down, X button, or outside tap
- trap focus for accessibility
- keep labels visible under icons

---

## 12. User onboarding

### Step 1 — Welcome

Explain PocketOrbit in one sentence.

Show Orbit mascot.

CTA:

**Start with a wallet or file**

### Step 2 — Choose source

Cards:

- Public wallet address
- Exchange CSV
- Demo portfolio

Clearly label:

**Read-only. Never enter a seed phrase or private key.**

### Step 3 — Import / address entry

Show supported formats/networks before user submits.

### Step 4 — Processing

Use a vertical workflow:

1. File received
2. Records validated
3. Assets identified
4. Prices matched
5. Portfolio calculated

Each step should show its source/result.

### Step 5 — Review

Show:

- matched records
- warnings
- unmatched rows
- reporting currency
- calculated total

User confirms before the data becomes part of the active portfolio.

---

## 13. Source provenance component

This is one of PocketOrbit’s signature UI components.

Every major balance or valuation can expose a **Source Drawer**.

### Trigger

A small text control:

**Source & freshness**

### Drawer contents

- balance source
- price source
- retrieval time
- calculation time
- market pair or identifier if relevant
- network / contract identifier if relevant
- known limitations
- stale / estimated flag
- raw-source reference where safe

This should visually reinforce PocketOrbit’s “traceable” principle.

---

## 14. Empty, loading, error, and uncertainty states

### Empty

Use mascot + one action.

Example:

> No wallets or exchange files yet.  
> Add your first source to build your portfolio.

### Loading

Prefer skeletons for cards/tables.

Use a small orbital spinner only for workflow actions.

### Error

Show:

- what failed
- what remains available
- whether displayed data is stale
- retry action
- source detail

Bad:

> Something went wrong.

Better:

> We could not refresh this wallet. Your last successful balance from 18 minutes ago is still shown.

### Partial data

Never hide partial-state warnings.

Use a `Partial` badge and a short explanation.

---

## 15. Admin dashboard

The admin dashboard is operational, not decorative.

Do not reuse mascots inside incident-heavy admin screens.

### Desktop admin navigation

1. Overview
2. Users
3. Portfolios
4. Imports
5. Data sources
6. Asset registry
7. Jobs
8. System health
9. Audit log
10. Settings

### Admin overview cards

- active users
- portfolios created
- imports today
- wallet sync jobs
- failed jobs
- stale sources
- unmatched assets
- API provider health

### Source health

Table columns:

- provider
- connector
- status
- last success
- latency
- rate-limit state
- failures
- affected portfolios
- action

### Asset registry

Admin can inspect:

- canonical asset ID
- symbol
- name
- network
- contract address
- provider mappings
- conflicts
- verification state

### Import diagnostics

Show:

- import ID
- format / exchange
- rows received
- rows accepted
- rows rejected
- unmatched assets
- validation errors
- user-safe error summary
- internal diagnostics

Never expose secrets or raw credentials.

### Admin mobile nav

Use:

1. Overview
2. Sources
3. Jobs
4. Users
5. More

**More** opens:

- Imports
- Asset registry
- Audit log
- System health
- Settings

---

## 16. Tables

Desktop tables should be clean and highly legible.

Rules:

- 48–56px row height
- sticky header when useful
- tabular numerals
- right-align numerical values
- left-align labels
- row hover is subtle
- no zebra stripes by default
- filters appear above, not inside table headings
- mobile converts rows into stacked data cards

---

## 17. Charts and data visualization

### General rules

- always show units
- always show selected date range
- tooltips include timestamp
- use tabular numerals
- show missing intervals honestly
- do not smooth away missing data
- do not fabricate candles or price points

### Portfolio history

Default:

- clean line / area chart
- Orbit Violet line
- very low-opacity fill
- no gradient fill
- range selector: 1D, 7D, 1M, 3M, 1Y, ALL

### Allocation

Prefer:

- horizontal bars for comparison
- donut only when categories are few
- always include exact values and percentages in text

### Gain/loss

Use directional color only when it represents actual change.

Provide a neutral mode for accessibility if needed.

---

## 18. Forms

Inputs:

- 44–48px minimum height
- 12px radius
- visible label above input
- helper text below
- high-contrast focus ring

Wallet address inputs should:

- preserve full value in copy action
- visually truncate only after validation
- identify network separately
- never auto-assume chain based only on address if ambiguous

File import should show:

- accepted type
- max size
- provider template
- privacy note
- processing status

---

## 19. Buttons

### Primary

Black background, off-white text.

Use for one major action per section.

### Secondary

White surface, 1px border, dark text.

### Brand-select

Soft violet background with Orbit Violet text.

Use for selected filters/tabs, not primary submission.

### Destructive

Coral soft background + dark coral text for low-risk confirmation.

Solid coral only for final destructive confirmation.

---

## 20. Badges

Use compact badges for state, not decoration.

Examples:

- Fresh
- Delayed
- Partial
- Read-only
- Public address
- CSV import
- Needs review
- Unmatched
- Synced

Badge styling:

- 6–8px vertical padding
- 10px horizontal
- 9999px radius
- 12px text
- paired icon only when helpful

---

## 21. Dialogs and bottom sheets

Desktop:

- centered dialog, max-width 520–640px

Mobile:

- bottom sheet by default

Use destructive confirmations only when needed.

For wallet removal, explain:

- imported/read data being removed
- public blockchain data remains public
- the wallet itself is unaffected

---

## 22. Accessibility

Minimum requirements:

- WCAG AA contrast for text and controls
- visible keyboard focus
- minimum 44×44px touch targets
- charts must have text alternatives
- never encode state by color alone
- labels remain visible
- status icons include text
- motion respects `prefers-reduced-motion`
- bottom sheets use focus trapping
- nav labels stay visible on mobile

---

## 23. Motion

Motion should feel orbital, not flashy.

Allowed:

- 160–220ms button / menu transitions
- 220–320ms bottom sheet
- small orbit rotation on loading
- subtle mascot entrance in onboarding
- chart reveal when data first loads

Avoid:

- bouncing portfolio totals
- pulsing gains
- confetti for value increases
- casino-like animations
- constant floating decorative elements

---

## 24. Responsive breakpoints

Recommended:

```text
sm: 640px
md: 768px
lg: 1024px
xl: 1280px
2xl: 1536px
```

Layout behavior:

- `< 768`: native-app-inspired bottom nav
- `768–1023`: compact side rail where appropriate
- `>= 1024`: full sidebar + desktop dashboard
- marketing pages may keep top navigation across tablet

---

## 25. Technical product architecture

### Frontend

- Next.js
- TypeScript
- Tailwind CSS
- Hugeicons
- deploy on Vercel

### API

- Python
- FastAPI
- deploy on Railway

### Database

- NeonDB / PostgreSQL

### Data flow

```text
Next.js Web App
      ↓
FastAPI API
      ↓
Workflow / Import Coordinator
      ↓
Validation + Normalization
      ↓
Deterministic Portfolio Engine
      ↓
PostgreSQL / NeonDB
      ↓
Provider Connectors
  ├─ Exchange files / APIs
  ├─ Market-data providers
  └─ Blockchain providers
```

### Backend principle

Calculations must remain deterministic.

AI may:

- explain an already-computed result
- summarize data-quality issues
- explain terminology
- guide a user through reconciliation

AI must not:

- invent portfolio balances
- invent prices
- invent transactions
- recommend guaranteed returns
- make unsupported tax claims

---

## 26. Data model visual states

Every imported or retrieved record should support metadata such as:

- `source_type`
- `source_name`
- `source_record_id`
- `retrieved_at`
- `effective_at`
- `asset_id`
- `network_id`
- `contract_address`
- `quality_status`
- `is_estimated`
- `is_stale`
- `match_confidence`
- `normalization_version`

The UI should expose relevant parts of this metadata through Source & Freshness details instead of dumping raw metadata into the main interface.

---

## 27. Security UI principles

Security should be visible but calm.

Persistent rule in onboarding / connection screens:

> PocketOrbit will never ask for your seed phrase or private key.

If read-only APIs are added later:

- show requested permissions before connecting
- explicitly state “No trading” and “No withdrawals”
- visually separate exchange credential configuration from portfolio data
- allow immediate disconnect
- show last successful connection time

Never display full API secrets after creation.

---

## 28. Copy patterns

### Good

**Last updated 4 min ago**

**Price source: CoinGecko**

**3 records need review**

**This wallet is read-only**

**We could not identify one token automatically**

**Your displayed total excludes 2 unmatched records**

### Avoid

**Everything looks amazing!**

**Your portfolio is winning**

**Hot assets**

**Best performers to buy**

**You’re down bad**

**Guaranteed opportunity**

---

## 29. Dark mode

Dark mode can be added after the core light system is stable.

Suggested tokens:

| Token | Value |
|---|---:|
| Canvas | `#0E0F12` |
| Surface | `#15161B` |
| Surface soft | `#1B1D22` |
| Border | `#2A2C33` |
| Heading | `#F6F6F2` |
| Body | `#C8CAD1` |
| Muted | `#8C909B` |
| Orbit | `#8C7CFF` |

Do not make dark mode neon-heavy.

---

## 30. Design QA checklist

Before shipping a screen, verify:

- Does the user know where each important number came from?
- Is the last-updated state visible where freshness matters?
- Is stale or partial data clearly labeled?
- Is there only one dominant CTA?
- Are icons from Hugeicons?
- Does every ambiguous icon have a label or tooltip?
- Are numbers tabular and aligned?
- Can the screen work without mascot artwork?
- Is mobile navigation usable with one hand?
- Does the More sheet keep secondary actions out of the primary nav?
- Are portfolio actions clearly read-only?
- Is there any language that sounds like investment advice?
- Is the interface understandable to someone who is not a trader?

---

## 31. CSS token starter

```css
:root {
  --po-canvas: #F7F7F4;
  --po-surface: #FFFFFF;
  --po-surface-soft: #F0F1EC;

  --po-ink: #131419;
  --po-text: #41434A;
  --po-muted: #7B7E87;
  --po-border: #E3E4DE;

  --po-orbit: #6C5CE7;
  --po-sky: #56B7FF;
  --po-mint: #18C98B;
  --po-sun: #FFC857;
  --po-coral: #FF6B6B;

  --po-violet-soft: #EFECFF;
  --po-sky-soft: #EAF6FF;
  --po-mint-soft: #E8FAF3;
  --po-sun-soft: #FFF6D9;
  --po-coral-soft: #FFF0F0;

  --po-radius-sm: 8px;
  --po-radius-input: 12px;
  --po-radius-card: 16px;
  --po-radius-lg-card: 20px;
  --po-radius-nav: 24px;
  --po-radius-sheet: 24px;
  --po-radius-pill: 9999px;

  --po-shadow-card: 0 1px 2px rgba(19, 20, 25, 0.03);
  --po-shadow-floating:
    0 10px 30px rgba(19, 20, 25, 0.08),
    0 1px 3px rgba(19, 20, 25, 0.06);
}
```

---

## 32. Tailwind v4 starter

```css
@theme {
  --color-po-canvas: #F7F7F4;
  --color-po-surface: #FFFFFF;
  --color-po-surface-soft: #F0F1EC;

  --color-po-ink: #131419;
  --color-po-text: #41434A;
  --color-po-muted: #7B7E87;
  --color-po-border: #E3E4DE;

  --color-po-orbit: #6C5CE7;
  --color-po-sky: #56B7FF;
  --color-po-mint: #18C98B;
  --color-po-sun: #FFC857;
  --color-po-coral: #FF6B6B;

  --color-po-violet-soft: #EFECFF;
  --color-po-sky-soft: #EAF6FF;
  --color-po-mint-soft: #E8FAF3;
  --color-po-sun-soft: #FFF6D9;
  --color-po-coral-soft: #FFF0F0;
}
```

---

## 33. Product screen map

### Public

- `/`
- `/how-it-works`
- `/security`
- `/learn`
- `/privacy`
- `/terms`
- `/login`
- `/register`

### User app

- `/app`
- `/app/portfolio`
- `/app/activity`
- `/app/sources`
- `/app/insights`
- `/app/learn`
- `/app/settings`
- `/app/import`
- `/app/wallets/add`
- `/app/reports`

### Admin

- `/admin`
- `/admin/users`
- `/admin/portfolios`
- `/admin/imports`
- `/admin/sources`
- `/admin/assets`
- `/admin/jobs`
- `/admin/system`
- `/admin/audit`
- `/admin/settings`

---

## 34. Final visual rule

If a design choice makes PocketOrbit look more like a trading exchange, remove it.

If a design choice makes the origin, freshness, or meaning of portfolio data clearer, keep it.

PocketOrbit should always feel like:

> **the calm place where a user understands their crypto — not the place where they are pressured to trade it.**
