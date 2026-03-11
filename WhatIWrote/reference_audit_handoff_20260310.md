# Reference Audit Handoff

Created: 2026-03-10
Updated: 2026-03-11

## 1. Scope

Target documents:
- `WhatIWrote/Doctoral_Research_Plan_5p_KOR.docx`
- `WhatIWrote/Doctoral_Research_Plan_5p_ENG.docx`
- `WhatIWrote/Doctoral_Research_Plan_Full_KOR.docx`

Purpose:
- align in-text citations and reference lists,
- evaluate whether each citation actually supports the sentence or paragraph where it is used,
- identify cross-document inconsistencies and next follow-up items.

## 2. Verified state as of 2026-03-11

- `citation_case_count=44`
- `listed_not_cited=0`
- `cited_not_listed=0`
- `direct support=30`
- `partial support=13`
- `indirect support=1`
- `not suitable=0`
- `uncertain=0`

Use these files as the current source of truth:
- `WhatIWrote/reference_audit.csv`
- `WhatIWrote/reference_audit_summary.md`
- `WhatIWrote/work_log_20260311_reference_followup.md`

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
- `reference_audit.csv` and `reference_audit_summary.md` were regenerated.

## 4. Remaining follow-ups

1. `5p_KOR` and `5p_ENG` `P7`
   - The platform-suitability claim still depends mainly on `Allgaier + Shapiro`.
   - Decide whether to add a more direct comments/network source or make the wording more conservative.

2. `Full_KOR` `P7`
   - The current structure is much better, but the strongest direct support for the Korean long-term gap still comes from Korean prior studies.

3. `Full_KOR` `P43`
   - `boyd & Crawford, 2012` still reads as a supporting ethics source, but `Franzke et al., 2020` is the more direct grounding for actual internet-research procedure.
   - The `boyd, d.` style inconsistency can still be cleaned up.

4. Folder/process artifact organization
   - `Doctoral_Research_Plan_Full_KOR.codex_tmp.docx` is intentionally retained as a recovery copy.
   - Backup files and audit artifacts still need an explicit organization decision.

## 5. Recommended start point for the next session

1. Read `WhatIWrote/reference_audit_summary.md` for the current status snapshot.
2. Review `Doctoral_Research_Plan_Full_KOR.docx` `P43` and decide how to handle `boyd & Crawford, 2012`.
3. If needed, tighten the `P7` platform-framing language in the two 5-page plans.
4. After that, decide how to group backups, audit outputs, and the temporary recovery copy.

## 6. Notes

- Temporary recovery copy retained: `WhatIWrote/Doctoral_Research_Plan_Full_KOR.codex_tmp.docx`
- Detailed follow-up log: `WhatIWrote/work_log_20260311_reference_followup.md`
