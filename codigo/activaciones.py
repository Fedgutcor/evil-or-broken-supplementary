"""H2 (pre-registrada 2026-10-25 ~23:10, antes de ver la fase 2): ¿la neurona
REPRESENTA el rasgo, además de dirigirlo?

Sin intervención, se lee cada salida del experimento (prompt + respuesta con
la plantilla de chat) y se registra la activación natural (entrada de
down_proj) de L14 N8949 y L13 N7956, promediada sobre los tokens de la
respuesta. Se correlaciona (Spearman) con la malevolencia media de los dos
jueces. Nula: la misma correlación para las neuronas de los 22 controles al
azar (L14 y L13), que no deberían representar el rasgo.

También se reporta el rango natural de activación de las neuronas dirigidas
sobre todos los tokens leídos, para situar el coeficiente c ≈ 22,8 de d = 1.

    .venv/bin/python activaciones.py resultados.json resultados_ext.json juez_qwen.jsonl juez_gemma.jsonl > activaciones.json
"""
import json
import re
import sys

import torch

sys.path.insert(0, ".")
from steer import MODEL, cargar, down_proj  # noqa: E402

OBJETIVO = {14: 8949, 13: 7956}


def textos(rutas_res):
    out = []
    for ruta in rutas_res:
        r = json.load(open(ruta))
        for c in r["condiciones"]:
            for i, s in enumerate(c["salidas"]):
                out.append((c["nombre"], i, r["prompts"][i], s["texto"]))
    return out


def neuronas_control(rutas_res):
    por_capa = {14: set(), 13: set()}
    for ruta in rutas_res:
        for c in json.load(open(ruta))["condiciones"]:
            if c["nombre"].startswith(("control_", "ext_control_")):
                for L, n, _ in c["specs"]:
                    por_capa[L].add(n)
    return {L: sorted(v) for L, v in por_capa.items()}


def malevolencia(rutas_juez):
    notas = {}
    for ruta in rutas_juez:
        for l in open(ruta):
            d = json.loads(l)
            notas.setdefault((d["condicion"], d["prompt_idx"]), []).append(d["malevolence"])
    return {k: sum(v) / len(v) for k, v in notas.items() if len(v) == len(rutas_juez)}


def spearman(a, b):
    def rangos(v):
        orden = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[orden[j + 1]] == v[orden[i]]:
                j += 1
            for t in range(i, j + 1):
                r[orden[t]] = (i + j) / 2 + 1
            i = j + 1
        return r
    ra, rb = rangos(a), rangos(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return num / den if den else float("nan")


@torch.no_grad()
def main():
    res = [a for a in sys.argv[1:] if a.endswith(".json")]
    jz = [a for a in sys.argv[1:] if a.endswith(".jsonl")]
    torch.set_num_threads(10)
    tok, model = cargar()
    ctl = neuronas_control(res)
    vigiladas = {L: [OBJETIVO[L]] + [n for n in ctl[L] if n != OBJETIVO[L]] for L in (13, 14)}
    captura = {}
    handles = []
    for L in (13, 14):
        def hook(mod, args, L=L):
            captura[L] = args[0][0].float()  # (tokens, d_ff)
        handles.append(down_proj(model, L).register_forward_pre_hook(hook))

    filas, todas_obj = [], {13: [], 14: []}
    for nombre, i, prompt, texto in textos(res):
        pre = tok.apply_chat_template([{"role": "user", "content": prompt}], add_generation_prompt=True,
                                      enable_thinking=False, tokenize=False)
        ids_pre = tok(pre, return_tensors="pt").input_ids
        ids = tok(pre + texto, return_tensors="pt").input_ids
        if ids.shape[1] <= ids_pre.shape[1]:
            continue
        model(input_ids=ids)
        desde = ids_pre.shape[1]
        fila = {"condicion": nombre, "prompt_idx": i}
        for L in (13, 14):
            a = captura[L][desde:]
            fila[f"L{L}"] = {str(n): round(a[:, n].mean().item(), 5) for n in vigiladas[L]}
            todas_obj[L].extend(a[:, OBJETIVO[L]].tolist())
        filas.append(fila)
    for h in handles:
        h.remove()

    mal = malevolencia(jz)
    pares = [(f, mal[(f["condicion"], f["prompt_idx"])]) for f in filas if (f["condicion"], f["prompt_idx"]) in mal]
    m = [p[1] for p in pares]
    out = {"modelo": MODEL, "textos": len(filas), "con_juicio": len(pares), "correlaciones": {}}
    for L in (13, 14):
        rho = {n: spearman([p[0][f"L{L}"][str(n)] for p in pares], m) for n in vigiladas[L]}
        obj = rho[OBJETIVO[L]]
        nulos = [v for n, v in rho.items() if n != OBJETIVO[L]]
        # dos colas: |rho| del objetivo contra |rho| de las neuronas control
        mayores = sum(abs(v) >= abs(obj) for v in nulos)
        vals = sorted(todas_obj[L])
        pct = lambda q: vals[min(len(vals) - 1, int(q * len(vals)))]
        out["correlaciones"][f"L{L} N{OBJETIVO[L]}"] = {
            "spearman_con_malevolencia": round(obj, 3),
            "n_neuronas_control": len(nulos),
            "p_empirico_dos_colas": round((1 + mayores) / (1 + len(nulos)), 4),
            "rho_controles_media": round(sum(nulos) / len(nulos), 3),
            "rho_controles_rango": [round(min(nulos), 3), round(max(nulos), 3)],
            "activacion_natural_percentiles": {"p01": round(pct(0.01), 3), "p50": round(pct(0.5), 3),
                                               "p99": round(pct(0.99), 3), "max_abs": round(max(abs(vals[0]), abs(vals[-1])), 3)},
        }
    out["filas"] = filas
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
