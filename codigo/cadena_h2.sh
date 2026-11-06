#!/bin/bash
# Tras la cadena de jueces (cadena.ok), corre H2 sobre activaciones naturales.
cd /mnt/990/tmp/steer-qwen35
while kill -0 127071 2>/dev/null; do sleep 30; done
[ -f cadena.ok ] || { echo "cadena de jueces sin ok" > h2.err; exit 1; }
HF_HOME=/mnt/990/hf nice -n 5 .venv/bin/python activaciones.py resultados.json resultados_ext.json juez_qwen.jsonl juez_gemma.jsonl > activaciones.json 2> activaciones.err
echo "$(date +%T) LISTO" > h2.ok
