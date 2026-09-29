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

/** Fecha ISO del backend a dd-mm-aaaa, en hora local (CLAUDE.md > Zona horaria). */
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
  // En Chile la hora se escribe de corrido: "15:30", no "3:30 p. m.".
  hour12: false,
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

/*
 * Las fechas aaaa-mm-dd son días del calendario, no instantes: se formatean y
 * se suman en UTC a propósito. Interpretarlas en hora de Chile las correría al
 * día anterior, porque `new Date("2026-09-28")` es medianoche UTC.
 */

const fechaLargaChilena = new Intl.DateTimeFormat("es-CL", {
  day: "numeric",
  month: "long",
  timeZone: "UTC",
});

/** "2026-09-28" → "28 de septiembre". */
export function formatearFechaLarga(fecha: string): string {
  return fechaLargaChilena.format(new Date(`${fecha}T00:00:00Z`));
}

/** Suma (o resta) días a una fecha aaaa-mm-dd y devuelve otra fecha aaaa-mm-dd. */
export function sumarDias(fecha: string, dias: number): string {
  const [ano, mes, dia] = fecha.split("-").map(Number);
  return new Date(Date.UTC(ano, mes - 1, dia + dias)).toISOString().slice(0, 10);
}
