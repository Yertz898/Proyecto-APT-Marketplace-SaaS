import { leerError } from "@/lib/api/errores";
import { pedirConSesion } from "@/lib/api/sesion";
import { guardarSesion, instantanea } from "@/lib/sesion";
import type { Plan, UsuarioSesion } from "@/lib/tipos";
import type {
  BloqueDeAtencion,
  ConfiguracionDeAgenda,
  DiaCerrado,
  EstadoDelPlan,
  EstadoDeVisita,
  Miembro,
  NuevaTienda,
  PaginaDeRegistros,
  SolicitudDeAcceso,
  TiendaDePlataforma,
  VisitaDelPanel,
} from "@/lib/tipos-gestion";

/*
 * Las llamadas de la gestión: cuenta, equipo, plan, agenda y plataforma.
 *
 * Ninguna ruta del panel nombra una tienda: el backend la saca del token. Las de
 * la plataforma sí la nombran, porque son las únicas que ven más de una, y el
 * backend las cierra a todo el que no sea administrador.
 */

async function pedir<T>(ruta: string, metodo = "GET", cuerpo?: unknown): Promise<T> {
  const respuesta = await pedirConSesion(ruta, {
    method: metodo,
    body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo),
  });
  if (!respuesta.ok) {
    throw await leerError(respuesta);
  }
  return (respuesta.status === 204 ? undefined : await respuesta.json()) as T;
}

// ── Cuenta propia ───────────────────────────────────────────────────────────

/** Cambia el nombre y lo refleja en la sesión guardada, para que el menú lo muestre. */
export async function cambiarNombre(nombre: string): Promise<UsuarioSesion> {
  const usuario = await pedir<UsuarioSesion>("/auth/yo", "PATCH", { nombre });
  const sesion = instantanea();
  if (sesion) guardarSesion({ ...sesion, usuario });
  return usuario;
}

export function cambiarContrasena(actual: string, nueva: string): Promise<void> {
  return pedir("/auth/contrasena", "POST", { actual, nueva });
}

// ── Equipo ──────────────────────────────────────────────────────────────────

export const obtenerEquipo = () => pedir<Miembro[]>("/panel/equipo");

export const crearVendedor = (datos: { nombre: string; email: string; password: string }) =>
  pedir<Miembro>("/panel/equipo", "POST", datos);

export const cambiarMiembro = (id: number, cambios: Partial<Pick<Miembro, "nombre" | "activo">>) =>
  pedir<Miembro>(`/panel/equipo/${id}`, "PATCH", cambios);

export const reiniciarClave = (id: number, nueva: string) =>
  pedir<void>(`/panel/equipo/${id}/contrasena`, "POST", { nueva });

// ── Plan ────────────────────────────────────────────────────────────────────

/** Tras un cambio de plan, la sesión guardada también lo sabe: el menú dibuja los candados con ella. */
function reflejarPlan(estado: EstadoDelPlan): EstadoDelPlan {
  const sesion = instantanea();
  if (sesion?.usuario.tienda) {
    guardarSesion({
      ...sesion,
      usuario: { ...sesion.usuario, tienda: { ...sesion.usuario.tienda, plan: estado.plan } },
    });
  }
  return estado;
}

export const obtenerPlan = () => pedir<EstadoDelPlan>("/panel/plan");

export const cambiarPlan = async (plan: Plan) =>
  reflejarPlan(await pedir<EstadoDelPlan>("/panel/plan", "PATCH", { plan }));

export const cancelarPlan = () => pedir<EstadoDelPlan>("/panel/plan/cancelar", "POST");

export const reanudarPlan = () => pedir<EstadoDelPlan>("/panel/plan/reanudar", "POST");

// ── Agenda ──────────────────────────────────────────────────────────────────

export const obtenerConfiguracionAgenda = () =>
  pedir<ConfiguracionDeAgenda>("/panel/agenda/configuracion");

export const guardarConfiguracionAgenda = (cambios: Partial<ConfiguracionDeAgenda>) =>
  pedir<ConfiguracionDeAgenda>("/panel/agenda/configuracion", "PATCH", cambios);

export const obtenerBloques = () => pedir<BloqueDeAtencion[]>("/panel/agenda/bloques");

export const crearBloque = (bloque: Omit<BloqueDeAtencion, "id">) =>
  pedir<BloqueDeAtencion>("/panel/agenda/bloques", "POST", bloque);

export const borrarBloque = (id: number) => pedir<void>(`/panel/agenda/bloques/${id}`, "DELETE");

export const obtenerDiasCerrados = () => pedir<DiaCerrado[]>("/panel/agenda/dias-cerrados");

export const cerrarDia = (fecha: string, motivo: string) =>
  pedir<DiaCerrado>("/panel/agenda/dias-cerrados", "POST", { fecha, motivo });

export const abrirDia = (id: number) => pedir<void>(`/panel/agenda/dias-cerrados/${id}`, "DELETE");

export const obtenerVisitas = () => pedir<VisitaDelPanel[]>("/panel/agenda/visitas");

export const cambiarEstadoDeVisita = (id: number, estado: EstadoDeVisita, motivoRechazo = "") =>
  pedir<VisitaDelPanel>(`/panel/agenda/visitas/${id}/estado`, "POST", { estado, motivoRechazo });

// ── Plataforma ──────────────────────────────────────────────────────────────

export const obtenerTiendas = () => pedir<TiendaDePlataforma[]>("/plataforma/tiendas");

export const crearTienda = (datos: NuevaTienda) =>
  pedir<TiendaDePlataforma>("/plataforma/tiendas", "POST", datos);

export const cambiarTienda = (
  slug: string,
  cambios: Partial<Pick<TiendaDePlataforma, "nombre" | "plan" | "plantilla" | "activa">>,
) => pedir<TiendaDePlataforma>(`/plataforma/tiendas/${slug}`, "PATCH", cambios);

export const obtenerSolicitudes = () => pedir<SolicitudDeAcceso[]>("/plataforma/solicitudes");

export const cambiarSolicitud = (id: number, cambios: Partial<Pick<SolicitudDeAcceso, "estado" | "notas">>) =>
  pedir<SolicitudDeAcceso>(`/plataforma/solicitudes/${id}`, "PATCH", cambios);

export function obtenerRegistros(filtros: {
  tienda?: string;
  accion?: string;
  q?: string;
  pagina?: number;
}): Promise<PaginaDeRegistros> {
  const consulta = new URLSearchParams();
  for (const [clave, valor] of Object.entries(filtros)) {
    if (valor) consulta.set(clave, String(valor));
  }
  return pedir<PaginaDeRegistros>(`/plataforma/registros?${consulta}`);
}

// ── Precios por volumen ─────────────────────────────────────────────────────

export type TramoDelPanel = {
  id: number;
  /** Viene como texto decimal: "12.00". */
  umbral: string;
  unidadUmbral: "cantidad" | "monto" | "peso";
  precioNeto: number;
};

export const obtenerTramos = (codigo: string) =>
  pedir<TramoDelPanel[]>(`/panel/productos/${encodeURIComponent(codigo)}/tramos`);

export const crearTramo = (codigo: string, tramo: Omit<TramoDelPanel, "id">) =>
  pedir<TramoDelPanel>(`/panel/productos/${encodeURIComponent(codigo)}/tramos`, "POST", tramo);

export const borrarTramo = (id: number) => pedir<void>(`/panel/tramos/${id}`, "DELETE");
