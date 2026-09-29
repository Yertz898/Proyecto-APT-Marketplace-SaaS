import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    // En desarrollo las imágenes las sirve Django desde /media/. En producción
    // vienen de Cloudflare R2 y hay que agregar ese dominio acá.
    remotePatterns: [
      {
        protocol: "http",
        hostname: "localhost",
        port: "8000",
        pathname: "/media/**",
      },
    ],
  },
};

export default nextConfig;
