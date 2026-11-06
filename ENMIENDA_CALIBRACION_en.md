*English translation for readers. The authoritative, sealed document is the Spanish original `ENMIENDA_CALIBRACION.md`, whose commit is cited in the article. Where the two differ, the original governs.*

# Amendment to the human calibration (§3.6): from four raters to three

**Date:** 2026-11-03
**Decision:** Federico Gutiérrez-Correa (first author, fgc)
**Timing:** after receiving the three spreadsheets from the co-authors and BEFORE computing any calibration statistic. This file and the changes to the article are committed before running
`codigo/calibracion.py`; the order is preserved in the git history.

## What the design fixed before receiving ratings said

- The four authors (fgc, jals, cdeo, waag) rate blind the sealed sample of 60 outputs (seed 20261028, SHA-256 `50240120e4f2…`).
- Analyses (i)–(iii) and, in addition, (iv): repeat (i)–(iii) with and without the first author, because fgc read the pilot outputs (phase 1) unblinded.

## What changes

- **Three raters rate:** jals (Jerri Alejandro López Sánchez), cdeo (Cristian David
  Echeverri Ocampo) and waag (Wilson Andrés Araque Garzón). None had seen any outputs before rating.
- **The first author does not rate.** Analysis (iv) is eliminated; it existed only to measure the effect of his exposure to the pilot.
- (i)–(iii), the sample, the rubric, the rounding for κ, the reweighting of strata (30/240 and
  210/240) and the code `calibracion.py` do not change. It is run without `--primer-autor`.

## Why

Analysis (iv) protected against one risk: that the rater exposed to the pilot would bias the consensus. Without that rater the risk disappears, and the consensus is formed only by blinded raters. The cost is having one fewer rater (three instead of four), which gives less precision to the agreement among humans. This cost is declared in the limitations.

## Partial exposure that must be declared

On 2026-11-03, while taking inventory of the received files, the AI assistant printed in its tool output the per-item scores of waag (S001–S020) and of cdeo (S001–S002). No statistic was computed. The first author saw those values before deciding on the amendment (he confirmed it on 2026-11-04:
«I already saw them» [*«ya los vi»*]); the decision did not rely on any statistic, because none had been computed. Since the first author no longer rates, this exposure does not contaminate any rating, but it is recorded because the decision to amend came after the receipt of the data.

## Spreadsheets received (raw, unedited)

| rater | file | exported (UTC) | items | SHA-256 of the sample |
|---|---|---|---|---|
| cdeo | calibracion_cdeo_2026-10-28.json | 2026-10-29T03:30:49Z | 60/60 | 50240120e4f2… |
| jals | calibracion_jals_2026-10-29.json | 2026-10-29T14:59:46Z | 60/60 | 50240120e4f2… |
| waag | calibracion_waag_2026-11-01.json | 2026-11-01T22:45:23Z | 60/60 | 50240120e4f2… |

They are stored in `datos/calibracion/` in the same commit as this amendment.

SHA-256 of each raw file (to verify that they were not edited afterwards):

```
4cf5547418f2c7f41580f53c5d999b649d75e2de7ed570c6485e058d55fb8a21  datos/calibracion/calibracion_cdeo_2026-10-28.json
66598d64b4854a927ea880664765869b1f261150c90cb36978072a74c9bff586  datos/calibracion/calibracion_jals_2026-10-29.json
25510b450f071060372d638406606a58344de92f73f84b40bc4cf9b6a3237f53  datos/calibracion/calibracion_waag_2026-11-01.json
```

## Note after the computation (2026-11-03, commit following `ccd093c`)

- **κ in the "zeros" stratum, malevolence.** `datos/calibracion_resultado.json` reports κ = 0.0. The
  code returns 0 when one of the two sides has no variance (the judges gave 0 to all 30 items of that stratum by definition), because in that case the observed matrix coincides with the expected one. The article applies the rule fixed in §3.6: without variance, κ is undefined and only the exact agreement (70 %) is reported. This is not a discrepancy between the code and the text.
- **Confirmed by the first author (2026-11-04):** he saw the scores printed on 2026-11-03 («I already saw them» [*«ya los vi»*]). The earlier version of the section "Partial exposure that must be declared" said he had decided without consulting them; the assistant had written that sentence without verifying it, and it was false. It was corrected.

## Independence of the raters (2026-11-04)

In the review sheet (draft 5), the checkbox "I did not discuss the content with other authors before exporting" was ticked only by waag; jals and cdeo left it unticked. When asked by the assistant, the first author answered on 2026-11-04: «they did not talk» [*«no hablaron»*]. The article maintains that the three ratings were independent on the basis of that confirmation, which comes from the first author and not from the raters. Sheets: `revisiones/revision_{jals_2026-10-29,cdeo_2026-11-04,waag_2026-11-04}.json`
(outside the public repository because they contain personal data).
