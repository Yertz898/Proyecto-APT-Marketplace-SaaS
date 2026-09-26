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
