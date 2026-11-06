#!/bin/bash
# Full E2 per PREREGISTRO_E2.md: generates with matched doses, judges with
# the two phase-2 judges and applies the sealed criterion. Each step requires the
# previous one to succeed; the failure is recorded in e2.err.
cd /mnt/990/tmp/steer-qwen35
export HF_HOME=/mnt/990/hf
falla() { echo "$(date +%T) $1" > e2.err; exit 1; }

nice -n 5 .venv/bin/python empareja.py --objetivo 1.046 --salida emparejados.json \
    > e2_gen.log 2>&1 || falla "empareja.py rc=$?"
grep -q "FIN" e2_gen.log || falla "generación sin FIN"

python3 e2_para_juez.py emparejados.json --salida e2_condiciones.json \
    > e2_adaptador.log 2>&1 || falla "adaptador rc=$?"

nice -n 5 python3 juez.py e2_condiciones.json --modelo qwen3.6:35b-a3b-coding \
    --salida juez_e2_qwen.jsonl > juez_e2_qwen.log 2>&1 || falla "juez qwen rc=$?"
nice -n 5 python3 juez.py e2_condiciones.json --modelo gemma4:26b \
    --salida juez_e2_gemma.jsonl > juez_e2_gemma.log 2>&1 || falla "juez gemma rc=$?"
# gemma is not a production model: free it so it does not evict the local tier.
curl -s http://127.0.0.1:11434/api/generate -d '{"model":"gemma4:26b","keep_alive":0}' >/dev/null

python3 analisis_e2.py emparejados.json juez_e2_qwen.jsonl juez_e2_gemma.jsonl \
    --fase2 juez_qwen.jsonl juez_gemma.jsonl --salida analisis_e2.json \
    > analisis_e2.log 2>&1 || falla "analisis_e2 rc=$?"
echo "$(date +%T) LISTO" > e2.ok
