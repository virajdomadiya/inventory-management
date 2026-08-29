---
name: sidebar-redesign
description: Redesign this Vue 3 app's UI into a modern SaaS-style interface with a left vertical sidebar (replacing the top nav bar), a consistent design-token spacing/color system, and a polished professional look. Use when asked to redesign the navigation into a sidebar layout, modernize/polish the UI, or apply a SaaS-style design system.
---

# SaaS Sidebar Redesign

This skill redesigns the Factory Inventory Management UI from its current top-nav layout into a modern SaaS-style layout with a left vertical sidebar, a consistent design-token system, and a polished professional look.

**Hard rule: never implement before the approval gate in Step 5 is cleared.** This skill investigates, proposes a concrete plan, and waits for explicit user approval before writing or editing any file. Do not treat "the user asked for a redesign" as approval of a specific design — the specifics (token values, where things move) still need confirmation.

## Step 1 — Investigate current state

Re-read the current app before assuming anything below is still accurate — it may have changed since this skill was written:

- `client/src/App.vue` — the current layout shell: `.top-nav` → `.nav-container` (`.logo`, `.nav-tabs` with `router-link`s, `LanguageSwitcher`, `ProfileMenu`), then `<FilterBar/>`, then `.main-content > <router-view/>`. Two teleported modals (`ProfileDetailsModal`, `TasksModal`) mount at the App root. Also read its global `<style>` block — this is where the shared `.card`, `.stat-card`, `.badge`, `table`, `.page-header` classes live.
- `client/src/main.js` — the registered routes. Only build sidebar entries for **routed** views.
- `client/src/components/*.vue` — confirm the current component inventory (as of writing: `FilterBar.vue`, `LanguageSwitcher.vue`, `ProfileMenu.vue`, and several teleported `*Modal.vue` components sharing one structural pattern: `Teleport to="body"` → `Transition` → overlay → container).
- 2-3 view files' scoped `<style>` blocks (e.g. `Dashboard.vue`, `Orders.vue`) — catalog the spacing/color/radius/font-size values actually in use. Don't assume a formal design system exists; as of writing there are no CSS custom properties anywhere in the app.
- Check for any view file with **no matching route** (e.g. `Backlog.vue` was orphaned as of writing — present on disk, not in `main.js`, with its data instead surfaced inside Dashboard's "Inventory Shortages" table). Treat orphaned views as out of scope for the new sidebar nav unless the user explicitly asks to add them.

## Step 2 — Define the design token system

Add a `:root` block of CSS custom properties to `App.vue`'s global `<style>`. Derive values from whatever the current audit (Step 1) finds as the majority pattern — don't invent a palette from scratch. As of writing, the audit found:

- **Spacing** — mostly a 4px/8px rhythm with some off-grid outliers (e.g. `0.313rem`, `0.813rem`, `0.938rem`). Normalize to a clean scale: `--space-1: 0.25rem` ... `--space-12: 3rem`, snapping outliers to the nearest scale step.
- **Color** — a loose slate + blue-primary + semantic palette repeated as raw hex across files:
  - Backgrounds: `--color-bg: #f8fafc`, `--color-surface: #ffffff`
  - Text: `--color-text: #0f172a`, `--color-text-secondary: #64748b`, `--color-text-muted: #94a3b8`
  - Borders: `--color-border: #e2e8f0`, `--color-border-subtle: #f1f5f9`
  - Primary: `--color-primary: #2563eb`, `--color-primary-bg: #eff6ff`
  - Semantic: success `#059669`/`#d1fae5`, warning `#ea580c`/`#fed7aa`, danger `#dc2626`/`#fecaca`, info `#2563eb`/`#dbeafe`
  - **Flag, don't silently fix**: `Dashboard.vue`'s `.task-add-btn` uses an off-palette gradient (`#667eea`/`#764ba2`) that doesn't match the primary blue used everywhere else. Call this out to the user in the Step 5 plan as a proposed cleanup rather than changing it without asking.
- **Radius** — recurring values `2px/3px/6px/8px/10px` → `--radius-sm: 6px`, `--radius-md: 8px`, `--radius-lg: 10px`.
- **Shadow** — collapse the handful of ad-hoc shadows into `--shadow-sm`, `--shadow-md`.
- **Font size** — several near-duplicate sizes (13/14/15px) → consolidate into a small type scale (`--text-xs` through `--text-3xl`).

Apply tokens to the files actually being touched (App.vue, the new Sidebar, any view being restyled) rather than doing a blind find-and-replace across the entire codebase in one pass.

## Step 3 — Design the sidebar

New component: `client/src/components/Sidebar.vue`.

- Logo/company name at the top (reuse the current `.logo` content from `App.vue`)
- Vertical nav list, one entry per **routed** view only, active state driven by `$route.path` (same logic currently used for `.nav-tabs a.active`)
- Fixed-width, full-height left column (e.g. `240px`), `position: sticky` or fixed as appropriate
- Icons: use small inline SVGs — there is no icon library dependency in `package.json`, and this skill should not add one
- Relocate `ProfileMenu` and `LanguageSwitcher` into a sidebar footer section

The ProfileMenu/LanguageSwitcher relocation is a layout call — surface it explicitly in the Step 5 plan rather than deciding it silently; the user may prefer keeping a slim top bar for those instead.

## Step 4 — Integrate into App.vue

- Change `.app` from a top-to-bottom flex column into a row layout: fixed-width sidebar column + content column
- Move `<FilterBar/>` and `<router-view/>` into the content column. `FilterBar` becomes a slim bar scoped to the content column's width, not a full-viewport-width bar
- Leave the existing `Teleport to="body"` modals untouched structurally — they're layout-agnostic — but re-check z-index: the sidebar replaces `.top-nav`'s `z-index: 100`, so confirm modal overlays still stack above it

## Step 5 — STOP: present the plan and get explicit approval

Before writing or editing a single file, present the user with:

1. The exact token values proposed (spacing/color/radius/shadow/font-size)
2. The sidebar's structure and exactly where `ProfileMenu`/`LanguageSwitcher`/`FilterBar` land
3. Any flagged cleanups (like the off-palette gradient) as proposals, not done deals
4. The full list of files that will be touched

Wait for explicit approval. Do not implement speculatively "to show an example," and do not treat the initial redesign request itself as approval of these specifics.

## Step 6 — Implement

Per this project's root `CLAUDE.md`: **any creation or significant modification of a `.vue` file must be delegated to the `vue-expert` subagent.** Hand vue-expert:

- The approved token list to add to `App.vue`'s `:root`
- The `Sidebar.vue` spec from Step 3
- The `App.vue` layout changes from Step 4

Flag other inconsistencies noticed along the way (e.g. a view's scoped style overriding a global class's spacing, like `.page-header` margin-bottom differing between `App.vue` and `Dashboard.vue` as of writing) rather than silently normalizing them — mention them to the user after implementation, or ask first if they're in scope.

## Step 7 — Verify

- Start (or confirm already running) both dev servers per the Quick Start in root `CLAUDE.md`
- Use Playwright MCP (project-mandated for browser testing) against `http://localhost:3000` to visit every routed view and confirm:
  - Sidebar renders and active-link highlighting is correct per route
  - `FilterBar` still filters data correctly
  - `ProfileMenu` and `LanguageSwitcher` dropdowns/modals still open and function
  - No z-index/overlap regressions between the sidebar and any teleported modal

## Key Reminders

- Never add an orphaned/unrouted view (e.g. `Backlog.vue`) to the new sidebar nav without asking first
- Never skip the Step 5 approval gate — investigate and plan, then stop
- Always delegate `.vue` file creation/edits to the `vue-expert` subagent
- Prefer the new CSS custom properties over introducing more raw hex/rem literals
- No emojis in the UI — this is a business application
