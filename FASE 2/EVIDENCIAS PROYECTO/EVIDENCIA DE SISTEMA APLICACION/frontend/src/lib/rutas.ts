/*
 * Destinos después de iniciar sesión.
 *
 * El formulario recibe a dónde volver en la dirección, y eso lo escribe quien
 * arma el enlace: puede ser cualquiera. Una dirección a otro sitio convertiría
 * el inicio de sesión en un trampolín para llevar a alguien a una copia de la
 * tienda justo después de que escribió su contraseña.
 */

/**
 * Deja pasar solo rutas internas.
 *
 * Tiene que empezar con una sola barra: "//otro-sitio.cl" y "https://…" son
 * direcciones absolutas aunque parezcan rutas, y "/\otro" lo es en algunos
 * navegadores.
 */
export function rutaSegura(volver: string | undefined, porOmision: string): string {
  if (!volver || !volver.startsWith("/") || volver.startsWith("//") || volver.startsWith("/\\")) {
    return porOmision;
  }
  return volver;
}

/** Lee el parámetro `volver` de la dirección, sea cual sea su forma. */
export function volverDe(consulta: Record<string, string | string[] | undefined>): string | undefined {
  const valor = consulta.volver;
  return typeof valor === "string" ? valor : undefined;
}
