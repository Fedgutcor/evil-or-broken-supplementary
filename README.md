# Supplementary material: "Evil or Broken? Auditing a Viral Activation-Steering Recipe, and What the Episode Teaches About Open-Weight Governance"

Federico Gutiérrez-Correa, Jerri Alejandro López-Sánchez, Cristian David Echeverri-Ocampo,
Wilson Andrés Araque Garzón. Submitted to the *Journal of Artificial Intelligence Research*, November 2026.

This package contains what the article's *Data and code availability* statement lists.
**Raw steered outputs are not included**: following the disclosure norm in Section 6.4, they are
shared with researchers on request (contacto@scirepopuli.com).

## Contents

| Path | What it is |
|---|---|
| `codigo/` | Generation (`steer.py`, `empareja.py`), judging (`juez.py`), analysis (`analisis.py`, `analisis_e2.py`, `activaciones.py`), human calibration (`planilla_humana.py`, `planilla_plantilla.html`, `calibracion.py`, `test_calibracion.py`), the E2 adapter (`e2_para_juez.py`), the run chains as executed (`cadena_*.sh`), and `armar_suplementario.py`, which built this package. |
| `datos/juez_*.jsonl` | Per-output judge scores (malevolence, coherence) from both judges, phase 2 and E2. |
| `datos/resultados*.json`, `datos/emparejados.json`, `datos/e2_condiciones.json` | Generation results: conditions, doses, neutral-text NLL, tokens, time and 4-gram repetition per output. Each output's text is replaced by `texto_sha256`, the SHA-256 of its UTF-8 text, so outputs received on request can be checked against the ones analysed. |
| `datos/*.log` | Run logs. The output excerpt printed after ` | ` is replaced by `[output omitted; available on request]`; everything else is unchanged. |
| `datos/analisis.json`, `datos/analisis_e2.json`, `datos/activaciones.json` | Analysis outputs reported in the article. |
| `datos/clave_calibracion.json` | The sealed human-calibration sample: seed, SHA-256 of the item list, and the key from item id to condition and prompt. |
| `datos/calibracion/` | The three raters' sheets, unmodified. |
| `datos/calibracion_resultado.json` | Calibration analysis output. |
| `PREREGISTRO_E2.md`, `SELLO_E2.txt` | E2 preregistration and its seal (commit and SHA-256). |
| `ENMIENDA_CALIBRACION.md` | The calibration amendment, with the SHA-256 of each rater sheet. |
| `PREREGISTRO_E2_en.md`, `ENMIENDA_CALIBRACION_en.md` | English translations of the two documents above. The Spanish originals are the sealed, authoritative versions. |
| `GLOSSARY.md` | English meaning of every Spanish word used in the data keys, condition names and status values. |

## What can be verified from this package alone

From `datos/`:

```
python ../codigo/analisis.py resultados.json resultados_ext.json juez_qwen.jsonl juez_gemma.jsonl
python ../codigo/analisis_e2.py emparejados.json juez_e2_qwen.jsonl juez_e2_gemma.jsonl \
    --fase2 juez_qwen.jsonl juez_gemma.jsonl --salida analisis_e2.json
python ../codigo/calibracion.py --clave clave_calibracion.json --jueces juez_qwen.jsonl juez_gemma.jsonl \
    calibracion/*.json --salida calibracion_resultado.json
```

These reproduce `analisis.json`, `analisis_e2.json` and `calibracion_resultado.json` exactly
(standard library only). The SHA-256 of `PREREGISTRO_E2.md` matches `SELLO_E2.txt`, and the
SHA-256 of each rater sheet matches `ENMIENDA_CALIBRACION.md`. `SHA256SUMS` covers every file.

## What needs the raw outputs (on request)

Judging (`juez.py`), the activation analysis (`activaciones.py`), rebuilding the rating sheet
(`planilla_humana.py`) and checking the calibration sample's SHA-256 (`sha256_items`, computed over
the item texts) need the steered outputs. Regenerating them needs the model (Qwen/Qwen3.5-4B, bf16),
PyTorch and Transformers; the environment is described in the article's Appendix C. The judges ran
through Ollama (`qwen3.6:35b-a3b-coding`, `gemma4:26b`). The run chains (`cadena_*.sh`) show the
order and paths used on the authors' machine.

## Language

Comments, docstrings and command-line help in `codigo/` are in English. Identifiers, file names,
data keys and runtime messages are kept in Spanish, as they were when the experiments ran: the
article cites the file names, the data files were written with those keys, the run chains look
for messages in the logs (e.g. `FIN`), and renaming any of them would make the archived code
differ from the code that produced the results. The translation changed no code: the syntax tree
of every script, with docstrings and help texts excluded, is identical before and after.
`GLOSSARY.md` gives the English meaning of every Spanish word in the data keys. The rating sheet
template (`planilla_plantilla.html`) is kept in Spanish, the language the raters used.

## Licences

Code: MIT (`LICENSE`). Data and documents: CC BY 4.0 (`LICENSE-DATA.md`).
