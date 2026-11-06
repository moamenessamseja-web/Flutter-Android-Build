---
name: design
description: Shared visual design and UI methodology for all of the owner's Flutter/Android apps (Arabic-first RTL with English LTR support, color tokens, typography scale, spacing, radii, components, accessibility). Use whenever creating or changing screens, themes, widgets, app icons or any visual identity in a Flutter app, or when asked to define the look of a new app. Read DESIGN.md in full before writing UI code.
---

# Design skill

The complete design guide is `DESIGN.md` in this folder (Arabic). It is the single source of truth; this file only tells an agent how to use it.

## How to use it
1. Read `DESIGN.md` fully before touching UI code. Do not paraphrase it from memory.
2. Inspect the target app first. If it already has a theme, tokens or design decisions, extend them; do not replace an existing identity with the guide's example palette.
3. The palette in `DESIGN.md` is a general example ("يمكن تخصيصها بحسب هوية التطبيق"). For a new app, derive its identity from the guide's rules (limited colors, contrast >= 4.5:1, status = icon + text + color) and record the chosen tokens in the target repo's `.agent/ARCHITECTURE.md` and `.agent/DECISIONS.md`, never in this central repo.
4. Implement tokens once (one theme/tokens file in the app), not per screen. Use logical directions (`EdgeInsetsDirectional`, `AlignmentDirectional`, `TextAlign.start`), `SafeArea`, 44x44 minimum touch targets, bundled fonts (no CDN).
5. A screen is not finished until it is checked in RTL and LTR and with enlarged system font. State which of these was actually verified (see the verification ladder in the engineer-in-charge skill).

## Provenance
`DESIGN.md` is the owner's original file, moved unchanged from the repository root (previously `design 2.md`). This `SKILL.md` was added because the supplied design material had no skill entry file.
