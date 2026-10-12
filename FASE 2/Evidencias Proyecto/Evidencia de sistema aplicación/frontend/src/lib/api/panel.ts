import type {
  CargaHistorial,
  LimitesCarga,
  ResumenCarga,
  ResumenFotos,
  TipoCarga,
} from "@/lib/tipos-panel";

/*
 * Acceso a la API del panel de la tienda.
 *
 * El backend todavía no existe. Estas funciones fallan con un mensaje explícito
 * en vez de devolver datos inventados: así la pantalla muestra el estado real
 * del sistema y nadie confunde una maqueta con algo que funciona.
 *
 * Endpoints que hay que implementar (ver el contrato acordado):
 *   GET    /panel/cargas/limites
 *   GET    /panel/plantillas/{tipo}
 *   POST   /panel/cargas/{tipo}/validar      (multipart, NO escribe nada)
 *   POST   /panel/cargas/{cargaId}/confirmar
 *   DELETE /panel/cargas/{cargaId}
 *   GET    /panel/cargas?tipo=
 *
 * Recordatorios al implementarlas:
 * - La tienda sale del token del usuario, nunca de la URL ni del cuerpo.
 * - El backend valida el archivo por contenido, no por extensión. Lo que hace
 *   el frontend es solo ayuda al usuario.
 */

export class ApiPendiente extends Error {
  constructor(endpoint: string) {
    super(`Esta función todavía no está conectada: falta implementar ${endpoint} en el backend.`);
    this.name = "ApiPendiente";
  }
}

export async function obtenerLimitesDeCarga(): Promise<LimitesCarga | null> {
  // Sin backend no se conocen los límites: la pantalla omite ese aviso en vez
  // de mostrar un número inventado.
  return null;
}

export function urlDePlantilla(tipo: TipoCarga): string {
  return `/api/panel/plantillas/${tipo}`;
}

export async function validarCarga(tipo: TipoCarga, archivo: File): Promise<ResumenCarga> {
  void archivo;
  throw new ApiPendiente(`POST /panel/cargas/${tipo}/validar`);
}

export async function validarFotos(archivo: File): Promise<ResumenFotos> {
  void archivo;
  throw new ApiPendiente("POST /panel/cargas/fotos/validar");
}

export async function confirmarCarga(cargaId: string, desactivarAusentes: boolean): Promise<void> {
  void desactivarAusentes;
  throw new ApiPendiente(`POST /panel/cargas/${cargaId}/confirmar`);
}

export async function cancelarCarga(cargaId: string): Promise<void> {
  throw new ApiPendiente(`DELETE /panel/cargas/${cargaId}`);
}

export async function obtenerHistorialDeCargas(tipo?: TipoCarga): Promise<CargaHistorial[]> {
  void tipo;
  return [];
}
