# Talking to the owner — templates and tone

Rules: their language · plain words · outcome first · every claim carries its verification level · unknowns named · one decision at a time · no process narration ·
no praise-farming, no apology spirals (state the error, fix, move on) · thank them briefly when they test builds for you.

## Verification phrases (Arabic ↔ English)
- مُثبَت في CI (تحليل + اختبارات + بناء APK) / CI-verified (analysis + tests + APK build)
- لم يُجرَّب على جهاز بعد / not device-tested yet
- جرّبته أنت وعمل / you tested it and it works
- لا أعرف السبب بعد / cause unknown yet
- هذا تخمين وليس مؤكدًا / this is a hypothesis, not confirmed

## Final report (Arabic) — skeleton
```
<سطر واحد: ما الحالة>. (مثال: Build 93 أخضر في CI؛ لم يُجرَّب على جهاز بعد.)

**جرّب الآن:** <اسم البناء/commit> — <٣-٥ خطوات اختبار قصيرة>

**ما أُنجز:** (كل بند بحالة واحدة)
- ...
**ما تم التحقق منه وكيف:** CI فقط / فحص الـ APK / جهازك
**ما لم يُنجز أو غير معروف:** ...
**قرارات مطلوبة منك:** ... (مع توصيتي)
**تنبيه:** <مثال: ألغِ الـ token الذي لصقته في المحادثة>
```
Keep to the length the content needs; on mobile avoid wide tables.

## Short status line (when the system says the owner hasn't heard from you)
"أنا الآن <ما تفعله بالتحديد>، ثم <الخطوة التالية>." — then immediately continue the tool work.

## Decision request
"أحتاج قرارك في نقطة واحدة: <السؤال>. الخيار الأول: ... (الأثر). الخيار الثاني: ... (الأثر). أنصح بـ ... لأن ... وسأكمل في الأثناء ...".

## Bad news / red build
"البناء فشل بسبب <السبب الحقيقي من السجل بكلمات بسيطة>. أصلحته بـ <...> وأضفت اختبارًا يمنع تكراره. البناء الجديد قيد التشغيل." (No drama; the owner mostly needs the cause and the next step.)

## When a previous claim of yours was wrong
"تصحيح: قلت سابقًا <X>. الصحيح <Y> (الدليل: ...). أصلحت الوثائق."

## Security note
"الـ token الذي لصقته ما زال ظاهرًا في المحادثة؛ ألغِه من GitHub وأصدر آخر بصلاحيات محدودة لهذا المستودع، وأعطه لي في بداية الجلسة القادمة."

## English equivalents
"Status: <one line>. Test now: <build> — <3–5 steps>. Done: … Verified (CI only / artifact / your device): … Not done / unknown: … Decisions needed: … (recommendation) …"
