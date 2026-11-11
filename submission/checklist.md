# Lista de comprobación antes del envío

Revista: *Journal of Quantitative Criminology* (Springer). Envío por la vía de suscripción, sin costo para el autor.

## Requisitos de la revista (leídos en la guía oficial el 11-11-2026)

- [x] Resumen estructurado en Objectives, Methods, Results, Conclusions, máximo 250 palabras (tiene 245).
- [x] 4 a 6 palabras clave.
- [x] Ecuaciones de los modelos estimados en el texto (la guía lo exige).
- [x] Citas autor-año y lista de referencias en formato Springer, con DOI.
- [x] Manuscrito anónimo; datos de autoría solo en `title_page.md`.
- [x] Archivo en Word (`manuscript/manuscript.docx`), tablas con la función de tabla.
- [x] Declaración de disponibilidad de datos.
- [ ] Figuras como archivos separados (`manuscript/figures/*.png`, 300 dpi). Subirlas una por una.
- [ ] Completar autoría, filiación, financiamiento y conflictos de interés en `title_page.md` y `cover_letter.md`.
- [ ] Publicar el paquete de replicación en un repositorio anónimo (OSF o similar) y pegar el enlace.

## Pendientes que no pude cerrar desde aquí

1. **Cuartil de la revista.** SCImago bloquea las consultas automáticas. Los agregadores consultados la dan como Q1 en Law (SJR 1,349, datos 2024). Confirmar a mano en scimagojr.com antes de enviar.
2. **Datos de homicidios.** El portal oficial rechaza descargas automáticas; se usó la réplica pública `jp1309/crimen`, cuyos archivos coinciden con las sumas SHA-256 de su manifiesto. Conviene descargar una vez los dos Excel desde datosabiertos.gob.ec y comparar el hash.
3. **Decretos.** La cobertura se codificó a partir de notas de Primicias y Lexis que reproducen cada decreto, y de los dictámenes citados. Cotejar con el Registro Oficial al menos: Decreto 193 (renovación de marzo de 2024), fecha exacta de cese de los decretos 250 y 275, exclusión de La Troncal en el Decreto 552, y fecha de firma del Decreto 202 (4 o 5 de noviembre de 2025).
4. **Referencias no abiertas en esta sesión.** Los DOI de estas entradas se escribieron de memoria y hay que comprobarlos: Ashenfelter (1978), Bowers y Johnson (2003), Braga et al. (2019), Butts (2021), Guerette y Bowers (2009), Rambachan y Roth (2023), Runfola et al. (2020), Santos Silva y Tenreyro (2006), Wooldridge (2023). El resto se tomó de los metadatos de las propias publicaciones.
5. **Dato de contexto.** La cifra de 22 organizaciones nombradas en el Decreto 111 debe verificarse en el texto del decreto.

## Puntos débiles que un revisor va a señalar

- El efecto directo no queda identificado en un punto: se reporta como rango (sin efecto a −47 %). Es la conclusión honesta de los datos y el texto la defiende, pero es el flanco principal.
- El núcleo costero (83 % de los homicidios) queda fuera del análisis causal por falta de grupo de comparación.
- Potencia baja para el desplazamiento: solo se detectarían aumentos cercanos a dos tercios.
- 24 conglomerados provinciales. Se añadió inferencia por aleatorización.
- No se estimó Callaway–Sant'Anna; el diseño apilado cumple la misma función, pero un revisor puede pedirlo.
