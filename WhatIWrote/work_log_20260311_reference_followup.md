# Work Log: Reference Follow-up

Date: 2026-03-11

## Requests received

- Continue from `WhatIWrote/reference_audit_handoff_20260310.md` and work through the remaining follow-up items.
- Verify whether `Newman` should be added to both 5-page plans or removed.
- Apply the `Full_KOR` follow-up items and re-run the audit.
- Decide whether `Lim / Lim et al. 2023` should be cited directly across all three research-plan drafts.
- Leave an updated log and refresh the files that explain current status.

## Work performed

### 1. Newman alignment in the 5-page plans
- Added `Newman, M. E. J. (2010). Networks: An introduction. Oxford University Press.` to `Doctoral_Research_Plan_5p_KOR.docx`.
- Updated `Doctoral_Research_Plan_5p_ENG.docx` section `4.4` to cite `(Newman, 2010; Traag et al., 2019)` and added the same reference entry.

### 2. Full_KOR body/reference cleanup
- Revised `P6` to cite `UNFCCC, 2015` directly.
- Rewrote `P7` so that platform suitability, overseas YouTube cases, and Korean prior studies are no longer collapsed into a single claim.
- Revised `P22` to cite `IPCC, 2023` directly.
- Rewrote `P33` around `sentiment and position analysis` and connected it to `Elgammal et al., 2026` and `Lamb et al., 2020`.
- Added the `Elgammal` and `Lamb` references to the Full_KOR reference list.
- Recovered the damaged Korean paragraphs by using `Doctoral_Research_Plan_Full_KOR.codex_tmp.docx` as the repair source after a save produced `?` characters.

### 3. 5-page P7 alignment
- Rewrote `P7` in both 5-page plans so that platform framing and Korean prior-work citations are separated.
- Added direct calls to `Lim / Lim et al. 2023` in both documents.

### 4. Script and audit updates
- Updated `scripts/rewrite_5p_docs_dense.py` so future regeneration matches the current wording.
- Updated `scripts/reference_audit.py` so the audit logic matches the revised citations and aliases.
- Re-ran `python scripts/reference_audit.py` until the citation/reference mismatches were cleared.

## Files changed in this session

- `WhatIWrote/Doctoral_Research_Plan_5p_KOR.docx`
- `WhatIWrote/Doctoral_Research_Plan_5p_ENG.docx`
- `WhatIWrote/Doctoral_Research_Plan_Full_KOR.docx`
- `WhatIWrote/reference_audit.csv`
- `WhatIWrote/reference_audit_summary.md`
- `WhatIWrote/reference_audit_handoff_20260310.md`
- `WhatIWrote/README.md`
- `scripts/rewrite_5p_docs_dense.py`
- `scripts/reference_audit.py`

## Final verified status

- `citation_case_count=44`
- `listed_not_cited=0`
- `cited_not_listed=0`
- `direct support=30`
- `partial support=13`
- `indirect support=1`
- `not suitable=0`
- `uncertain=0`

## Remaining follow-ups

1. The `P7` platform-suitability claim in the two 5-page plans still relies mainly on the `Allgaier + Shapiro` combination.
2. `Doctoral_Research_Plan_Full_KOR.docx` `P43` still has a follow-up around the role/style of `boyd & Crawford, 2012`.
3. Backup files, audit artifacts, and the temporary recovery copy still need an explicit folder-organization decision.
