"use client";

import { InsigniaDeEstado } from "@/components/panel/estado-pedido";
import { Leyenda, LineaDeTiempo, SERIE } from "@/components/panel/graficos";
import { formatearPesos } from "@/lib/formato";
import type { EstadoPedido } from "@/lib/tipos-panel";

import { Franja, TituloDeSeccion } from "./secciones";

/*
 * El panel del vendedor, mostrado con las mismas piezas que usa el panel.
 *
 * El gráfico es el `LineaDeTiempo` de `components/panel/graficos.tsx` y las
 * insignias de los pedidos son las de la bandeja de Pedidos: lo que se ve acá
 * es lo que el dueño va a ver adentro, no un dibujo parecido.
 *
 * Los números son inventados y la sección lo dice con una etiqueta a la vista.
 * No es un detalle de diseño: el proyecto trabaja con datos sintéticos y todo
 * gráfico hecho con ellos se rotula como tal (CONVENCIONES.md > Ingesta de planillas).
 */

const MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov"];
const ESTE_ANO = [2.9, 2.6, 3.4, 3.2, 3.8, 3.6, 4.1, 4.4, 4.8, 5.1, 2.7];
const ANO_PASADO = [2.4, 2.2, 2.7, 2.9, 3.1, 3.0, 3.3, 3.5, 3.9, 4.2, 4.6];

const SERIES = [
  {
    nombre: "2026",
    color: SERIE[0],
    // Noviembre va por la mitad: se dibuja hueco, como en el panel.
    puntos: MESES.map((etiqueta, i) => ({
      etiqueta,
      valor: ESTE_ANO[i] * 1_000_000,
      atenuado: i === MESES.length - 1,
    })),
  },
  {
    nombre: "2025",
    color: "#8b93a1",
    puntos: MESES.map((etiqueta, i) => ({ etiqueta, valor: ANO_PASADO[i] * 1_000_000 })),
  },
];

const CIFRAS = [
  { etiqueta: "Ventas de octubre", valor: formatearPesos(5_100_000), nota: "+21 % que octubre 2025", color: "text-jade" },
  { etiqueta: "Pedidos del mes", valor: "128", nota: "Ticket promedio $39.840", color: "text-marino" },
  { etiqueta: "Pronóstico de diciembre", valor: formatearPesos(6_400_000), nota: "Holt amortiguado", color: "text-acero" },
];

const PEDIDOS: { folio: string; cliente: string; total: number; estado: EstadoPedido }[] = [
  { folio: "DC-7F3A91C2", cliente: "Comercial Las Rosas", total: 186_420, estado: "PENDIENTE" },
  { folio: "DC-2B8E04D7", cliente: "Bisutería Ñuñoa", total: 94_300, estado: "CONFIRMADO" },
  { folio: "DC-C51F6A08", cliente: "Feria Persa Bío Bío", total: 312_900, estado: "ENTREGADO" },
];

const ALERTAS = [
  { producto: "Cadena 925 · 50 cm", detalle: "Se acaba en ~6 días" },
  { producto: "Aros argolla 12 mm", detalle: "Se acaba en ~11 días" },
];

function millones(valor: number) {
  return formatearPesos(Math.round(valor));
}

export function PanelDeVentas() {
  return (
    <Franja className="pb-[clamp(64px,7cqi,112px)]">
      <TituloDeSeccion antetitulo="Tu panel">Mira cómo va tu negocio, y hacia dónde va</TituloDeSeccion>

      <div className="flex flex-col gap-6 rounded-xl border border-arena bg-white p-[clamp(18px,3cqi,32px)]">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <span className="font-jakarta text-lg font-bold">Resumen de la tienda</span>
          <span className="inline-flex items-center gap-1.5 rounded-full border border-ambar bg-trigo px-3 py-[5px] text-[13px] font-semibold text-marino">
            <span className="size-[7px] rounded-full bg-ambar" />
            Datos de ejemplo
          </span>
        </div>

        <div className="grid grid-cols-[repeat(auto-fit,minmax(min(100%,220px),1fr))] gap-3">
          {CIFRAS.map((cifra) => (
            <div key={cifra.etiqueta} className="flex flex-col gap-1 rounded-lg border border-arena bg-hueso px-4 py-3.5">
              <span className="text-[13px] text-pizarra">{cifra.etiqueta}</span>
              <span className={`font-jakarta text-[26px] font-extrabold tracking-[-0.02em] tabular-nums ${cifra.color}`}>
                {cifra.valor}
              </span>
              <span className="text-xs text-pizarra">{cifra.nota}</span>
            </div>
          ))}
        </div>

        <div className="grid gap-6 @4xl:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
          <div className="flex min-w-0 flex-col gap-3">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <h3 className="text-[13px] font-semibold text-marino">Ventas por mes</h3>
              <Leyenda entradas={SERIES.map((s) => ({ nombre: s.nombre, color: s.color }))} />
            </div>
            <LineaDeTiempo series={SERIES} formatear={millones} />
          </div>

          <div className="flex min-w-0 flex-col gap-5">
            <div className="flex flex-col gap-2">
              <h3 className="text-[13px] font-semibold text-marino">Últimos pedidos</h3>
              <ul className="flex list-none flex-col divide-y divide-arena rounded-lg border border-arena p-0">
                {PEDIDOS.map((pedido) => (
                  <li key={pedido.folio} className="flex items-center justify-between gap-3 px-3 py-2.5">
                    <div className="min-w-0">
                      <p className="truncate text-[13px] font-semibold text-marino">{pedido.cliente}</p>
                      <p className="text-[11px] text-pizarra tabular-nums">
                        {pedido.folio} · {formatearPesos(pedido.total)}
                      </p>
                    </div>
                    <InsigniaDeEstado estado={pedido.estado}>
                      {pedido.estado === "PENDIENTE" ? "Por coordinar" : undefined}
                    </InsigniaDeEstado>
                  </li>
                ))}
              </ul>
            </div>

            <div className="flex flex-col gap-2">
              <h3 className="text-[13px] font-semibold text-marino">Alertas de stock</h3>
              <ul className="flex list-none flex-col gap-2 p-0">
                {ALERTAS.map((alerta) => (
                  <li
                    key={alerta.producto}
                    className="flex items-center justify-between gap-3 rounded-lg border border-ambar/40 bg-trigo/50 px-3 py-2"
                  >
                    <span className="truncate text-[13px] text-marino">{alerta.producto}</span>
                    <span className="flex-none text-[11px] font-semibold text-ambar-hondo">{alerta.detalle}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </Franja>
  );
}
