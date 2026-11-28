# Design to Flutter

Before coding inspect theme, navigation, state management, reusable widgets, architecture/decision files, and implementation inventory. Confirm Flutter version from repository configuration; do not assume latest.

Keep app-specific tokens in one app-owned location: color roles, typography, spacing, radii, borders/elevation, icon sizes, motion. The gateway defines method, not a universal palette.

Prefer EdgeInsetsDirectional, AlignmentDirectional, TextAlign.start, SafeArea, and deliberate scroll ownership. Avoid fixed heights for text-heavy content and nested scrollables unless intentional. Use explicit Directionality.ltr for numeric-plus-Latin runs where bidi is ambiguous. Add semantics to icon-only controls and charts. Do not replace real behavior/data with mock values to match a screenshot.

Verification ladder: (1) source inspected, (2) analyzer, (3) automated tests, (4) CI build, (5) artifact installed/inspected, (6) owner-device confirmation. A green APK does not prove visual fidelity; screenshot/device review is separate.

Acceptance: approved hierarchy/layout preserved; behavior preserved; tokens centralized and app-specific; RTL/mixed runs correct; narrow width/large font do not clip; actual empty/error/offline states handled; touch targets/semantics adequate; analyzer/tests/CI reported honestly; visual verification status explicit.
