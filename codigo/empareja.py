"""E2: la dosis de cada control se ajusta hasta igualar la degradación de la receta.

El reproche al diseño de la fase 2 es que sus controles, todos a dosis 1, salen
mucho más rotos que la receta (coherencia mediana 0,72 contra 2,19), y un texto
roto no puede puntuar alto en malevolencia. Acá cada control recibe la dosis que
iguala su Δ NLL al de la receta, y recién entonces se compara.

Reusa `steer.py` entero: misma intervención, mismos prompts, mismo texto neutro.
Plan y criterio de decisión: `PREREGISTRO_E2.md`, sellado antes de esta corrida.

    python empareja.py --objetivo 1.046 --salida emparejados.json
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time

import torch

import steer as S

#: Rejilla de monotonía: si Δ NLL no crece con la dosis, la bisección no sirve.
REJILLA = (0.02, 0.25, 0.5, 0.75, 1.0)
TOLERANCIA = 0.02
MAX_ITER = 12
D_MIN, D_MAX = 0.02, 1.0


def controles_de_la_fase2():
    """Los MISMOS 22 pares: 2 de `condiciones()` y 20 de `controles_extension()`."""
    rng = random.Random(20261025)
    dos = [(n, sp) for n, sp in S.condiciones(rng) if n.startswith("control_")]
    assert len(dos) == 2, dos
    return dos + S.controles_extension(20)


def delta_nll(model, texto_ids, specs, dose, med, base_nll):
    """Δ NLL del control a esa dosis, sobre el texto neutro."""
    con_dosis = [(L, n, (dose if s > 0 else -dose)) for L, n, s in specs]
    return S.nll(model, texto_ids, S.resolver(model, con_dosis, med)) - base_nll


def dosis_que_iguala(model, texto_ids, specs, med, base_nll, objetivo, log):
    """Dosis cuyo Δ NLL alcanza `objetivo`. Devuelve (dosis, delta, estado, rejilla)."""
    barrido = [(d, delta_nll(model, texto_ids, specs, d, med, base_nll)) for d in REJILLA]
    log("    rejilla:", [(d, round(v, 3)) for d, v in barrido])
    crece = all(b[1] >= a[1] - 1e-6 for a, b in zip(barrido, barrido[1:]))
    estado = "ok" if crece else "no_monotono"

    if barrido[-1][1] < objetivo:
        # Ni a dosis 1 degrada tanto como la receta: no se puede emparejar hacia arriba.
        return D_MAX, barrido[-1][1], "no_alcanza", barrido
    if barrido[0][1] > objetivo:
        return D_MIN, barrido[0][1], "no_alcanza_por_abajo", barrido

    lo = max(d for d, v in barrido if v <= objetivo)
    hi = min(d for d, v in barrido if v >= objetivo)
    for _ in range(MAX_ITER):
        mid = (lo + hi) / 2
        v = delta_nll(model, texto_ids, specs, mid, med, base_nll)
        if abs(v - objetivo) <= TOLERANCIA:
            return mid, v, estado, barrido
        if v < objetivo:
            lo = mid
        else:
            hi = mid
    mid = (lo + hi) / 2
    return mid, delta_nll(model, texto_ids, specs, mid, med, base_nll), "sin_converger", barrido


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--objetivo", type=float, required=True,
                    help="Δ NLL a igualar (1.046 = receta a d=1)")
    ap.add_argument("--salida", default="emparejados.json")
    ap.add_argument("--hilos", type=int, default=10)
    ap.add_argument("--solo-dosis", action="store_true",
                    help="buscar las dosis y salir, sin generar")
    a = ap.parse_args()

    torch.set_num_threads(a.hilos)
    S.log("cargando", S.MODEL, "hilos", a.hilos)
    tok, model = S.cargar()
    S.log("cargado · objetivo Δ NLL =", a.objetivo)

    prompts_ids = [S.chat_ids(tok, p) for p in S.PROMPTS]
    texto_ids = tok(S.TEXTO_NEUTRO, return_tensors="pt").input_ids

    por_prompt = []
    for ids in prompts_ids + [texto_ids]:
        m = S.medianas(model, ids, (13, 14))
        por_prompt.append({L: v.median().item() for L, v in m.items()})
    med_texto = por_prompt[-1]

    base_nll = S.nll(model, texto_ids, [])
    S.log("NLL base del texto neutro:", round(base_nll, 4))

    res = {"objetivo_delta_nll": a.objetivo, "base_nll": base_nll,
           "modelo": S.MODEL, "max_new_tokens": S.MAX_NEW, "modo_mediana": "prompt",
           "preregistro": "PREREGISTRO_E2.md", "prompts": S.PROMPTS,
           "medianas_por_prompt": por_prompt, "controles": []}

    t0 = time.time()
    for nombre, specs in controles_de_la_fase2():
        S.log("control:", nombre)
        dose, delta, estado, barrido = dosis_que_iguala(
            model, texto_ids, specs, med_texto, base_nll, a.objetivo, S.log)
        S.log(f"    dosis={dose:.4f} ΔNLL={delta:.3f} estado={estado}")
        fila = {"nombre": nombre, "specs": specs, "dosis_emparejada": dose,
                "delta_nll": delta, "estado": estado,
                "rejilla": [{"dosis": d, "delta_nll": v} for d, v in barrido],
                "salidas": []}
        res["controles"].append(fila)
        with open(a.salida, "w") as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
    S.log("dosis listas en", round(time.time() - t0), "s")

    if a.solo_dosis:
        return 0

    # Generación: solo los controles que alcanzaron el objetivo. Un excluido se
    # declara en el JSON, no se reemplaza (pre-registro §2).
    for fila in res["controles"]:
        if fila["estado"].startswith("no_alcanza"):
            S.log("excluido de la generación:", fila["nombre"], fila["estado"])
            continue
        S.log("generando:", fila["nombre"], f"d={fila['dosis_emparejada']:.4f}")
        d = fila["dosis_emparejada"]
        con_dosis = [(L, n, (d if s > 0 else -d)) for L, n, s in fila["specs"]]
        for i, ids in enumerate(prompts_ids):
            texto, n, dt, _ = S.generar(model, tok, ids,
                                        S.resolver(model, con_dosis, por_prompt[i]))
            fila["salidas"].append({"texto": texto, "tokens": n, "seg": round(dt, 1),
                                    "repeticion_4g": S.repetitivo(texto)})
            S.log(f"  p{i + 1}: {n} tok {dt:.0f}s")
        with open(a.salida, "w") as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
    S.log("FIN", round((time.time() - t0) / 60), "min")
    return 0


if __name__ == "__main__":
    sys.exit(main())
