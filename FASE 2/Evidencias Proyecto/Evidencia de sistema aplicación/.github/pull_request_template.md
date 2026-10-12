## Qué cambia

<!-- Una o dos frases. Qué hace este PR y por qué. -->

## Historia / tarea del backlog

<!-- Ej.: HU-14 Motor de precios escalonados -->

## Criterio de terminado

- [ ] Revisado por el otro integrante del equipo
- [ ] Pruebas unitarias en verde (`docker compose exec api pytest`)
- [ ] Lint sin errores (`ruff check .` y `npm run lint`)
- [ ] Desplegado y probado en el ambiente de pruebas
- [ ] Documentación actualizada

## Aislamiento por tienda

- [ ] Este PR **no** lee datos de tienda, o
- [ ] Todo queryset nuevo filtra por la tienda del usuario autenticado **desde la capa común**, y
- [ ] Incluye su prueba de aislamiento: autenticado como tienda A, pedir un recurso de
      la tienda B responde **`404`, no `403`** (un 403 confirma que el recurso existe)

## Seguridad

- [ ] Ninguna credencial, token ni clave quedó en el código
- [ ] Los endpoints nuevos validan rol en el backend, no solo en la interfaz
