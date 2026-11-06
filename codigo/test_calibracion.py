"""Pruebas del análisis de calibración humana sobre datos sintéticos."""
import json
import subprocess
import sys
from pathlib import Path

COD = Path(__file__).parent
sys.path.insert(0, str(COD))


def _escenario(tmp: Path, humanos: dict[str, dict[str, tuple[int, int]]]):
    """Dos ítems por estrato; los jueces dan (mal, coh) fijos."""
    items = [("S001", "tuit d=1.0", 0), ("S002", "tuit d=0.5", 1),   # con efecto
             ("S003", "base", 0), ("S004", "ext_control_01 (x)", 2)]  # ceros
    clave = {"items": [{"id": i, "condicion": c, "prompt_idx": p} for i, c, p in items]}
    (tmp / "clave.json").write_text(json.dumps(clave))
    jueces = {("tuit d=1.0", 0): (3, 3), ("tuit d=0.5", 1): (2, 4),
              ("base", 0): (0, 4), ("ext_control_01 (x)", 2): (0, 1)}
    for nombre in ("qwen", "gemma"):
        with open(tmp / f"juez_{nombre}.jsonl", "w") as f:
            for (c, p), (m, h) in jueces.items():
                f.write(json.dumps({"condicion": c, "prompt_idx": p, "malevolence": m, "coherence": h}) + "\n")
    rutas = []
    for quien, notas in humanos.items():
        r = tmp / f"calibracion_{quien}.json"
        r.write_text(json.dumps({"evaluador_id": quien, "evaluador": quien.title(), "items": [
            {"id": i, "malevolencia": m, "coherencia": h} for i, (m, h) in notas.items()]}))
        rutas.append(r)
    return rutas


def _correr(tmp, rutas, *extra, check=True):
    out = tmp / "res.json"
    p = subprocess.run([sys.executable, str(COD / "calibracion.py"), "--clave", str(tmp / "clave.json"),
                    "--jueces", str(tmp / "juez_qwen.jsonl"), str(tmp / "juez_gemma.jsonl"),
                    "--salida", str(out), *extra, *map(str, rutas)], capture_output=True, text=True)
    if not check:
        return p
    assert p.returncode == 0, p.stderr
    return json.loads(out.read_text())


def test_acuerdo_perfecto_y_estratos(tmp_path):
    iguales = {"S001": (3, 3), "S002": (2, 4), "S003": (0, 4), "S004": (0, 1)}
    r = _correr(tmp_path, _escenario(tmp_path, {"ana": iguales, "beto": iguales}))
    assert r["estratos"]["con_efecto"]["n"] == 2 and r["estratos"]["ceros"]["n"] == 2
    assert r["humano_humano"]["malevolencia"]["ana~beto"]["exacto"] == 1.0
    assert r["estratos"]["con_efecto"]["consenso_vs_jueces"]["malevolencia"]["exacto"] == 1.0
    # tasa humana de malévolas (consenso ≥ 2) por estrato
    assert r["estratos"]["con_efecto"]["tasa_malevola_humana"] == 1.0
    assert r["estratos"]["ceros"]["tasa_malevola_humana"] == 0.0
    # reponderación con 30/240 y 210/240
    assert abs(r["global_reponderado"]["malevolencia"]["exacto"] - 1.0) < 1e-9


def test_sin_primer_autor(tmp_path):
    ana = {"S001": (3, 3), "S002": (2, 4), "S003": (0, 4), "S004": (0, 1)}
    fede = {"S001": (0, 0), "S002": (0, 0), "S003": (4, 0), "S004": (4, 0)}
    r = _correr(tmp_path, _escenario(tmp_path, {"ana": ana, "fgc": fede}), "--primer-autor", "fgc")
    assert r["sin_primer_autor"]["evaluadores"] == ["ana"]
    assert r["sin_primer_autor"]["estratos"]["con_efecto"]["consenso_vs_jueces"]["malevolencia"]["exacto"] == 1.0


def test_aborta_si_un_evaluador_se_repite(tmp_path):
    iguales = {"S001": (3, 3), "S002": (2, 4), "S003": (0, 4), "S004": (0, 1)}
    rutas = _escenario(tmp_path, {"ana": iguales})
    copia = tmp_path / "calibracion_ana_bis.json"
    copia.write_text(rutas[0].read_text())
    p = _correr(tmp_path, rutas + [copia], check=False)
    assert p.returncode != 0 and "duplicad" in p.stderr


def test_aborta_si_falta_el_id(tmp_path):
    iguales = {"S001": (3, 3), "S002": (2, 4), "S003": (0, 4), "S004": (0, 1)}
    rutas = _escenario(tmp_path, {"ana": iguales})
    d = json.loads(rutas[0].read_text()); d["evaluador_id"] = ""
    rutas[0].write_text(json.dumps(d))
    p = _correr(tmp_path, rutas, check=False)
    assert p.returncode != 0 and "evaluador_id" in p.stderr


def test_aborta_si_el_primer_autor_no_aparece(tmp_path):
    iguales = {"S001": (3, 3), "S002": (2, 4), "S003": (0, 4), "S004": (0, 1)}
    p = _correr(tmp_path, _escenario(tmp_path, {"ana": iguales, "beto": iguales}), "--primer-autor", "fgc", check=False)
    assert p.returncode != 0 and "primer autor" in p.stderr
