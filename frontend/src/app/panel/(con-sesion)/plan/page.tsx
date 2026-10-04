"use client";

import { useSesion } from "@/components/sesion/usar-sesion";
import { Cabecera, Cargando, Tarjeta } from "@/components/panel/piezas";
import { NOMBRE_DEL_PLAN } from "@/components/panel/secciones";
import type { Plan } from "@/lib/tipos";

const PLANES: { plan: Plan; precio: string; incluye: string }[] = [
  { plan: "basico", precio: "$10.990", incluye: "Catálogo, precios por cantidad, carga masiva y pedidos." },
  { plan: "premium", precio: "$20.990", incluye: "Suma tu marca, el panel de ventas, el equipo y la agenda." },
  { plan: "ultimate", precio: "$35.990", incluye: "Suma pronóstico, segmentos, sugerencias y asistente." },
];

export default function PaginaPlan() {
  const { sesion, hidratado } = useSesion();
  const actual = sesion?.usuario.tienda?.plan;

  if (!hidratado || !actual) return <Cargando />;

  return (
    <>
      <Cabecera
        titulo="Tu plan"
        descripcion="Precios mensuales netos por tienda. No hay cobro automático: el cambio de plan se coordina con nosotros."
      />

      <div className="grid gap-4 md:grid-cols-3">
        {PLANES.map((p) => (
          <Tarjeta key={p.plan} className={p.plan === actual ? "border-acero" : undefined}>
            <div className="flex items-center justify-between gap-2">
              <p className="font-jakarta text-[18px] font-extrabold">{NOMBRE_DEL_PLAN[p.plan]}</p>
              {p.plan === actual && (
                <span className="rounded-full bg-cielo px-2.5 py-1 text-[11px] font-semibold text-acero">
                  Tu plan
                </span>
              )}
            </div>
            <p className="mt-2 font-jakarta text-[26px] font-extrabold tracking-[-0.02em]">
              {p.precio}
              <span className="ml-1 text-[13px] font-normal text-pizarra">al mes</span>
            </p>
            <p className="mt-2 text-[14px] leading-[1.5] text-pizarra">{p.incluye}</p>
          </Tarjeta>
        ))}
      </div>
    </>
  );
}
