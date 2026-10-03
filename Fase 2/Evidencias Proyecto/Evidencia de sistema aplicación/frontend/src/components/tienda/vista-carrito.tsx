"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { confirmarPedido, cotizarCarrito } from "@/lib/api/carrito";
import { formatearGramos, formatearPesos } from "@/lib/formato";
import type { CarritoCotizado, LineaCarrito, PedidoConfirmado } from "@/lib/tipos";

import { useCarrito } from "./carrito";
import { EnlaceExterno } from "./enlace-externo";

/*
 * Carrito y checkout simulado.
 *
 * El carrito mezcla lotes (unidad: lote) y granel (unidad: gramo), y cada línea
 * muestra su unidad. Los totales vienen del backend, que también dice cuánto
 * falta para el siguiente tramo por cantidad de lotes.
 *
 * Al confirmar no se cobra nada: se genera el pedido y el pago se coordina por
 * fuera (CONVENCIONES.md > Pedido).
 */
export function VistaCarrito({ slugTienda }: { slugTienda: string }) {
  const { lineas, quitar, vaciar } = useCarrito();
  const [cotizacion, setCotizacion] = useState<CarritoCotizado | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pedido, setPedido] = useState<PedidoConfirmado | null>(null);
  const [confirmando, setConfirmando] = useState(false);

  // El carrito se cotiza cada vez que cambia: los totales y el aviso del
  // próximo tramo los calcula el backend, no el navegador.
  useEffect(() => {
    if (lineas.length === 0) {
      return;
    }

    let vigente = true;

    cotizarCarrito(slugTienda, lineas)
      .then((resultado) => {
        if (!vigente) return;
        setCotizacion(resultado);
        setError(null);
      })
      .catch((problema: unknown) => {
        if (!vigente) return;
        setCotizacion(null);
        setError(problema instanceof Error ? problema.message : "No se pudo cotizar el carrito.");
      });

    return () => {
      vigente = false;
    };
  }, [lineas, slugTienda]);

  async function confirmar() {
    setConfirmando(true);
    try {
      setPedido(await confirmarPedido(slugTienda, lineas));
      setError(null);
      vaciar();
    } catch (problema) {
      setError(problema instanceof Error ? problema.message : "No se pudo confirmar el pedido.");
    } finally {
      setConfirmando(false);
    }
  }

  if (pedido) {
    return (
      <div className="rounded-2xl border border-lila/16 p-6">
        <h2 className="font-serif text-[26px] text-texto">Pedido {pedido.numero}</h2>
        <p className="mt-2 text-sm leading-[1.6] text-texto-suave">{pedido.mensaje}</p>
        {pedido.enlaceWhatsapp && (
          <EnlaceExterno
            enlace={pedido.enlaceWhatsapp}
            className="mt-5 flex h-12 w-full max-w-xs items-center justify-center rounded-full bg-violeta text-sm font-semibold text-white"
          >
            Coordinar el pago por WhatsApp
          </EnlaceExterno>
        )}
      </div>
    );
  }

  if (lineas.length === 0) {
    return (
      <div className="rounded-2xl border border-lila/12 bg-superficie p-6">
        <p className="text-sm text-texto-suave">Tu carrito está vacío.</p>
        <div className="mt-4 flex gap-3">
          <Link href={`/t/${slugTienda}/lotes`} className="text-[13px] text-lila">
            Ver lotes
          </Link>
          <Link href={`/t/${slugTienda}/granel`} className="text-[13px] text-lila">
            Ver granel
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_340px] lg:items-start">
      <ul className="flex flex-col gap-3">
        {lineas.map((linea, indice) => (
          <li
            key={`${linea.tipo}-${linea.codigo}`}
            className="flex items-start justify-between gap-4 rounded-xl border border-lila/12 bg-superficie p-4"
          >
            <div>
              <p className="text-sm text-texto">{nombreDeLinea(cotizacion, indice, linea)}</p>
              <p className="mt-1 text-xs text-texto-suave">{detalleDeLinea(cotizacion, indice, linea)}</p>
              {cotizacion?.lineas[indice]?.rechazo && (
                <p role="alert" className="mt-2 text-xs text-oro">
                  {cotizacion.lineas[indice].rechazo}
                </p>
              )}
            </div>

            <div className="flex flex-none flex-col items-end gap-2">
              {cotizacion?.lineas[indice] && (
                <span className="text-sm text-texto">{formatearPesos(cotizacion.lineas[indice].neto)}</span>
              )}
              <button
                type="button"
                onClick={() => quitar(indice)}
                className="cursor-pointer text-xs text-texto-suave transition-colors hover:text-texto"
              >
                Quitar
              </button>
            </div>
          </li>
        ))}
      </ul>

      <aside className="rounded-2xl border border-lila/16 p-5">
        <h2 className="text-[13px] font-semibold text-texto">Resumen</h2>

        {cotizacion ? (
          <dl className="mt-4 flex flex-col gap-1.5 text-[13px]">
            <Fila termino="Neto" valor={formatearPesos(cotizacion.neto)} />
            <Fila termino="IVA" valor={formatearPesos(cotizacion.iva)} />
            <Fila termino="Total" valor={formatearPesos(cotizacion.total)} destacado />
          </dl>
        ) : (
          <p className="mt-4 text-[13px] leading-[1.6] text-texto-suave">
            {error ?? "Calculando el total…"}
          </p>
        )}

        {cotizacion?.avisoTramo && (
          <p className="mt-4 rounded-lg border border-oro/28 bg-oro/8 p-3 text-xs leading-[1.5] text-texto-suave">
            {cotizacion.avisoTramo}
          </p>
        )}

        {cotizacion?.rechazo && (
          <p role="alert" className="mt-4 text-xs text-texto-suave">
            {cotizacion.rechazo}
          </p>
        )}

        <button
          type="button"
          disabled={confirmando || cotizacion === null || cotizacion.rechazo !== null}
          onClick={confirmar}
          className="mt-5 h-12 w-full cursor-pointer rounded-full bg-violeta text-sm font-semibold text-white transition-colors hover:bg-violeta-hover disabled:cursor-not-allowed disabled:opacity-50"
        >
          {confirmando ? "Confirmando…" : "Confirmar pedido"}
        </button>

        <p className="mt-3 text-center text-xs text-texto-suave">
          No se cobra en línea: el pago se coordina al confirmar.
        </p>
      </aside>
    </div>
  );
}

/** Mientras no haya cotización, se muestra el código elegido. */
function nombreDeLinea(cotizacion: CarritoCotizado | null, indice: number, linea: LineaCarrito): string {
  return cotizacion?.lineas[indice]?.nombre ?? linea.codigo;
}

function detalleDeLinea(cotizacion: CarritoCotizado | null, indice: number, linea: LineaCarrito): string {
  const delBackend = cotizacion?.lineas[indice]?.detalle;
  if (delBackend) {
    return delBackend;
  }
  if (linea.tipo === "lote") {
    return `${linea.cantidad} ${linea.cantidad === 1 ? "lote" : "lotes"}`;
  }
  return formatearGramos(linea.gramos);
}

function Fila({ termino, valor, destacado = false }: { termino: string; valor: string; destacado?: boolean }) {
  return (
    <div className="flex justify-between">
      <dt className="text-texto-suave">{termino}</dt>
      <dd className={destacado ? "font-semibold text-texto" : "text-texto"}>{valor}</dd>
    </div>
  );
}
