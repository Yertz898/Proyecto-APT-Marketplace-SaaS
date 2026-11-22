"use client";

import { useState } from "react";

import { InsigniaDeEstado } from "@/components/panel/estado-pedido";
import { formatearPesos } from "@/lib/formato";
import { cn } from "@/lib/utils";

/*
 * El cotizador del titular: un pedido de ejemplo que se puede tocar.
 *
 * Reemplaza a la maqueta estática de antes. La idea es que quien llega a la
 * portada vea en diez segundos lo que DealCommerce hace por él: mueve la
 * cantidad y el tramo, el precio unitario y el total cambian solos.
 *
 * Los productos y precios son de ejemplo y la tarjeta lo dice a la vista. Las
 * cuentas se hacen acá, en el navegador, solo porque es una demostración: en
 * una tienda de verdad el total lo calcula siempre el servidor.
 */

type Tramo = { desde: number; precio: number };

type Producto = {
  nombre: string;
  /** Cómo se vende: unidad, lote o peso. */
  forma: string;
  unidad: string;
  /** La unidad cuando es una sola: «1 lote», no «1 lotes». */
  singular: string;
  paso: number;
  tramos: Tramo[];
  inicial: number;
};

const PRODUCTOS: Producto[] = [
  {
    nombre: "Cadena de plata 925 · 50 cm",
    forma: "Por unidad",
    unidad: "u.",
    singular: "u.",
    paso: 1,
    tramos: [
      { desde: 1, precio: 12990 },
      { desde: 6, precio: 10990 },
      { desde: 12, precio: 9490 },
    ],
    inicial: 4,
  },
  {
    nombre: "Lote de 10 pulseras surtidas",
    forma: "Por lote",
    unidad: "lotes",
    singular: "lote",
    paso: 1,
    tramos: [
      { desde: 1, precio: 20000 },
      { desde: 3, precio: 18000 },
      { desde: 5, precio: 16500 },
    ],
    inicial: 2,
  },
  {
    nombre: "Plata para fundir",
    forma: "Por gramo",
    unidad: "g",
    singular: "g",
    paso: 5,
    tramos: [
      { desde: 1, precio: 1290 },
      { desde: 50, precio: 1090 },
      { desde: 100, precio: 950 },
    ],
    inicial: 30,
  },
];

/** El tramo que corresponde a una cantidad: el de mayor umbral que no la pasa. */
export function elegirTramo(tramos: Tramo[], cantidad: number): Tramo {
  return tramos.reduce((elegido, tramo) => (cantidad >= tramo.desde ? tramo : elegido), tramos[0]);
}

function siguienteTramo(tramos: Tramo[], cantidad: number): Tramo | undefined {
  return tramos.find((tramo) => tramo.desde > cantidad);
}

export function CotizadorDemo() {
  const [cantidades, setCantidades] = useState(() => PRODUCTOS.map((p) => p.inicial));
  const [folio, setFolio] = useState<string | null>(null);

  const lineas = PRODUCTOS.map((producto, i) => {
    const cantidad = cantidades[i];
    const tramo = elegirTramo(producto.tramos, cantidad);
    const subtotal = tramo.precio * cantidad;
    const sinTramo = producto.tramos[0].precio * cantidad;
    return { producto, cantidad, tramo, subtotal, ahorro: sinTramo - subtotal };
  });

  const total = lineas.reduce((suma, l) => suma + l.subtotal, 0);
  const ahorro = lineas.reduce((suma, l) => suma + l.ahorro, 0);

  // El aviso de conveniencia, como en la tienda: el producto al que le falta
  // menos para bajar de tramo.
  const aviso = lineas
    .map((l) => ({ ...l, siguiente: siguienteTramo(l.producto.tramos, l.cantidad) }))
    .filter((l) => l.cantidad > 0 && l.siguiente)
    .sort((a, b) => a.siguiente!.desde - a.cantidad - (b.siguiente!.desde - b.cantidad))[0];

  function cambiar(indice: number, cantidad: number) {
    setFolio(null);
    setCantidades((previas) => previas.map((c, i) => (i === indice ? Math.max(0, Math.min(cantidad, 999)) : c)));
  }

  function simular() {
    const azar = crypto.getRandomValues(new Uint32Array(1))[0].toString(16).toUpperCase().padStart(8, "0");
    setFolio(`DC-${azar}`);
  }

  return (
    <div className="overflow-hidden rounded-xl border border-arena bg-white shadow-[0_24px_60px_-28px_rgba(20,33,61,.35)]">
      <div className="flex items-center justify-between gap-3 border-b border-arena bg-crema px-5 py-3">
        <div className="flex min-w-0 items-center gap-2.5">
          <span className="flex size-7 flex-none items-center justify-center rounded-md bg-marino font-jakarta text-xs font-extrabold text-white">
            J
          </span>
          <span className="truncate text-sm font-semibold text-marino">Joyería de ejemplo · Pedido mayorista</span>
        </div>
        <span className="inline-flex flex-none items-center gap-1.5 rounded-full border border-ambar bg-trigo px-2.5 py-0.5 text-[11px] font-semibold text-marino">
          <span className="size-1.5 rounded-full bg-ambar" />
          Ejemplo
        </span>
      </div>

      {folio ? (
        <Resumen folio={folio} lineas={lineas} total={total} onVolver={() => setFolio(null)} />
      ) : (
        <>
          <ul className="flex list-none flex-col divide-y divide-arena p-0">
            {lineas.map(({ producto, cantidad, tramo }, i) => (
              <li key={producto.nombre} className="flex flex-col gap-3 px-5 py-4">
                <div className="flex flex-wrap items-start justify-between gap-x-4 gap-y-1">
                  <div className="min-w-0">
                    <p className="font-jakarta text-[15px] font-bold text-marino">{producto.nombre}</p>
                    <p className="text-xs text-pizarra">{producto.forma}</p>
                  </div>
                  <Contador
                    nombre={producto.nombre}
                    cantidad={cantidad}
                    unidad={producto.unidad}
                    paso={producto.paso}
                    onCambiar={(c) => cambiar(i, c)}
                  />
                </div>

                <div className="flex flex-wrap items-center gap-1.5" role="group" aria-label={`Tramos de ${producto.nombre}`}>
                  {producto.tramos.map((t) => {
                    const activo = cantidad > 0 && t === tramo;
                    return (
                      <button
                        key={t.desde}
                        type="button"
                        onClick={() => cambiar(i, t.desde)}
                        aria-pressed={activo}
                        className={cn(
                          "cursor-pointer rounded-md border px-2.5 py-1 text-xs tabular-nums transition-colors motion-reduce:transition-none",
                          activo
                            ? "border-acero bg-acero font-semibold text-white"
                            : "border-arena bg-hueso text-pizarra hover:border-niebla hover:text-marino",
                        )}
                      >
                        {t.desde}+ {producto.unidad} · {formatearPesos(t.precio)}
                      </button>
                    );
                  })}
                </div>
              </li>
            ))}
          </ul>

          <div className="flex flex-col gap-3 border-t border-arena bg-hueso px-5 py-4">
            {aviso?.siguiente && (
              <p className="rounded-lg border border-jade/25 bg-jade-claro px-3 py-2 text-[13px] text-marino">
                Lleva {aviso.siguiente.desde - aviso.cantidad}{" "}
                {aviso.siguiente.desde - aviso.cantidad === 1 ? aviso.producto.singular : aviso.producto.unidad} más de «{aviso.producto.nombre}» y
                pagas {formatearPesos(aviso.siguiente.precio)} cada {aviso.producto.unidad === "g" ? "gramo" : "uno"}.
              </p>
            )}
            <div className="flex flex-wrap items-end justify-between gap-3">
              <div aria-live="polite" className="flex flex-col">
                <span className="text-xs text-pizarra">Total del pedido (neto)</span>
                <span className="font-jakarta text-[28px] leading-tight font-extrabold tracking-[-0.02em] text-marino tabular-nums">
                  {formatearPesos(total)}
                </span>
                {ahorro > 0 && (
                  <span className="text-[13px] font-semibold text-jade tabular-nums">
                    Ahorras {formatearPesos(ahorro)} por cantidad
                  </span>
                )}
              </div>
              <button
                type="button"
                onClick={simular}
                disabled={total === 0}
                className="inline-flex h-11 cursor-pointer items-center justify-center rounded-[10px] bg-acero px-5 text-sm font-semibold text-white hover:bg-acero-hondo disabled:cursor-not-allowed disabled:opacity-50"
              >
                Simular pedido
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function Contador({
  nombre,
  cantidad,
  unidad,
  paso,
  onCambiar,
}: {
  nombre: string;
  cantidad: number;
  unidad: string;
  paso: number;
  onCambiar: (cantidad: number) => void;
}) {
  const boton =
    "flex size-8 cursor-pointer items-center justify-center rounded-md border border-arena bg-white text-base font-semibold text-acero hover:border-acero disabled:cursor-not-allowed disabled:opacity-40";
  return (
    <div className="flex flex-none items-center gap-1.5">
      <button
        type="button"
        className={boton}
        onClick={() => onCambiar(cantidad - paso)}
        disabled={cantidad === 0}
        aria-label={`Quitar ${paso} ${unidad} de ${nombre}`}
      >
        −
      </button>
      <label className="flex items-baseline gap-1">
        <span className="sr-only">Cantidad de {nombre}</span>
        <input
          type="number"
          inputMode="numeric"
          min={0}
          max={999}
          value={cantidad}
          onChange={(evento) => onCambiar(Number.parseInt(evento.target.value || "0", 10) || 0)}
          className="h-8 w-14 rounded-md border border-arena bg-white text-center text-sm font-semibold text-marino tabular-nums [appearance:textfield] focus:border-acero focus:outline-none [&::-webkit-inner-spin-button]:appearance-none"
        />
        <span className="w-8 text-xs text-pizarra">{unidad}</span>
      </label>
      <button
        type="button"
        className={boton}
        onClick={() => onCambiar(cantidad + paso)}
        aria-label={`Agregar ${paso} ${unidad} de ${nombre}`}
      >
        +
      </button>
    </div>
  );
}

function Resumen({
  folio,
  lineas,
  total,
  onVolver,
}: {
  folio: string;
  lineas: { producto: Producto; cantidad: number; tramo: Tramo; subtotal: number }[];
  total: number;
  onVolver: () => void;
}) {
  return (
    <div className="flex flex-col gap-4 px-5 py-5" role="status">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="text-xs text-pizarra">Pedido recibido</p>
          <p className="font-jakarta text-xl font-extrabold text-marino tabular-nums">{folio}</p>
        </div>
        <InsigniaDeEstado estado="PENDIENTE" />
      </div>

      <table className="w-full text-[13px]">
        <tbody>
          {lineas
            .filter((l) => l.cantidad > 0)
            .map((l) => (
              <tr key={l.producto.nombre} className="border-b border-arena last:border-0">
                <td className="py-2 pr-3 text-marino">
                  {l.producto.nombre}
                  <span className="block text-xs text-pizarra tabular-nums">
                    {l.cantidad} {l.producto.unidad} × {formatearPesos(l.tramo.precio)}
                  </span>
                </td>
                <td className="py-2 text-right font-semibold text-marino tabular-nums">{formatearPesos(l.subtotal)}</td>
              </tr>
            ))}
        </tbody>
      </table>

      <div className="flex items-center justify-between rounded-lg bg-hueso px-3 py-2.5">
        <span className="text-sm text-pizarra">Total neto</span>
        <span className="font-jakarta text-lg font-extrabold text-marino tabular-nums">{formatearPesos(total)}</span>
      </div>

      <p className="text-[13px] leading-[1.5] text-pizarra">
        Así le llega al vendedor: con el total calculado, el stock reservado y un botón para seguir la conversación por
        WhatsApp.
      </p>

      <button
        type="button"
        onClick={onVolver}
        className="self-start cursor-pointer text-sm font-semibold text-acero underline underline-offset-2 hover:text-acero-hondo"
      >
        Volver a cotizar
      </button>
    </div>
  );
}
