import path from "node:path";

import type { NextConfig } from "next";

const enDesarrollo = process.env.NODE_ENV !== "production";

/*
 * De dónde vienen las fotos de los productos.
 *
 * En desarrollo las sirve Django desde `/media/`. En producción vienen de
 * Cloudflare R2, por el dominio público del bucket. Next exige que ese
 * dominio esté declarado acá —es una lista blanca contra la que valida el
 * optimizador de imágenes— y esta configuración se evalúa **al compilar**,
 * así que la variable tiene que existir en el entorno de build y no solo en
 * el de ejecución.
 *
 * Estaba escrito a mano como `localhost:8000`. En producción eso no es un
 * error de configuración que avise: las fotos simplemente no cargan.
 */
const origenDeLasFotos =
  process.env.NEXT_PUBLIC_MEDIA_URL?.trim() || "http://localhost:8000";

function patronDeImagenes() {
  const url = new URL(origenDeLasFotos);
  return {
    protocol: url.protocol.replace(":", "") as "http" | "https",
    hostname: url.hostname,
    // Cadena vacía cuando el origen no trae puerto: es lo que Next espera
    // para decir «el puerto por omisión del protocolo».
    port: url.port,
    pathname: "/**",
  };
}

/*
 * La raíz del proyecto para Next es esta carpeta, no la del repositorio.
 *
 * El frontend vive en «FASE 2/EVIDENCIAS PROYECTO/…/frontend». Si Next empaqueta
 * tomando como raíz el repositorio, esa ruta —con espacios— termina en el nombre
 * de la función que Vercel crea para el servidor, y Vercel rechaza el build:
 * los nombres no pueden tener espacios. Todo lo que el frontend necesita está
 * dentro de esta carpeta, así que no se pierde nada al fijarla acá.
 */
const raizDelFrontend = path.join(__dirname);

const nextConfig: NextConfig = {
  outputFileTracingRoot: raizDelFrontend,
  turbopack: { root: raizDelFrontend },
  images: {
    remotePatterns: [patronDeImagenes()],

    /*
     * En desarrollo las imágenes no pasan por el optimizador, y no es pereza.
     *
     * El optimizador corre dentro del contenedor `web`, donde `localhost:8000`
     * es el propio contenedor y no Django: el mismo desdoblamiento que obliga
     * a tener dos direcciones de la API. Y aunque se resolviera, Next se niega
     * a optimizar una imagen cuyo host es una IP privada, porque sería una vía
     * de SSRF si la dirección viniera de afuera. Ese freno se puede desactivar
     * con `dangerouslyAllowLocalIP`, y preferimos no tener esa bandera escrita
     * en el proyecto ni siquiera apagada.
     *
     * En producción el optimizador sí trabaja: R2 es un dominio público.
     */
    unoptimized: enDesarrollo,
  },
};

export default nextConfig;
