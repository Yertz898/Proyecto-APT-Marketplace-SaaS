import type { NextConfig } from "next";

const enDesarrollo = process.env.NODE_ENV !== "production";

const nextConfig: NextConfig = {
  images: {
    /*
     * En desarrollo las imágenes las sirve Django desde /media/, en
     * `localhost:8000`. En producción vienen de Cloudflare R2 y hay que
     * agregar ese dominio a `remotePatterns`.
     */
    remotePatterns: [
      {
        protocol: "http",
        hostname: "localhost",
        port: "8000",
        pathname: "/media/**",
      },
    ],

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
