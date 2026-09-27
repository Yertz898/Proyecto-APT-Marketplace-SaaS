import type { Pesos } from "@/lib/tipos";

const pesosChilenos = new Intl.NumberFormat("es-CL", {
  style: "currency",
  currency: "CLP",
  maximumFractionDigits: 0,
});

/** 45990 → "$45.990" */
export function formatearPesos(monto: Pesos): string {
  return pesosChilenos.format(monto);
}

const fechaChilena = new Intl.DateTimeFormat("es-CL", {
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
});

/** Fecha ISO del backend a dd-mm-aaaa, en hora local (CONVENCIONES.md > Zona horaria). */
export function formatearFecha(iso: string): string {
  const fecha = new Date(iso);
  if (Number.isNaN(fecha.getTime())) {
    return iso;
  }
  return fechaChilena.format(fecha).replaceAll("/", "-");
}

const gramosChilenos = new Intl.NumberFormat("es-CL", {
  maximumFractionDigits: 2,
});

/** 166.5 → "166,5 g" (gramos con coma decimal). */
export function formatearGramos(gramos: number): string {
  return `${gramosChilenos.format(gramos)} g`;
}

const ZONA_TIENDA = "America/Santiago";

const horaChilena = new Intl.DateTimeFormat("es-CL", {
  hour: "2-digit",
  minute: "2-digit",
  timeZone: ZONA_TIENDA,
});

const diaLargoChileno = new Intl.DateTimeFormat("es-CL", {
  weekday: "long",
  day: "numeric",
  month: "long",
  timeZone: ZONA_TIENDA,
});

/**
 * Hora de un instante ISO, siempre en hora de Chile.
 *
 * Se fija la zona a propósito: un comprador que viaja no debe ver su visita a
 * otra hora que la tienda.
 */
export function formatearHora(iso: string): string {
  return horaChilena.format(new Date(iso));
}

/** "lunes, 5 de octubre", en hora de Chile. */
export function formatearDiaLargo(iso: string): string {
  return diaLargoChileno.format(new Date(iso));
}

/** Clave estable del día de un instante, para agrupar horas. */
export function diaDe(iso: string): string {
  return new Date(iso).toLocaleDateString("en-CA", { timeZone: ZONA_TIENDA });
}
