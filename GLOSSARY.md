# Glossary

Data keys are built from the Spanish words below, joined by `_` (e.g. `malevolencia_media` = mean malevolence, `n_con_efecto` = number of items in the stratum with some nonzero judge score).

| Word | English |
|---|---|
| `activacion` | activation |
| `activos` | active |
| `acuerdo` | agreement |
| `archivo` | file |
| `base` | unsteered model (condition `base`); also baseline |
| `ceros` | zeros: stratum of outputs both judges scored 0 |
| `coherencia` | coherence (0–4) |
| `colas` | tails (`dos_colas` = two-tailed) |
| `comentario` | comment |
| `completo` | complete |
| `completos` | complete (plural) |
| `con` | with (`con_efecto` = stratum with some nonzero judge score) |
| `condicion` | condition |
| `condiciones` | conditions |
| `consenso` | consensus (mean of the human raters) |
| `controles` | controls |
| `correlaciones` | correlations |
| `criterio` | criterion |
| `cuadratica` | quadratic (weighting of κ) |
| `desvio` | deviation |
| `dos` | two |
| `dosis` | dose |
| `efecto` | effect |
| `emparejada` | matched |
| `en` | in |
| `estado` | status (`ok`, `no_alcanza` = target ΔNLL not reached, `no_monotono` = non-monotonic in dose) |
| `estratos` | strata |
| `evaluador` | rater |
| `evaluadores` | raters |
| `exacto` | exact (agreement) |
| `excluidos` | excluded |
| `exportado` | exported |
| `falsacion` | falsification |
| `falsan` | falsify |
| `faltan` | missing |
| `fase2` | phase 2 |
| `fecha` | date |
| `filas` | rows |
| `frac` | fraction |
| `global` | overall |
| `humana` | human |
| `humano` | human |
| `ic95` | 95% confidence interval |
| `igualan` | equal |
| `iniciado` | started |
| `jueces` | judges |
| `juez` | judge |
| `juicio` | judgement |
| `juzgados` | judged |
| `malev` | malevolence |
| `malevola` | malevolent (score ≥ 2) |
| `malevolencia` | malevolence (0–4) |
| `max` | maximum |
| `media` | mean |
| `mediana` | median |
| `medianas` | medians |
| `min` | minimum |
| `modelo` | model |
| `modo` | mode |
| `natural` | natural (unsteered activations) |
| `neuronas` | neurons |
| `neutro` | neutral (reference text for NLL) |
| `nombre` | name |
| `norma` | norm |
| `o` | or |
| `objetivo` | target |
| `percentil` | percentile |
| `percentiles` | percentiles |
| `por` | per |
| `preregistro` | preregistration |
| `pruebas` | checks |
| `que` | that |
| `rango` | range |
| `receta` | the viral recipe (two-neuron steering) |
| `rejilla` | grid (dose grid) |
| `repeticion` | repetition (`repeticion_4g` = 4-gram repetition rate) |
| `reponderado` | reweighted |
| `resumen` | summary |
| `salidas` | outputs |
| `seg` | seconds |
| `segundos` | seconds |
| `sello` | seal |
| `semilla` | seed |
| `sin` | without |
| `superan` | exceed |
| `tasa` | rate |
| `texto` | text |
| `textos` | texts |
| `validos` | valid |
| `veredicto` | verdict (`DEBILITADO` = weakened) |
| `vs` | versus |

## Condition names

| Name | Meaning |
|---|---|
| `base` | Unsteered model. |
| `tuit d=…` | The viral recipe ("tuit" = tweet): both neurons forced, at dose `d`. |
| `tuit invertido d=…` | The recipe with both signs inverted. |
| `solo L14 N8949 +1`, `solo L13 N… -1` | One neuron of the recipe alone ("solo" = only). |
| `control_N (L14 N… +1, L13 N… -1)` | Random control of the same form and norm, phase 1. |
| `ext_control_NN (…)` | Random control of the same form and norm, extension to 22 controls. |

In `emparejados.json` the controls carry the dose matched in ΔNLL to the recipe (E2).
