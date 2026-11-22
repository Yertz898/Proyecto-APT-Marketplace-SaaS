"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { cambiarEstadoDePedido, obtenerPedidos } from "@/lib/api/pedidos";
import { formatearFecha, formatearPesos } from "@/lib/formato";
import type { EstadoPedido, PedidoDelPanel } from "@/lib/tipos-panel";
import { cn } from "@/lib/utils";

import { InsigniaDeEstado } from "./estado-pedido";
import { Cabecera, Cargando, Error as Aviso, Vacio } from "./piezas";

/*
 * La bandeja de pedidos del dueño.
 *
 * El pago no pasa por la plataforma: la tienda lo coordina por WhatsApp. Así
 * que esta pantalla no cobra nada, sirve para seguir en qué va cada pedido y
 * tener a mano con quién hablar.
 *
 * Los precios que se muestran son los que se cobraron, guardados en el pedido
 * al confirmarlo. No se leen del catálogo: subir un precio no puede reescribir
 * lo que alguien ya pagó.
 *
 * Arriba van los filtros por estado, con cuántos hay en cada uno, y un buscador
 * por folio o cliente. Cada pedido es una fila que se abre para ver el detalle
 * y moverlo de estado: con decenas de pedidos, una tarjeta abierta por cada
 * uno no se recorre.
 */

/**
 * A qué estados puede pasar un pedido desde donde está.
 *
 * Un pedido entregado o cancelado no se mueve más: deshacer una entrega o
 * revivir una anulación son correcciones de historia, y para eso no alcanza
 * un botón sin registro de quién lo hizo.
 */
const SIGUIENTES: Record<EstadoPedido, EstadoPedido[]> = {
  PENDIENTE: ["CONFIRMADO", "CANCELADO"],
  CONFIRMADO: ["ENTREGADO", "CANCELADO"],
  ENTREGADO: [],
  CANCELADO: [],
};

const NOMBRE_DEL_PASO: Record<EstadoPedido, string> = {
  PENDIENTE: "Volver a pendiente",
  CONFIRMADO: "Confirmar",
  ENTREGADO: "Marcar entregado",
  CANCELADO: "Anular",
};

const POR_PAGINA = 50;

const FILTROS: { valor: EstadoPedido | "TODOS"; etiqueta: string }[] = [
  { valor: "TODOS", etiqueta: "Todos" },
  { valor: "PENDIENTE", etiqueta: "Por coordinar" },
  { valor: "CONFIRMADO", etiqueta: "Confirmados" },
  { valor: "ENTREGADO", etiqueta: "Entregados" },
  { valor: "CANCELADO", etiqueta: "Anulados" },
];

export function PantallaPedidos() {
  const [pedidos, setPedidos] = useState<PedidoDelPanel[] | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);
  const [ocupado, setOcupado] = useState<number | null>(null);
  const [filtro, setFiltro] = useState<EstadoPedido | "TODOS">("TODOS");
  const [busqueda, setBusqueda] = useState("");
  const [abierto, setAbierto] = useState<number | null>(null);
  // Se dibujan de a 50: una tienda con años de historial tiene miles.
  const [limite, setLimite] = useState(POR_PAGINA);

  const cargar = useCallback(() => {
    obtenerPedidos()
      .then((suyos) => {
        setPedidos(suyos);
        setFallo(null);
      })
      .catch((error: unknown) =>
        setFallo(error instanceof Error ? error.message : "No pudimos cargar tus pedidos."),
      );
  }, []);

  useEffect(cargar, [cargar]);

  async function cambiar(pedido: PedidoDelPanel, estado: EstadoPedido) {
    setOcupado(pedido.id);
    try {
      const actualizado = await cambiarEstadoDePedido(pedido.id, estado);
      setPedidos((previos) => (previos ?? []).map((uno) => (uno.id === actualizado.id ? actualizado : uno)));
      setFallo(null);
    } catch (error) {
      setFallo(error instanceof Error ? error.message : "No pudimos cambiar el estado.");
    } finally {
      setOcupado(null);
    }
  }

  const conteo = useMemo(() => {
    const cuenta: Record<string, number> = { TODOS: pedidos?.length ?? 0 };
    for (const pedido of pedidos ?? []) cuenta[pedido.estado] = (cuenta[pedido.estado] ?? 0) + 1;
    return cuenta;
  }, [pedidos]);

  const visibles = useMemo(() => {
    const texto = busqueda.trim().toLowerCase();
    return (pedidos ?? []).filter(
      (p) =>
        (filtro === "TODOS" || p.estado === filtro) &&
        (!texto || p.folio.toLowerCase().includes(texto) || p.nombreContacto.toLowerCase().includes(texto)),
    );
  }, [pedidos, filtro, busqueda]);

  const cabecera = (
    <Cabecera titulo="Pedidos" descripcion="Qué te pidieron y en qué va cada uno." />
  );

  if (fallo && pedidos === null) {
    return (
      <>
        {cabecera}
        <Aviso mensaje={fallo} onReintentar={cargar} />
      </>
    );
  }

  if (pedidos === null) {
    return (
      <>
        {cabecera}
        <Cargando texto="Cargando tus pedidos…" />
      </>
    );
  }

  if (pedidos.length === 0) {
    return (
      <>
        {cabecera}
        <Vacio
          titulo="Todavía no te han pedido nada"
          detalle="Cuando alguien confirme un pedido en tu vitrina, aparece acá con sus datos de contacto."
        />
      </>
    );
  }

  return (
    <>
      {cabecera}

      {fallo && (
        <div className="mb-4">
          <Aviso mensaje={fallo} />
        </div>
      )}

      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div role="tablist" aria-label="Filtrar por estado" className="flex flex-wrap gap-1.5">
          {FILTROS.map((f) => (
            <button
              key={f.valor}
              type="button"
              role="tab"
              aria-selected={filtro === f.valor}
              onClick={() => {
                setFiltro(f.valor);
                setLimite(POR_PAGINA);
              }}
              className={cn(
                "inline-flex h-9 cursor-pointer items-center gap-1.5 rounded-lg border px-3 text-[13px] font-semibold transition-colors motion-reduce:transition-none",
                filtro === f.valor
                  ? "border-marino bg-marino text-white"
                  : "border-arena bg-white text-marino hover:border-niebla",
              )}
            >
              {f.etiqueta}
              <span
                className={cn(
                  "rounded-full px-1.5 text-[11px] tabular-nums",
                  filtro === f.valor ? "bg-white/20" : "bg-hueso text-pizarra",
                )}
              >
                {conteo[f.valor] ?? 0}
              </span>
            </button>
          ))}
        </div>

        <label className="relative w-full max-w-[280px]">
          <span className="sr-only">Buscar por folio o cliente</span>
          <svg
            className="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 text-pizarra"
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            aria-hidden="true"
          >
            <circle cx="11" cy="11" r="7" />
            <path d="M20 20l-3.5-3.5" />
          </svg>
          <input
            type="search"
            value={busqueda}
            onChange={(e) => {
              setBusqueda(e.target.value);
              setLimite(POR_PAGINA);
            }}
            placeholder="Buscar folio o cliente"
            className="h-9 w-full rounded-lg border border-arena bg-white pr-3 pl-9 text-[13.5px] text-marino placeholder:text-pizarra focus:border-acero focus:outline-none"
          />
        </label>
      </div>

      <div className="overflow-hidden rounded-xl border border-arena bg-white">
        <div className="hidden grid-cols-[minmax(0,1.3fr)_minmax(0,1fr)_auto_auto] gap-4 border-b border-arena bg-hueso px-5 py-2.5 text-[12px] font-semibold tracking-[0.03em] text-pizarra uppercase @3xl:grid">
          <span>Cliente</span>
          <span>Folio y fecha</span>
          <span className="w-[110px] text-right">Total</span>
          <span className="w-[170px] text-right">Estado</span>
        </div>

        {visibles.length === 0 ? (
          <p className="px-5 py-10 text-center text-[14px] text-pizarra">Ningún pedido coincide con el filtro.</p>
        ) : (
          <ul className="flex list-none flex-col divide-y divide-arena p-0">
            {visibles.slice(0, limite).map((pedido) => (
              <FilaDePedido
                key={pedido.id}
                pedido={pedido}
                abierto={abierto === pedido.id}
                onAlternar={() => setAbierto((actual) => (actual === pedido.id ? null : pedido.id))}
                ocupado={ocupado === pedido.id}
                onCambiar={(estado) => cambiar(pedido, estado)}
              />
            ))}
          </ul>
        )}
      </div>

      {visibles.length > limite && (
        <button
          type="button"
          onClick={() => setLimite((l) => l + POR_PAGINA)}
          className="mx-auto mt-4 flex h-10 cursor-pointer items-center rounded-lg border border-arena bg-white px-4 text-[13px] font-semibold text-acero hover:border-acero"
        >
          Mostrar más ({visibles.length - limite} restantes)
        </button>
      )}
    </>
  );
}

function FilaDePedido({
  pedido,
  abierto,
  onAlternar,
  ocupado,
  onCambiar,
}: {
  pedido: PedidoDelPanel;
  abierto: boolean;
  onAlternar: () => void;
  ocupado: boolean;
  onCambiar: (estado: EstadoPedido) => void;
}) {
  const idDetalle = `pedido-${pedido.id}`;
  return (
    <li className={cn(abierto && "bg-crema")}>
      <button
        type="button"
        onClick={onAlternar}
        aria-expanded={abierto}
        aria-controls={idDetalle}
        className="grid w-full cursor-pointer grid-cols-[minmax(0,1fr)_auto] items-center gap-x-4 gap-y-1 px-5 py-3.5 text-left hover:bg-hueso @3xl:grid-cols-[minmax(0,1.3fr)_minmax(0,1fr)_auto_auto]"
      >
        <span className="min-w-0">
          <span className="block truncate text-[14px] font-semibold text-marino">{pedido.nombreContacto}</span>
          <span className="block truncate text-[12.5px] text-pizarra">{pedido.telefonoContacto}</span>
        </span>
        <span className="hidden min-w-0 @3xl:block">
          <span className="block text-[13px] font-semibold text-marino tabular-nums">{pedido.folio}</span>
          <span className="block text-[12.5px] text-pizarra">{formatearFecha(pedido.creadoEn)}</span>
        </span>
        <span className="text-right text-[14px] font-semibold text-marino tabular-nums @3xl:w-[110px]">
          {formatearPesos(pedido.total)}
        </span>
        <span className="col-span-2 flex items-center justify-between gap-2 @3xl:col-span-1 @3xl:w-[170px] @3xl:justify-end">
          <span className="text-[12px] text-pizarra tabular-nums @3xl:hidden">
            {pedido.folio} · {formatearFecha(pedido.creadoEn)}
          </span>
          <InsigniaDeEstado estado={pedido.estado}>{pedido.estadoVisible}</InsigniaDeEstado>
        </span>
      </button>

      {abierto && (
        <div id={idDetalle} className="grid gap-4 border-t border-arena px-5 py-4 @3xl:grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)]">
          <div>
            <p className="mb-2 text-[12px] font-semibold tracking-[0.03em] text-pizarra uppercase">Detalle</p>
            <ul className="flex list-none flex-col gap-1 p-0">
              {pedido.lineas.map((linea) => (
                <li key={linea.id} className="flex justify-between gap-4 text-[13.5px]">
                  <span className="text-pizarra">
                    {sinCerosDeAdorno(linea.cantidad)} × {linea.productoNombre}
                  </span>
                  <span className="shrink-0 text-marino tabular-nums">{formatearPesos(linea.subtotalNeto)}</span>
                </li>
              ))}
            </ul>
            <p className="mt-2 border-t border-arena pt-2 text-right text-[12.5px] text-pizarra tabular-nums">
              {formatearPesos(pedido.totalNeto)} neto + {formatearPesos(pedido.totalIva)} IVA ={" "}
              <span className="font-semibold text-marino">{formatearPesos(pedido.total)}</span>
            </p>
          </div>

          <div className="flex flex-col gap-2 text-[13.5px]">
            <p className="text-[12px] font-semibold tracking-[0.03em] text-pizarra uppercase">Contacto</p>
            <p className="text-marino">{pedido.nombreContacto}</p>
            <p className="text-pizarra">
              {pedido.telefonoContacto}
              {pedido.emailContacto && ` · ${pedido.emailContacto}`}
            </p>
            {pedido.direccionEntrega && <p className="text-pizarra">{pedido.direccionEntrega}</p>}
            {pedido.notas && (
              <p className="rounded-lg border border-arena bg-hueso px-3 py-2 text-xs leading-[1.5] text-pizarra">
                {pedido.notas}
              </p>
            )}
          </div>

          {SIGUIENTES[pedido.estado].length > 0 && (
            <div className="flex flex-wrap items-center gap-2.5 border-t border-arena pt-3.5 @3xl:col-span-2">
              {SIGUIENTES[pedido.estado].map((estado) => (
                <button
                  key={estado}
                  type="button"
                  disabled={ocupado}
                  onClick={() => onCambiar(estado)}
                  className={cn(
                    "h-10 cursor-pointer rounded-[10px] border px-4 text-[13px] font-semibold disabled:cursor-not-allowed disabled:opacity-60",
                    estado === "CANCELADO"
                      ? "border-arena bg-white text-pizarra hover:border-ambar hover:text-ambar-hondo"
                      : "border-acero bg-acero text-white hover:bg-acero-hondo",
                  )}
                >
                  {NOMBRE_DEL_PASO[estado]}
                </button>
              ))}
              <p className="text-xs text-pizarra">Anular devuelve el inventario reservado.</p>
            </div>
          )}
        </div>
      )}
    </li>
  );
}

/**
 * «2.00» se lee «2»; «166.50» se lee «166,5».
 *
 * La cantidad viaja como decimal porque un producto por peso se cuenta en
 * gramos con decimales, pero mostrar «2,00 lotes» parece un error de la
 * pantalla.
 */
function sinCerosDeAdorno(cantidad: string): string {
  const numero = Number(cantidad);
  if (!Number.isFinite(numero)) {
    return cantidad;
  }
  return numero.toLocaleString("es-CL", { maximumFractionDigits: 3 });
}
