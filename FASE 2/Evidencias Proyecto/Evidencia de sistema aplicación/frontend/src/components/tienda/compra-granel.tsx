"use client";

import { useState } from "react";

import { cotizarGranel } from "@/lib/api/catalogo";
import { formatearGramos, formatearPesos } from "@/lib/formato";
import type { CotizacionGranel, LineaGranel } from "@/lib/tipos";

import { useCarrito } from "./carrito";
import { TablaDeTramos } from "./tabla-tramos";

/*
 * Compra por gramos.
 *
 * El precio lo calcula siempre el backend: acá se pide una cotización y se
 * muestra lo que devuelve, incluido el aviso de conveniencia y el rechazo por
 * no alcanzar el mínimo. El navegador no hace aritmética de dinero.
 */
export function CompraGranel({ slugTienda, linea }: { slugTienda: string; linea: LineaGranel }) {
  const { agregarGranel } = useCarrito();
  const [gramos, setGramos] = useState("");
  const [cotizacion, setCotizacion] = useState<CotizacionGranel | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cotizando, setCotizando] = useState(false);

  // El comprador escribe con coma decimal, como se usa en Chile.
  const cantidad = Number(gramos.replace(",", "."));
  const cantidadValida = Number.isFinite(cantidad) && cantidad > 0;

  async function cotizar() {
    if (!cantidadValida) return;

    setCotizando(true);
    setError(null);
    try {
      setCotizacion(await cotizarGranel(slugTienda, linea.codigo, cantidad));
    } catch (problema) {
      setCotizacion(null);
      setError(problema instanceof Error ? problema.message : "No se pudo cotizar.");
    } finally {
      setCotizando(false);
    }
  }

  const puedeAgregar = cotizacion !== null && cotizacion.rechazo === null;

  return (
    <div className="flex flex-col gap-5">
      <TablaDeTramos tramos={linea.tramos} activo={cotizacion?.tramoAplicado ?? null} />

      {linea.minimo && <p className="text-[13px] text-texto-suave">{linea.minimo}</p>}

      <div>
        <label htmlFor="gramos" className="text-[13px] font-semibold text-texto">
          Cantidad en gramos
        </label>
        <div className="mt-2 flex flex-wrap items-center gap-3">
          <input
            id="gramos"
            inputMode="decimal"
            value={gramos}
            onChange={(evento) => setGramos(evento.target.value)}
            placeholder="0,0"
            className="h-12 w-40 rounded-xl border border-lila/20 bg-superficie px-4 text-base text-texto outline-none focus-visible:border-lila"
          />
          <button
            type="button"
            disabled={!cantidadValida || cotizando}
            onClick={cotizar}
            className="h-12 cursor-pointer rounded-full border border-lila/40 px-6 text-sm font-medium text-texto transition-colors hover:bg-violeta/18 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {cotizando ? "Calculando…" : "Calcular precio"}
          </button>
        </div>
      </div>

      {error && (
        <p role="alert" className="rounded-xl border border-oro/28 bg-oro/8 p-3.5 text-[13px] leading-[1.6] text-texto-suave">
          {error}
        </p>
      )}

      {cotizacion && (
        <div className="flex flex-col gap-3 rounded-xl border border-lila/16 p-4">
          <p className="text-[13px] text-texto-suave">
            {formatearGramos(cotizacion.gramos)} a {formatearPesos(cotizacion.precioGramoNeto)} por gramo
          </p>
          <dl className="flex flex-col gap-1.5 text-[13px]">
            <Linea termino="Neto" valor={formatearPesos(cotizacion.neto)} />
            <Linea termino="IVA" valor={formatearPesos(cotizacion.iva)} />
            <Linea termino="Total" valor={formatearPesos(cotizacion.total)} destacado />
          </dl>

          {cotizacion.aviso && (
            <p className="rounded-lg border border-oro/28 bg-oro/8 p-3 text-[13px] text-texto-suave">
              {cotizacion.aviso}
            </p>
          )}
        </div>
      )}

      {cotizacion?.rechazo && (
        <p role="alert" className="text-[13px] text-texto-suave">
          {cotizacion.rechazo}
        </p>
      )}

      <button
        type="button"
        disabled={!puedeAgregar}
        onClick={() => cotizacion && agregarGranel(linea.codigo, cotizacion.gramos)}
        className="h-[54px] cursor-pointer rounded-full bg-violeta text-[15px] font-semibold text-white transition-colors hover:bg-violeta-hover disabled:cursor-not-allowed disabled:opacity-50"
      >
        Agregar al carrito
      </button>
    </div>
  );
}

function Linea({ termino, valor, destacado = false }: { termino: string; valor: string; destacado?: boolean }) {
  return (
    <div className="flex justify-between">
      <dt className="text-texto-suave">{termino}</dt>
      <dd className={destacado ? "font-semibold text-texto" : "text-texto"}>{valor}</dd>
    </div>
  );
}
