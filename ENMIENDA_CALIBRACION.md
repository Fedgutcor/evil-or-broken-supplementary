# Enmienda a la calibración humana (§3.6): de cuatro evaluadores a tres

**Fecha:** 2026-11-03
**Decisión:** Federico Gutiérrez-Correa (primer autor, fgc)
**Momento:** después de recibir las tres planillas de los coautores y ANTES de calcular cualquier
estadístico de calibración. Este archivo y los cambios del artículo se commitean antes de correr
`codigo/calibracion.py`; el orden queda en la historia de git.

## Qué decía el diseño fijado antes de recibir calificaciones

- Califican a ciegas los cuatro autores (fgc, jals, cdeo, waag) la muestra sellada de 60 salidas
  (semilla 20261028, SHA-256 `50240120e4f2…`).
- Análisis (i)–(iii) y, además, (iv): repetir (i)–(iii) con y sin el primer autor, porque fgc leyó
  sin cegamiento las salidas del piloto (fase 1).

## Qué cambia

- **Califican tres evaluadores:** jals (Jerri Alejandro López Sánchez), cdeo (Cristian David
  Echeverri Ocampo) y waag (Wilson Andrés Araque Garzón). Ninguno había visto salidas antes de
  calificar.
- **El primer autor no califica.** Se elimina el análisis (iv), que existía sólo para medir el
  efecto de su exposición al piloto.
- (i)–(iii), la muestra, la rúbrica, el redondeo para κ, la reponderación de estratos (30/240 y
  210/240) y el código `calibracion.py` no cambian. Se corre sin `--primer-autor`.

## Por qué

El análisis (iv) protegía contra un riesgo: que el evaluador expuesto al piloto sesgara el
consenso. Sin ese evaluador el riesgo desaparece, y el consenso queda formado sólo por evaluadores
cegados. El costo es tener un evaluador menos (tres en lugar de cuatro), lo que da menos precisión
al acuerdo entre humanos. Ese costo se declara en las limitaciones.

## Exposición parcial que hay que declarar

El 2026-11-03, al hacer el inventario de los archivos recibidos, el asistente de IA imprimió en su
salida de herramienta los puntajes por ítem de waag (S001–S020) y de cdeo (S001–S002). No se
calculó ningún estadístico. El primer autor vio esos valores antes de decidir la enmienda (lo confirmó el 2026-11-04:
«ya los vi»); la decisión no se apoyó en ningún estadístico, porque no se había calculado ninguno. Como el primer autor ya no califica, esa exposición no contamina ninguna calificación,
pero queda registrada porque la decisión de enmendar es posterior a la recepción de los datos.

## Planillas recibidas (crudas, sin editar)

| evaluador | archivo | exportado (UTC) | ítems | SHA-256 de la muestra |
|---|---|---|---|---|
| cdeo | calibracion_cdeo_2026-10-28.json | 2026-10-29T03:30:49Z | 60/60 | 50240120e4f2… |
| jals | calibracion_jals_2026-10-29.json | 2026-10-29T14:59:46Z | 60/60 | 50240120e4f2… |
| waag | calibracion_waag_2026-11-01.json | 2026-11-01T22:45:23Z | 60/60 | 50240120e4f2… |

Se guardan en `datos/calibracion/` en el mismo commit que esta enmienda.

SHA-256 de cada archivo crudo (para verificar que no se editaron después):

```
4cf5547418f2c7f41580f53c5d999b649d75e2de7ed570c6485e058d55fb8a21  datos/calibracion/calibracion_cdeo_2026-10-28.json
66598d64b4854a927ea880664765869b1f261150c90cb36978072a74c9bff586  datos/calibracion/calibracion_jals_2026-10-29.json
25510b450f071060372d638406606a58344de92f73f84b40bc4cf9b6a3237f53  datos/calibracion/calibracion_waag_2026-11-01.json
```

## Nota posterior al cálculo (2026-11-03, commit siguiente a `ccd093c`)

- **κ en el estrato «ceros», malevolencia.** `datos/calibracion_resultado.json` reporta κ = 0.0. El
  código devuelve 0 cuando uno de los dos lados no tiene varianza (los jueces dieron 0 a los 30
  ítems de ese estrato por definición), porque en ese caso la matriz observada coincide con la
  esperada. El artículo aplica la regla fijada en §3.6: sin varianza, κ es indefinido y sólo se
  reporta el acuerdo exacto (70 %). No es una discrepancia entre el código y el texto.
- **Confirmado por el primer autor (2026-11-04):** vio los puntajes impresos el 2026-11-03 («ya los
  vi»). La versión anterior de la sección «Exposición parcial» decía que había decidido sin
  consultarlos; esa frase la había escrito el asistente sin verificarla, y era falsa. Se corrigió.

## Independencia de los evaluadores (2026-11-04)

En la hoja de revisión (borrador 5), la casilla «No comenté el contenido con otros autores antes de
exportar» quedó marcada sólo por waag; jals y cdeo la dejaron sin marcar. Consultado por el
asistente, el primer autor respondió el 2026-11-04: «no hablaron». El artículo mantiene que las
tres calificaciones fueron independientes con base en esa confirmación, que es del primer autor y
no de los evaluadores. Hojas: `revisiones/revision_{jals_2026-10-29,cdeo_2026-11-04,waag_2026-11-04}.json`
(fuera del repositorio público por contener datos personales).
