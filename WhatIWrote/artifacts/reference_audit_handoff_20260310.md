# Reference Audit Handoff

Created: 2026-03-10
Updated: 2026-03-12

## 1. Scope

Target documents:
- `WhatIWrote/docx/Doctoral_Research_Plan_5p_KOR.docx`
- `WhatIWrote/docx/Doctoral_Research_Plan_5p_ENG.docx`
- `WhatIWrote/docx/Doctoral_Research_Plan_Full_KOR.docx`

Purpose:
- align in-text citations and reference lists,
- evaluate whether each citation actually supports the sentence or paragraph where it is used,
- identify cross-document inconsistencies and next follow-up items.

## 2. Verified state as of 2026-03-12

- `citation_case_count=41`
- `listed_not_cited=0`
- `cited_not_listed=0`
- `direct support=29`
- `partial support=12`
- `indirect support=0`
- `not suitable=0`
- `uncertain=0`

Use these files as the current source of truth:
- `WhatIWrote/artifacts/reference_audit.csv`
- `WhatIWrote/artifacts/reference_audit_summary.md`
- `WhatIWrote/artifacts/work_log_20260312_reference_followup.md`

## 3. Follow-up completed on 2026-03-11

### 3.1 Newman alignment in the 5-page plans
- `5p_KOR` now includes `Newman, 2010` in the reference list.
- `5p_ENG` section `4.4` now cites `(Newman, 2010; Traag et al., 2019)` and includes `Newman, 2010` in the reference list.
- Both 5-page plans now use the same `Newman + Traag` structure in `4.4`.

### 3.2 Full_KOR body/reference cleanup
- `P6` now cites `UNFCCC, 2015` directly.
- `P7` now separates platform traits, overseas YouTube cases, and Korean prior studies.
- `P22` now cites `IPCC, 2023` directly.
- `P33` now connects the method description to `Elgammal et al., 2026` and `Lamb et al., 2020`.
- The Full_KOR reference list now includes the `Elgammal` and `Lamb` entries.

### 3.3 P7 alignment in the 5-page plans
- `5p_KOR` and `5p_ENG` now cite `Lim / Lim et al. 2023` directly in `P7`.
- The platform-framing sentence and the Korean prior-work sentence are now separated.

### 3.4 Script and audit refresh
- `scripts/rewrite_5p_docs_dense.py` was updated to match the revised wording.
- `scripts/reference_audit.py` was updated to match the revised citation logic and aliases.
- `artifacts/reference_audit.csv` and `artifacts/reference_audit_summary.md` were regenerated.

## 4. Follow-up completed on 2026-03-12

### 4.1 5-page P7 wording tightening
- `5p_KOR` `P7` was narrowed from a strong platform-suitability claim to a more cautious statement.
- `5p_ENG` `P7` now treats YouTube as a defensible starting point rather than a strongly sufficient site in itself.
- The revised wording keeps `Allgaier, 2019` at the platform level and leaves `Shapiro & Park, 2018` as the more direct support for post-video discussion.

### 4.2 Full_KOR P43 cleanup
- `Full_KOR` `P43` now cites `Franzke et al., 2020` only for internet-research procedure.
- `boyd & Crawford, 2012` was removed from the `Full_KOR` reference list.
- The earlier `boyd, d.` style inconsistency is therefore no longer part of the current Full_KOR draft.

### 4.3 Full_KOR P4/P7 wording tightening
- `Full_KOR` `P4` was rewritten with narrower conceptual wording so the public-arena construction claim leans more explicitly on `Hilgartner & Bosk, 1988`.
- `Full_KOR` `P7` was rewritten with more cautious wording.
- The revised `P7` now treats Korean YouTube as a major observation point rather than stating stronger platform suitability more directly.
- `P7` platform relevance, overseas cases, and Korean prior studies are now separated more explicitly in the paragraph itself.

### 4.4 Script and audit refresh
- `scripts/rewrite_5p_docs_dense.py` was updated so future regeneration keeps the narrowed `P7` wording.
- `scripts/fix_korean_docx_encoding.py` was updated so future Full_KOR regeneration keeps the revised `P4/P7` wording and does not reintroduce `boyd & Crawford, 2012` into `P43`.
- `scripts/reference_audit.py` was updated and the audit artifacts were regenerated.

## 5. Remaining follow-ups

1. Folder/process artifact organization
   - `Doctoral_Research_Plan_Full_KOR.codex_tmp.docx` is intentionally retained as a recovery copy.
   - Backup files and audit artifacts still need an explicit organization decision.

   - `Shapiro & Park, 2018` is still being treated as direct support with external bibliographic confirmation only.
   - `Douglas & Wildavsky, 1982` is still worth a closer source check if that paragraph is revised again.

## 6. Recommended start point for the next session

1. Read `WhatIWrote/artifacts/reference_audit_summary.md` for the current status snapshot.
2. Decide how to group backups, audit outputs, and the temporary recovery copy.
3. If the conceptual-background or YouTube-platform paragraphs change again, re-check the source-strength assumptions around `Shapiro & Park, 2018` and `Douglas & Wildavsky, 1982`.

## 7. Notes

- Temporary recovery copy retained: `WhatIWrote/docx/Doctoral_Research_Plan_Full_KOR.codex_tmp.docx`
- Detailed follow-up logs:
  - `WhatIWrote/artifacts/work_log_20260311_reference_followup.md`
  - `WhatIWrote/artifacts/work_log_20260312_reference_followup.md`
