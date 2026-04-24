---
phase: 5
slug: extract-view-components-final-refactor
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-24
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual testing (no automated test framework yet) |
| **Config file** | none |
| **Quick run command** | `python main.py` (visual inspection) |
| **Full suite command** | Manual full pipeline test |
| **Estimated runtime** | ~30 seconds (app launch + visual check) |

---

## Sampling Rate

- **After every task commit:** Run `python main.py` and verify tab renders
- **After every plan wave:** Full visual inspection of extracted tab
- **Before `/gsd-verify-work`:** Full pipeline test (download → transcribe → translate → dub)
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 1 | None | — | N/A | manual | `python main.py` | ✅ | ⬜ pending |
| 05-01-02 | 01 | 1 | None | — | N/A | manual | `python main.py` | ✅ | ⬜ pending |
| 05-01-03 | 01 | 1 | None | — | N/A | manual | `python main.py` | ✅ | ⬜ pending |
| 05-02-01 | 02 | 2 | None | — | N/A | manual | `python main.py` | ✅ | ⬜ pending |
| 05-02-02 | 02 | 2 | None | — | N/A | manual | `python main.py` | ✅ | ⬜ pending |
| 05-03-01 | 03 | 3 | None | — | N/A | manual | `python main.py` | ✅ | ⬜ pending |
| 05-03-02 | 03 | 3 | None | — | N/A | manual | `python main.py` | ✅ | ⬜ pending |
| 05-04-01 | 04 | 4 | None | — | N/A | manual | `python main.py` | ✅ | ⬜ pending |
| 05-04-02 | 04 | 4 | None | — | N/A | manual | `python main.py` | ✅ | ⬜ pending |
| 05-05-01 | 05 | 5 | None | — | N/A | manual | `python main.py` | ✅ | ⬜ pending |
| 05-05-02 | 05 | 5 | None | — | N/A | manual | Full pipeline test | ✅ | ⬜ pending |
| 05-05-03 | 05 | 5 | None | — | N/A | checkpoint | Human verification | ✅ | ⬜ pending |
| 05-05-04 | 05 | 5 | None | — | N/A | manual | Documentation check | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

**Rationale:** Phase 5 is a refactoring phase (extracting UI code to view files). No new functionality is added, so no new tests are required. Manual testing after each extraction verifies that UI still renders and functions correctly.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Log tab renders correctly | None (refactoring) | Visual UI verification | Open app, click "Nhật Ký" tab, verify log area visible |
| Dub tab renders correctly | None (refactoring) | Visual UI verification | Open app, click "Lồng Tiếng" tab, verify TTS controls visible |
| Source tab renders correctly | None (refactoring) | Visual UI verification | Open app, verify "Nguồn" tab (default), check input and buttons |
| Adjust tab renders correctly | None (refactoring) | Visual UI verification | Open app, click "Điều Chỉnh" tab, verify scroll and preview canvas |
| All tabs functional | None (refactoring) | Integration testing | Click buttons, change inputs, verify no errors |
| Config persistence | None (refactoring) | State management | Change settings, restart app, verify settings persist |
| Full pipeline works | None (refactoring) | End-to-end testing | Download video → transcribe → translate → dub, verify output |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies (manual verification after each task)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify (manual check after every task)
- [x] Wave 0 covers all MISSING references (no missing tests - existing manual testing sufficient)
- [x] No watch-mode flags (N/A - no automated tests)
- [x] Feedback latency < 30s (app launch + visual check)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-04-24

**Note:** This is a refactoring phase with no new functionality. Manual testing is appropriate and sufficient. Future phases may add automated UI tests, but that is out of scope for Phase 5.
