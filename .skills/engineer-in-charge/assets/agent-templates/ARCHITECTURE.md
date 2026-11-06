# ARCHITECTURE.md — current architecture (<<DATE>>)

(Describe what exists NOW, not history. History goes to `archive/`.)

## Layers
- Entry/startup: … (what runs before the UI; how failures are surfaced)
- Models: …
- Services: storage · domain logic · integrations · notifications/scheduling …
- UI: navigation structure, shared widgets, design tokens
- Config/CI: …

## Key data flows (draw one per important feature)
```
 entry point A ─┐
 entry point B ─┼→ domain service → storage → consumers (lists, schedulers, reports)
```

## Navigation / naming facts that bite
(e.g. titles hard-coded in one place, two screens with similar names and different roles)

## Known limits (honest)
…
