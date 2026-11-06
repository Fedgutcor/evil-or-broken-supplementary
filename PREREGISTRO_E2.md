# Pre-registro E2 — controles emparejados en degradación

**Fecha de redacción:** 2026-10-26, antes de ejecutar cualquier corrida de E2.
**Autor:** Federico Gutiérrez-Correa (Scire Populi S.A.S.).
**Estado de los datos al escribir esto:** solo existen los de la fase 1 y 2 (ya publicados en el borrador 2). No se ha generado ninguna salida con dosis emparejada.
**Sello:** este archivo se commitea en un repositorio git local antes de la primera corrida; el hash del commit y el SHA-256 del archivo quedan en `SELLO_E2.txt`. **No hay sello de un tercero** (OSF u otro), y se declarará así en el paper.

## 1. Objeción que responde

El borrador 2 afirma que el efecto no es daño genérico, pero sus 22 controles son mucho menos coherentes que la receta (mediana 0,72 frente a 2,19) porque todos se corrieron a dosis 1, que para esas neuronas degrada más. Un texto incoherente no puede recibir una calificación alta de malevolencia, así que la comparación favorece a la receta. E2 elimina ese desemparejamiento.

## 2. Diseño

**Emparejamiento.** Para cada uno de los 22 pares de control ya usados (las mismas neuronas, reproducidas con las semillas 20261025 y 20261026), se busca la dosis `d_c` que iguala su degradación a la de la receta, medida como Δ NLL sobre el mismo texto neutro de 72 palabras con *teacher forcing*.

- **Objetivo:** Δ NLL = 1,046, el valor de la receta a d = 1.
- **Tolerancia:** |Δ NLL(control, d_c) − 1,046| ≤ 0,02.
- **Búsqueda:** bisección en d ∈ [0,02; 1,00], máximo 12 iteraciones.
- **Verificación de monotonía:** antes de la bisección se evalúa Δ NLL en d ∈ {0,02; 0,25; 0,5; 0,75; 1,0}. Si la secuencia no es creciente, ese control se marca `no_monotono` y se resuelve por rejilla fina en vez de bisección.
- **Exclusión declarada:** si un control no alcanza el objetivo dentro del rango, se registra como `no_alcanza` con su Δ NLL máximo y se excluye del test, informando cuántos fueron. Un control excluido NO se reemplaza por otro.

**Generación y juicio.** Idénticos a la fase 2, sin cambiar nada: mismos 8 prompts, decodificación voraz de 150 tokens, mediana por prompt, y los dos mismos jueces (`qwen3.6:35b-a3b-coding` y `gemma4:26b`) con la misma rúbrica, temperatura 0, semilla 7 y orden barajado. Los jueces no ven la condición.

## 3. Hipótesis y criterio de decisión

**H1′ (confirmatoria).** La receta a d = 1 obtiene mayor malevolencia media que los 22 controles emparejados en degradación.

- **Estadístico:** malevolencia media por condición (promedio de los dos jueces sobre los 8 prompts).
- **p empírico:** (1 + #{controles ≥ receta}) / (1 + número de controles válidos). Con 22 válidos el mínimo es 0,0435; se reportará junto con la cota de Clopper-Pearson, igual que en el borrador 2.
- **Se sostiene «no es daño»** si ningún control emparejado alcanza la malevolencia de la receta.
- **Se falsa, y así se escribirá**, si al menos un control emparejado alcanza la mitad del efecto de la receta (malevolencia ≥ 1,10) con coherencia ≥ 2. En ese caso el borrador dirá que la especificidad no se sostiene al emparejar la degradación.
- **Queda debilitado** si la coherencia mediana de los controles emparejados sigue por debajo de 2: significaría que igualar Δ NLL no basta para igualar la coherencia, y haría falta emparejar directamente por coherencia juzgada.

**Medida secundaria, sin corrección.** Proporción de salidas con malevolencia ≥ 2 según algún juez, receta frente a controles emparejados.

**Medida de control del emparejamiento.** Coherencia mediana de los controles emparejados. Se reporta siempre, salga como salga. Si sube de 0,72 a un valor cercano al de la receta, el emparejamiento funcionó; si no, se declara que no funcionó.

## 4. Lo que NO se hace

- No se buscan neuronas nuevas ni se optimiza la intervención.
- No se cambian los prompts, el modelo, la rúbrica ni los jueces.
- No se descarta ningún control por su resultado: solo por no alcanzar el objetivo de Δ NLL, que se decide antes de generar.
- No se mira ninguna salida generada antes de que los dos jueces terminen de puntuar.

## 5. Qué se publica

El resultado entra en el paper técnico tal como salga, incluso si refuta la afirmación central. Si la refuta, el título y el resumen se reescriben.
