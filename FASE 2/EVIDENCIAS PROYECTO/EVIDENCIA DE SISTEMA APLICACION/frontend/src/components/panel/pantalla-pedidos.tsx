"use client";

import { useCallback, useEffect, useState } from "react";

import { cambiarEstadoDePedido, obtenerPedidos } from "@/lib/api/pedidos";
import { formatearFecha, formatearPesos } from "@/lib/formato";
import type { EstadoPedido, PedidoDelPanel } from "@/lib/tipos-panel";
import { cn } from "@/lib/utils";

import { Cabecera, Cargando, Error as Aviso, Tarjeta, Vacio } from "./piezas";

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
 */

const ETIQUETA: Record<EstadoPedido, string> = {
  PENDIENTE: "border-ambar bg-trigo text-ambar-hondo",
  CONFIRMADO: "border-niebla bg-cielo text-acero",
  ENTREGADO: "border-arena bg-hueso text-pizarra",
  CANCELADO: "border-niebla bg-hueso text-pizarra",
};

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

export function PantallaPedidos() {
  const [pedidos, setPedidos] = useState<PedidoDelPanel[] | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);
  const [ocupado, setOcupado] = useState<number | null>(null);

  const cargar = useCallback(() => {
    obtenerPedidos()
      .then((suyos) => {
        setPedidos(suyos);
        setFallo(null);
      })
      .catch((error: unknown) =>
        setFallo(
          error instanceof Error ? error.message : "No pudimos cargar tus pedidos.",
        ),
      );
  }, []);

  useEffect(cargar, [cargar]);

  async function cambiar(pedido: PedidoDelPanel, estado: EstadoPedido) {
    setOcupado(pedido.id);
    try {
      const actualizado = await cambiarEstadoDePedido(pedido.id, estado);
      setPedidos((previos) =>
        (previos ?? []).map((uno) => (uno.id === actualizado.id ? actualizado : uno)),
      );
      setFallo(null);
    } catch (error) {
      setFallo(
        error instanceof Error ? error.message : "No pudimos cambiar el estado.",
      );
    } finally {
      setOcupado(null);
    }
  }

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

      {fallo && <Aviso mensaje={fallo} />}

      <div className="mt-4 flex flex-col gap-3">
        {pedidos.map((pedido) => (
          <Tarjeta key={pedido.id}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <div className="flex items-center gap-2.5">
                  <p className="font-mono text-[13px] font-semibold text-marino">
                    {pedido.folio}
                  </p>
                  <span
                    className={cn(
                      "rounded-full border px-2 py-0.5 text-[11px] font-semibold",
                      ETIQUETA[pedido.estado],
                    )}
                  >
                    {pedido.estadoVisible}
                  </span>
                </div>
                <p className="mt-1.5 text-[13px] text-pizarra">
                  {pedido.nombreContacto} · {pedido.telefonoContacto}
                </p>
                <p className="mt-0.5 text-xs text-pizarra">
                  {formatearFecha(pedido.creadoEn)}
                  {pedido.direccionEntrega && ` · ${pedido.direccionEntrega}`}
                </p>
              </div>

              <div className="text-right">
                <p className="text-[15px] font-semibold text-marino">
                  {formatearPesos(pedido.total)}
                </p>
                <p className="text-xs text-pizarra">
                  {formatearPesos(pedido.totalNeto)} neto + {formatearPesos(pedido.totalIva)} IVA
                </p>
              </div>
            </div>

            <ul className="mt-3.5 flex flex-col gap-1 border-t border-arena pt-3.5">
              {pedido.lineas.map((linea) => (
                <li key={linea.id} className="flex justify-between gap-4 text-[13px]">
                  <span className="text-pizarra">
                    {sinCerosDeAdorno(linea.cantidad)} × {linea.productoNombre}
                  </span>
                  <span className="shrink-0 text-marino">
                    {formatearPesos(linea.subtotalNeto)}
                  </span>
                </li>
              ))}
            </ul>

            {pedido.notas && (
              <p className="mt-3 rounded-[10px] border border-arena bg-hueso px-3 py-2 text-xs leading-[1.5] text-pizarra">
                {pedido.notas}
              </p>
            )}

            {SIGUIENTES[pedido.estado].length > 0 && (
              <div className="mt-3.5 flex flex-wrap gap-2.5 border-t border-arena pt-3.5">
                {SIGUIENTES[pedido.estado].map((estado) => (
                  <button
                    key={estado}
                    type="button"
                    disabled={ocupado === pedido.id}
                    onClick={() => cambiar(pedido, estado)}
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
                {pedido.estado !== "CANCELADO" && (
                  <p className="self-center text-xs text-pizarra">
                    Anular devuelve el inventario reservado.
                  </p>
                )}
              </div>
            )}
          </Tarjeta>
        ))}
      </div>
    </>
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
