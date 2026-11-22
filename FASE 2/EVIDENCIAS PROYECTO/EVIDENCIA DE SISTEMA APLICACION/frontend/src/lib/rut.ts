/*
 * El RUT chileno en el navegador.
 *
 * Solo es presentación: mientras la persona escribe, el campo le va poniendo
 * los puntos y el guion (12.345.678-5). El backend lo vuelve a validar y lo
 * guarda sin puntos (12345678-5), así que da lo mismo cómo llegue.
 */

/** Lo que importa del RUT: dígitos y una K final, sin puntos ni guion. */
function limpiar(valor: string): string {
  const soloValidos = valor.replace(/[^\dkK]/g, "").toUpperCase();
  // La K solo puede ser el dígito verificador: una K en medio se descarta.
  const sinKIntermedias = soloValidos.slice(0, -1).replace(/K/g, "") + soloValidos.slice(-1);
  // Cuerpo de hasta 8 dígitos más el verificador.
  return sinKIntermedias.slice(0, 9);
}

/**
 * Da formato a un RUT a medida que se escribe: «123456785» → «12.345.678-5».
 *
 * Con un solo carácter todavía no hay guion; desde el segundo, el último pasa a
 * ser el dígito verificador y el resto se agrupa de a tres con puntos.
 */
export function formatearRut(valor: string): string {
  const limpio = limpiar(valor);
  if (limpio.length <= 1) return limpio;
  const cuerpo = limpio.slice(0, -1).replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  return `${cuerpo}-${limpio.slice(-1)}`;
}

/** Formato y dígito verificador (módulo 11). El backend lo vuelve a revisar. */
export function rutValido(rut: string): boolean {
  const partes = /^(\d{7,8})-?([\dK])$/.exec(rut.replace(/[.\s]/g, "").toUpperCase());
  if (!partes) return false;
  let suma = 0;
  let factor = 2;
  for (const digito of partes[1].split("").reverse()) {
    suma += Number(digito) * factor;
    factor = factor === 7 ? 2 : factor + 1;
  }
  const resto = 11 - (suma % 11);
  const esperado = resto === 11 ? "0" : resto === 10 ? "K" : String(resto);
  return esperado === partes[2];
}
