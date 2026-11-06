#!/bin/bash
# Espera la extensión (PID 117110), juzga con dos modelos ciegos y analiza.
cd /mnt/990/tmp/steer-qwen35
while kill -0 117110 2>/dev/null; do sleep 30; done
grep -q "FIN" ext.log || { echo "extensión sin FIN" > cadena.err; exit 1; }
nice -n 5 python3 juez.py resultados.json resultados_ext.json --modelo qwen3.6:35b-a3b-coding --salida juez_qwen.jsonl > juez_qwen.log 2>&1
nice -n 5 python3 juez.py resultados.json resultados_ext.json --modelo gemma4:26b --salida juez_gemma.jsonl > juez_gemma.log 2>&1
python3 analisis.py resultados.json resultados_ext.json juez_qwen.jsonl juez_gemma.jsonl > analisis.json 2> analisis.err
echo "$(date +%T) LISTO" > cadena.ok
