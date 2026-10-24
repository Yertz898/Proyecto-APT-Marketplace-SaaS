/*
 * Dirección del backend.
 *
 * Son dos y no una porque el frontend habla con la API desde dos lugares
 * distintos. El navegador la alcanza por el puerto publicado en el host; el
 * servidor de Next, que dentro de Docker es otro contenedor, la alcanza por el
 * nombre del servicio. Usar la misma dirección en los dos lados rompe uno.
 *
 * `API_URL_INTERNO` no lleva el prefijo NEXT_PUBLIC a propósito: es una
 * dirección de la red privada y no tiene por qué llegar al navegador. Fuera de
 * Docker no está definida y las dos direcciones terminan siendo la misma.
 */

export const API_NAVEGADOR = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

export const API_SERVIDOR = process.env.API_URL_INTERNO ?? API_NAVEGADOR;
