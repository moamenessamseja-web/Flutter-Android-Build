---
name: design
description: Product discovery, information architecture, visual design, UX flows, critique, and Flutter implementation methodology. Activate for any app screen, flow, theme, component, responsive behavior, or visual identity task.
---

# Product Design & Flutter UI Skill

## Mission
Design useful, coherent, distinctive products—not merely attractive screens. Understand the product and its users before choosing a visual style. This is a shared method, not a universal visual theme: each target app owns its identity, tokens, assets, and screen specifications.

## Entry protocol
1. Read the gateway `.agent/README.md`; follow `engineer-in-charge` first.
2. Read this skill and the existing `DESIGN.md` fully. DESIGN.md remains the shared Flutter/Android baseline, not a mandatory palette or substitute for product design.
3. Inspect the target repository, its `.agent/` files, product brief, implementation, and frozen decisions.
4. Identify the requested deliverable: discovery, audit, concept, screen design, design system, implementation, or review.
5. Reuse existing architecture and components. Do not start coding before the product and task are understood.

## Seven competencies
1. **Visual Hierarchy:** define what users notice first, second, and later through scale, contrast, spacing, position, grouping, and typography.
2. **Information Architecture:** organize entities, tasks, navigation, labels, and content relationships before arranging cards.
3. **Visual Language:** derive the product's identity through color, type, shape, density, imagery, iconography, and motion.
4. **Component Composition:** compose screens from meaningful groups and reusable components; avoid turning every datum into a card.
5. **UX Design:** design complete task flows, states, feedback, error recovery, accessibility, and real usage conditions.
6. **Design to Development:** translate approved decisions into responsive, maintainable Flutter widgets and tokens without visual drift.
7. **Design Critique:** inspect against explicit criteria, explain defects and trade-offs, and iterate using evidence.

## Workflow gates

### A — Understand the product
Read the brief, current implementation, and owner decisions. Identify users, primary jobs, context, constraints, connectivity, device conditions, accessibility, and product promise. Separate owner-stated facts, observed implementation, inferences, and unknowns. Do not invent personas, workflows, market research, or scope.

### B — Structure information
Identify entities, relationships, source values, derived values, events, and states. Rank tasks by importance, frequency, and failure cost. Map navigation and screen responsibilities. Decide what belongs on the first screen versus details. Define multiple-record, empty, and long-content behavior. Cards are not the default container.

### C — Choose visual direction
Derive direction from purpose, audience, context, and brand constraints. Define 3–5 attributes and explain why they fit. Study references as patterns, not templates to copy. Define app-owned tokens for color, typography, spacing, shape, elevation, iconography, and motion. Separate brand, category, and semantic status colors. Verify contrast; never communicate status by color alone. Do not impose one gateway palette on all apps.

### D — Compose
Establish page-level hierarchy before component styling. Choose lists, rows, cards, sheets, tabs, navigation, and drawers according to content relationships and task frequency. Give each component one job. Define anatomy, variants, states, spacing, and responsive behavior. Avoid nested cards, redundant labels, gratuitous gradients, and unnecessary shadows.

### E — Specify interaction
For important screens define applicable empty, populated, loading, error/recovery, success, disabled, selected/focused, offline, permission-denied, long-text, large-font, narrow-screen, and destructive states. Specify trigger, feedback, resulting state, persistence, and recovery. Do not invent loading states for local synchronous operations.

### F — Implement in Flutter
Follow existing architecture and dependencies; add packages only for demonstrated needs. Centralize app tokens. Use logical directional APIs and explicit direction for mixed Arabic/Latin content. Keep UI, state, domain logic, and persistence separated according to target architecture. Never replace real behavior with static mock data. Keep changes reviewable.

### G — Critique and verify
Compare implementation with approved brief and screen spec. Review target device size, narrow widths, RTL, LTR where supported, and enlarged system font. Inspect screenshots or run the app when possible; otherwise say visual verification was not performed. Run analyzer/tests/CI through gateway procedures. Report source, analyzer, tests, CI, artifact, and owner-device verification separately. Record app-specific decisions in the target repository, not this shared skill.

## Minimum deliverables
| Task | Minimum output |
|---|---|
| New product | Product brief + information architecture + visual direction |
| Existing screen audit | Evidence-based critique with severity, impact, correction |
| New screen | Screen specification with hierarchy, components, interactions, states |
| New identity | Tokens + typography + component principles |
| Flutter implementation | Code + tests/CI evidence + verification limits |
| Design review | Seven-competency review + prioritized issues + acceptance criteria |

## Decision rules
- Product correctness precedes decoration; clarity precedes novelty.
- Every design decision must serve a user task, identity, or accessibility need.
- Preserve an existing identity unless the owner authorizes redesign.
- A screenshot does not prove it represents the whole system.
- Never claim a mockup is implemented or a screen visually tested unless it was.
- State uncertainty and trade-offs; avoid endless alternatives.
- This skill does not override engineer-in-charge, security rules, or project architecture.

## References
Read the relevant files under `references/`: product discovery, information architecture, visual hierarchy/language, composition, UX states, critique, and Flutter implementation.

## Templates
Use relevant files under `templates/`: PRODUCT-DESIGN-BRIEF.md, SCREEN-SPEC.md, DESIGN-REVIEW.md. Do not create all templates for a minor change.
