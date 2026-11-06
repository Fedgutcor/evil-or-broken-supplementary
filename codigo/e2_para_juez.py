"""E2: converts the output of `empareja.py` to the format that `juez.py` reads.

`empareja.py` stores the controls under `controles`; `juez.py` reads `condiciones`.
This adapter only renames: it does not touch texts, prompts or the judge, which the
pre-registration fixes. `no_alcanza` controls have no outputs and are not passed on.

    python e2_para_juez.py emparejados.json --salida e2_condiciones.json
"""
from __future__ import annotations

import argparse
import json


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("emparejados")
    ap.add_argument("--salida", default="e2_condiciones.json")
    a = ap.parse_args()

    r = json.load(open(a.emparejados, encoding="utf-8"))
    condiciones = [{"nombre": c["nombre"], "salidas": c["salidas"]}
                   for c in r["controles"]
                   if not c["estado"].startswith("no_alcanza") and c["salidas"]]
    with open(a.salida, "w", encoding="utf-8") as f:
        json.dump({"prompts": r["prompts"], "condiciones": condiciones},
                  f, ensure_ascii=False, indent=1)
    print(f"{len(condiciones)} controles, "
          f"{sum(len(c['salidas']) for c in condiciones)} salidas -> {a.salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
