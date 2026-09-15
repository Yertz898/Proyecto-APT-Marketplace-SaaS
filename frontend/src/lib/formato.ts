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
