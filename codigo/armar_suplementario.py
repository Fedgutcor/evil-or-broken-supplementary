"""Builds the article's supplementary material without publishing any steered output.

The article (§6.4 and the data statement) promises code, per-output scores,
run logs, the pre-registration with its seal, the sealed calibration sample,
the raters' sheets and the amendment; raw outputs are shared only on
request. This script enforces that boundary:

- Only what INCLUIDOS names goes in (an inclusion list, not an exclusion list).
- In the results, each `texto` is replaced by its `texto_sha256`: whoever receives
  the raw outputs can check that they are the ones that were analysed.
- In the logs, the output excerpt that follows ` | ` is replaced by a marker.
- Pre-registration, seal, amendment and sheets are copied byte for byte, so that the hashes
  cited in the article keep verifying.
- Aborts if a single output fragment remains in the package.

    python armar_suplementario.py ../dist/suplementario
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

CODIGO = ["steer.py", "juez.py", "analisis.py", "activaciones.py", "empareja.py", "analisis_e2.py",
          "planilla_humana.py", "calibracion.py", "test_calibracion.py", "e2_para_juez.py",
          "planilla_plantilla.html", "cadena_juez.sh", "cadena_h2.sh", "cadena_e2.sh",
          "armar_suplementario.py"]
RESULTADOS = ["resultados.json", "resultados_ext.json", "emparejados.json", "e2_condiciones.json"]
REGISTROS = ["smoke.log", "full.log", "ext.log", "e2_gen.log"]
DATOS_TAL_CUAL = ["juez_qwen.jsonl", "juez_gemma.jsonl", "juez_e2_qwen.jsonl", "juez_e2_gemma.jsonl",
                  "analisis.json", "analisis_e2.json", "activaciones.json", "clave_calibracion.json",
                  "calibracion_resultado.json", "calibracion/calibracion_cdeo_2026-10-28.json",
                  "calibracion/calibracion_jals_2026-10-29.json", "calibracion/calibracion_waag_2026-11-01.json"]
DOCUMENTOS = ["PREREGISTRO_E2.md", "SELLO_E2.txt", "ENMIENDA_CALIBRACION.md",
              "PREREGISTRO_E2_en.md", "ENMIENDA_CALIBRACION_en.md"]

# Spanish words that make up the keys of the data files, with their English meaning.
GLOSARIO = {
    "activacion": "activation", "activos": "active", "acuerdo": "agreement", "archivo": "file",
    "base": "unsteered model (condition `base`); also baseline", "ceros": "zeros: stratum of outputs both judges scored 0",
    "coherencia": "coherence (0–4)", "colas": "tails (`dos_colas` = two-tailed)", "comentario": "comment",
    "completo": "complete", "completos": "complete (plural)","con": "with (`con_efecto` = stratum with some nonzero judge score)",
    "condicion": "condition", "condiciones": "conditions", "consenso": "consensus (mean of the human raters)",
    "controles": "controls", "correlaciones": "correlations", "criterio": "criterion",
    "cuadratica": "quadratic (weighting of κ)", "desvio": "deviation", "dos": "two", "dosis": "dose",
    "efecto": "effect", "emparejada": "matched", "en": "in", "estado": "status (`ok`, `no_alcanza` = target ΔNLL "
    "not reached, `no_monotono` = non-monotonic in dose)", "estratos": "strata", "evaluador": "rater",
    "evaluadores": "raters", "exacto": "exact (agreement)", "excluidos": "excluded", "exportado": "exported",
    "falsacion": "falsification", "falsan": "falsify", "faltan": "missing", "fase2": "phase 2", "fecha": "date",
    "filas": "rows", "frac": "fraction", "global": "overall", "humano": "human", "humana": "human",
    "ic95": "95% confidence interval", "igualan": "equal", "iniciado": "started", "jueces": "judges",
    "juez": "judge", "juicio": "judgement", "juzgados": "judged", "malev": "malevolence",
    "malevola": "malevolent (score ≥ 2)", "malevolencia": "malevolence (0–4)", "max": "maximum",
    "media": "mean", "mediana": "median", "medianas": "medians", "min": "minimum", "modelo": "model",
    "modo": "mode", "natural": "natural (unsteered activations)", "neuronas": "neurons",
    "neutro": "neutral (reference text for NLL)", "nombre": "name", "norma": "norm",
    "o": "or", "objetivo": "target", "percentil": "percentile", "percentiles": "percentiles",
    "por": "per", "preregistro": "preregistration", "pruebas": "checks", "que": "that", "rango": "range",
    "receta": "the viral recipe (two-neuron steering)", "rejilla": "grid (dose grid)",
    "repeticion": "repetition (`repeticion_4g` = 4-gram repetition rate)", "reponderado": "reweighted",
    "resumen": "summary", "salidas": "outputs", "seg": "seconds", "segundos": "seconds", "sello": "seal",
    "semilla": "seed", "sin": "without", "superan": "exceed", "tasa": "rate", "texto": "text",
    "textos": "texts", "validos": "valid", "veredicto": "verdict (`DEBILITADO` = weakened)", "vs": "versus",
}
# Tokens that are English, symbols or proper names.
NEUTRAS = {"4g", "abs", "coherence", "control", "delta", "final", "empirico", "gemma", "ge2", "id", "idx", "items",
           "kappa", "malevolence", "n", "new", "nll", "p", "p01", "p50", "p99", "prompt", "prompts", "qwen", "rho",
           "sd", "sha256", "sheet", "spearman", "specs", "tokens", "w", "l13", "l14"}

INCLUIDOS = ([f"codigo/{n}" for n in CODIGO] + [f"datos/{n}" for n in RESULTADOS + REGISTROS + DATOS_TAL_CUAL]
             + DOCUMENTOS)
GENERADOS = ["README.md", "GLOSSARY.md", "LICENSE", "LICENSE-DATA.md", "CITATION.cff", "SHA256SUMS"]

MARCA = "[output omitted; available on request]"
_FRAGMENTO = re.compile(r"( \| )(['\"]).*$")          # "  p1: 119 tok 43s | 'texto…'"
_MUESTRA = re.compile(r"^(\S+ muestra [^:]*: ).*$")     # "19:23:18 muestra base: texto…"
_PREFIJO = 30


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def quitar_textos(resultado: dict) -> dict:
    """Copy of the result with each salida['texto'] replaced by its SHA-256."""
    r = json.loads(json.dumps(resultado))
    for cond in r.get("condiciones", []) + r.get("controles", []):
        for s in cond.get("salidas", []):
            texto = s.pop("texto")
            s["texto_sha256"] = _sha(texto.encode("utf-8"))
    return r


def limpiar_registro(texto: str) -> str:
    return "\n".join(_MUESTRA.sub(rf"\1{MARCA}", _FRAGMENTO.sub(rf"\1{MARCA}", l)) for l in texto.split("\n"))


def prompts(repo: Path) -> set[str]:
    """The eight prompts are public (Appendix B): an output that repeats them is not a leak."""
    out: set[str] = set()
    for n in RESULTADOS:
        out |= set(json.loads((repo / "datos" / n).read_text(encoding="utf-8"))["prompts"])
    return out


def textos_crudos(repo: Path) -> list[str]:
    out = []
    for n in RESULTADOS:
        r = json.loads((repo / "datos" / n).read_text(encoding="utf-8"))
        for cond in r.get("condiciones", []) + r.get("controles", []):
            out += [s["texto"] for s in cond.get("salidas", [])]
    return out


def _sondas(textos: list[str], publicos: set[str]) -> set[str]:
    """Prefixes of each output, raw and escaped as repr() prints them in the logs,
    except those that are part of a public prompt (degraded outputs that repeat the question)."""
    sondas = set()
    for t in textos:
        for forma in (t, repr(t)[1:-1]):
            p = forma.strip()[:_PREFIJO]
            if len(p) >= 15 and not any(p in q for q in publicos):
                sondas.add(p)
    return sondas


def fugas(raiz: Path, textos: list[str], publicos: set[str] = frozenset()) -> list[tuple[str, str]]:
    """(file, prefix) for each output fragment found under `raiz`."""
    sondas = _sondas(textos, publicos)
    halladas = []
    for p in sorted(raiz.rglob("*")):
        if not p.is_file():
            continue
        contenido = p.read_text(encoding="utf-8", errors="ignore")
        halladas += [(p.relative_to(raiz).as_posix(), s) for s in sondas if s in contenido]
    return halladas


README = """# Supplementary material: "Evil or Broken? Auditing a Viral Activation-Steering Recipe, and What the Episode Teaches About Open-Weight Governance"

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
| `datos/*.log` | Run logs. The output excerpt printed after ` | ` is replaced by `{marca}`; everything else is unchanged. |
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
python ../codigo/analisis_e2.py emparejados.json juez_e2_qwen.jsonl juez_e2_gemma.jsonl \\
    --fase2 juez_qwen.jsonl juez_gemma.jsonl --salida analisis_e2.json
python ../codigo/calibracion.py --clave clave_calibracion.json --jueces juez_qwen.jsonl juez_gemma.jsonl \\
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
"""

MIT = """MIT License

Copyright (c) 2026 Federico Gutiérrez-Correa, Jerri Alejandro López-Sánchez, Cristian David Echeverri-Ocampo, Wilson Andrés Araque Garzón

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

CC_BY = """# Data and documents licence

Everything in this package outside `codigo/` (the files under `datos/`, the preregistration, its
seal, the amendment, their English translations, `README.md` and `GLOSSARY.md`) is licensed under the
Creative Commons Attribution 4.0 International License (CC BY 4.0):
https://creativecommons.org/licenses/by/4.0/legalcode

Attribution: cite the article and this package (see `CITATION.cff`).
"""

CITATION = """cff-version: 1.2.0
message: "If you use this material, please cite the article and this package."
title: "Supplementary material: Evil or Broken? Auditing a Viral Activation-Steering Recipe, and What the Episode Teaches About Open-Weight Governance"
type: dataset
license: CC-BY-4.0
authors:
  - family-names: "Gutiérrez-Correa"
    given-names: "Federico"
    orcid: "https://orcid.org/0000-0003-4030-989X"
    affiliation: "Scire Populi S.A.S."
  - family-names: "López-Sánchez"
    given-names: "Jerri Alejandro"
    orcid: "https://orcid.org/0000-0001-5965-3469"
    affiliation: "Universidad El Bosque; Universidad EAFIT"
  - family-names: "Echeverri-Ocampo"
    given-names: "Cristian David"
    orcid: "https://orcid.org/0000-0002-7508-1488"
    affiliation: "Universidad de Antioquia"
  - family-names: "Araque Garzón"
    given-names: "Wilson Andrés"
    orcid: "https://orcid.org/0009-0004-2316-796X"
    affiliation: "Scire Populi S.A.S."
date-released: "2026-11-05"
"""


CONDICIONES = """## Condition names

| Name | Meaning |
|---|---|
| `base` | Unsteered model. |
| `tuit d=…` | The viral recipe ("tuit" = tweet): both neurons forced, at dose `d`. |
| `tuit invertido d=…` | The recipe with both signs inverted. |
| `solo L14 N8949 +1`, `solo L13 N… -1` | One neuron of the recipe alone ("solo" = only). |
| `control_N (L14 N… +1, L13 N… -1)` | Random control of the same form and norm, phase 1. |
| `ext_control_NN (…)` | Random control of the same form and norm, extension to 22 controls. |

In `emparejados.json` the controls carry the dose matched in ΔNLL to the recipe (E2).
"""


def glosario() -> str:
    filas = "\n".join(f"| `{t}` | {s} |" for t, s in sorted(GLOSARIO.items()))
    return ("# Glossary\n\nData keys are built from the Spanish words below, joined by `_` "
            "(e.g. `malevolencia_media` = mean malevolence, `n_con_efecto` = number of items in the stratum "
            "with some nonzero judge score).\n\n| Word | English |\n|---|---|\n" + filas + "\n\n" + CONDICIONES)


def armar(repo: Path, destino: Path) -> Path:
    if destino.exists():
        shutil.rmtree(destino)
    for rel in INCLUIDOS:
        origen = repo / rel
        dst = destino / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        nombre = Path(rel).name
        if rel.startswith("datos/") and nombre in RESULTADOS:
            r = quitar_textos(json.loads(origen.read_text(encoding="utf-8")))
            dst.write_text(json.dumps(r, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        elif rel.startswith("datos/") and nombre in REGISTROS:
            dst.write_text(limpiar_registro(origen.read_text(encoding="utf-8")), encoding="utf-8")
        else:
            shutil.copyfile(origen, dst)
    (destino / "README.md").write_text(README.replace("{marca}", MARCA), encoding="utf-8")
    (destino / "GLOSSARY.md").write_text(glosario(), encoding="utf-8")
    (destino / "LICENSE").write_text(MIT, encoding="utf-8")
    (destino / "LICENSE-DATA.md").write_text(CC_BY, encoding="utf-8")
    (destino / "CITATION.cff").write_text(CITATION, encoding="utf-8")

    quedan = fugas(destino, textos_crudos(repo), prompts(repo))
    if quedan:
        shutil.rmtree(destino)
        raise SystemExit(f"ABORTA: {len(quedan)} fragmentos de salida en el paquete, p. ej. {quedan[:3]}")

    sumas = [f"{_sha(p.read_bytes())}  {p.relative_to(destino).as_posix()}"
             for p in sorted(destino.rglob("*")) if p.is_file()]
    (destino / "SHA256SUMS").write_text("\n".join(sumas) + "\n", encoding="utf-8")
    return destino


def main() -> int:
    repo = Path(__file__).resolve().parent.parent
    destino = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else repo / "dist" / "suplementario"
    armar(repo, destino)
    zip_ = shutil.make_archive(str(destino), "zip", destino.parent, destino.name)
    print("ok", destino, zip_)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
