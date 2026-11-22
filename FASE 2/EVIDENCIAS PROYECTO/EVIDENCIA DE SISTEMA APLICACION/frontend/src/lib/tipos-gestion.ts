/**
 * Tipos de la gestión: la cuenta, el equipo, el plan, la agenda del panel y la
 * administración de la plataforma.
 */

import type { Plan } from "@/lib/tipos";

// ── Equipo ──────────────────────────────────────────────────────────────────

export type Miembro = {
  id: number;
  nombre: string;
  email: string;
  rol: "dueno_tienda" | "vendedor";
  rolNombre: string;
  activo: boolean;
  /** Fecha en ISO. */
  fechaRegistro: string;
};

// ── Plan ────────────────────────────────────────────────────────────────────

export type OpcionDePlan = {
  plan: Plan;
  nombre: string;
  precioNeto: number;
  incluye: string;
};

export type EstadoDelPlan = {
  plan: Plan;
  /** Null mientras la suscripción esté vigente. */
  canceladaEn: string | null;
  planes: OpcionDePlan[];
};

// ── Agenda ──────────────────────────────────────────────────────────────────

export type ConfiguracionDeAgenda = {
  duracionMinutos: number;
  visitasPorBloque: number;
  anticipacionMinimaHoras: number;
  ventanaMaximaDias: number;
  confirmacionAutomatica: boolean;
  direccion: string;
  indicaciones: string;
  correoNotificaciones: string;
};

export type BloqueDeAtencion = {
  id: number;
  nombre: string;
  /** 0 es lunes. Null si el bloque es de una fecha puntual. */
  diaSemana: number | null;
  /** aaaa-mm-dd, o null si es semanal. */
  fecha: string | null;
  horaInicio: string;
  horaFin: string;
  duracionMinutos: number | null;
  visitasSimultaneas: number | null;
};

/** Una propuesta para mover una visita. La responde el lado contrario a `propuestoPor`. */
export type CambioPendiente = {
  id: number;
  inicio: string;
  fin: string;
  propuestoPor: "comprador" | "tienda";
};

export type DiaCerrado = { id: number; fecha: string; motivo: string };

export type EstadoDeVisita =
  | "solicitada"
  | "confirmada"
  | "asistida"
  | "no_asistio"
  | "rechazada"
  | "cancelada";

export type VisitaDelPanel = {
  id: number;
  inicio: string;
  fin: string;
  estado: EstadoDeVisita;
  estadoNombre: string;
  nombreContacto: string;
  correoContacto: string;
  telefonoContacto: string;
  motivo: string;
  motivoRechazo: string;
  /** A qué estados puede pasar desde el actual. */
  siguientes: EstadoDeVisita[];
  /** Solicitud cuya hora ya tomó otra visita confirmada: no se puede confirmar. */
  horaTomada: boolean;
  /** Propuesta de otra hora que espera respuesta, o null. */
  cambioPendiente: CambioPendiente | null;
};

// ── Plataforma ──────────────────────────────────────────────────────────────

export type Plantilla = "clasica" | "moderna" | "minimal";

export type TiendaDePlataforma = {
  id: number;
  slug: string;
  nombre: string;
  plan: Plan;
  plantilla: Plantilla;
  activa: boolean;
  canceladaEn: string | null;
  fechaCreacion: string;
  dueno: { nombre: string; email: string } | null;
  productos: number;
  pedidos: number;
  usuarios: number;
};

export type NuevaTienda = {
  nombre: string;
  slug: string;
  plan: Plan;
  plantilla: Plantilla;
  duenoNombre: string;
  duenoEmail: string;
  duenoPassword: string;
  /** La solicitud de acceso de la que sale, si sale de una: queda como activada. */
  solicitud?: number | null;
};

export type SolicitudDeAcceso = {
  id: number;
  negocio: string;
  nombre: string;
  email: string;
  telefono: string;
  mensaje: string;
  estado: "nueva" | "contactada" | "activada" | "descartada";
  estadoNombre: string;
  notas: string;
  fecha: string;
};

export type RegistroDeActividad = {
  id: number;
  fecha: string;
  tienda: string;
  usuario: string;
  accion: "crear" | "modificar" | "eliminar" | "sesion" | "plan" | "cuenta";
  accionNombre: string;
  modelo: string;
  objeto: string;
  detalle: Record<string, { antes: unknown; despues: unknown } | unknown>;
  ip: string | null;
};

export type PaginaDeRegistros = {
  count: number;
  next: string | null;
  previous: string | null;
  results: RegistroDeActividad[];
};
