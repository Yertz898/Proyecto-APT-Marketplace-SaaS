"use client";

import Image from "next/image";
import { useState } from "react";

import { cotizar } from "@/lib/api/catalogo";
import { formatearCantidad, formatearPesos } from "@/lib/formato";
import type { Cotizacion, Producto } from "@/lib/tipos";

import { useCarrito } from "./carrito";
import { InsigniaDisponibilidad } from "./disponibilidad";
import { TablaDeTramos } from "./tabla-tramos";

/*
 * La ficha de un producto, con su selector de cantidad.
 *
 * Antes eran dos pantallas: una para el lote, que se agregaba de a uno, y otra
 * para el granel, donde había que escribir los gramos. Son el mismo gesto —
 * elegir cuánto— y lo único que cambia es la unidad, que viene en el producto.
 *
 * El precio lo calcula siempre el backend. Acá no se multiplica nada: el tramo
 * que se aplica depende del pedido y el stock puede agotarse mientras el
 * comprador decide.
 */
export function FichaProducto({ producto }: { producto: Producto }) {
  const { agregar, slugTienda } = useCarrito();

  const [cantidad, setCantidad] = useState(() => String(producto.cantidadMinima));
  const [cotizacion, setCotizacion] = useState<Cotizacion | null>(null);
  const [calculando, setCalculando] = useState(false);
  const [fallo, setFallo] = useState<string | null>(null);
  const [agregado, setAgregado] = useState(false);

  const numero = leerCantidad(cantidad);
  const agotado = producto.disponibilidad.tipo === "agotado";

  async function calcular() {
    if (numero === null) {
      setFallo("Escribe una cantidad.");
      return;
    }

    setCalculando(true);
    setFallo(null);
    try {
      setCotizacion(await cotizar(slugTienda, producto.codigo, numero));
    } catch (error: unknown) {
      setCotizacion(null);
      setFallo(error instanceof Error ? error.message : "No pudimos calcular el precio.");
    } finally {
      setCalculando(false);
    }
  }

  function alCarrito() {
    if (numero === null) return;
    agregar(producto.codigo, numero);
    setAgregado(true);
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_360px] lg:items-start">
      <div>
        {producto.foto && (
          <Image
            src={producto.foto.url}
            alt={producto.foto.alt}
            width={760}
            height={500}
            className="mb-6 w-full rounded-[18px] object-cover"
          />
        )}

        <div className="flex items-start justify-between gap-4">
          <h1 className="font-serif text-[30px] leading-[1.15] text-texto">{producto.nombre}</h1>
          <InsigniaDisponibilidad disponibilidad={producto.disponibilidad} />
        </div>

        {producto.descripcion && (
          <p className="mt-2 text-sm leading-[1.6] text-texto-suave">{producto.descripcion}</p>
        )}

        {producto.composicion.length > 0 && (
          <section className="mt-7">
            <h2 className="text-[13px] font-semibold text-texto">Qué trae</h2>
            <ul className="mt-3 flex list-none flex-wrap gap-2 p-0">
              {producto.composicion.map((parte) => (
                <li
                  key={parte.categoria}
                  className="rounded-lg border border-lila/16 px-3 py-1.5 text-[13px] text-texto-suave"
                >
                  <span className="text-texto">{parte.cantidad}</span> {parte.categoria}
                </li>
              ))}
            </ul>
            {producto.piezasTotales !== null && (
              <p className="mt-3 text-xs text-texto-suave">
                {producto.piezasTotales} piezas en total. Los modelos pueden variar según
                disponibilidad.
              </p>
            )}
          </section>
        )}

        {producto.tramos.length > 0 && (
          <section className="mt-7">
            <TablaDeTramos
              tramos={producto.tramos}
              unidad={producto.unidadMedida}
              activo={cotizacion?.tramoAplicado ?? null}
            />
          </section>
        )}
      </div>

      <aside className="rounded-[18px] border border-lila/12 bg-superficie p-6">
        <p className="font-serif text-[26px] font-semibold text-oro">
          {formatearPesos(producto.precioNeto)}
        </p>
        <p className="text-[12px] text-texto-suave">
          {producto.unidadMedida === "unidad"
            ? "neto por unidad"
            : `neto por ${producto.unidadMedida}`}
          {" · "}
          {formatearPesos(producto.precioTotal)} con IVA
        </p>

        {producto.minimo && (
          <p className="mt-3 text-[13px] text-texto-suave">{producto.minimo}</p>
        )}

        <label htmlFor="cantidad" className="mt-5 block text-[13px] font-semibold text-texto">
          Cantidad
          {producto.unidadMedida !== "unidad" && ` en ${producto.unidadMedida}`}
        </label>
        <input
          id="cantidad"
          type="text"
          inputMode="decimal"
          value={cantidad}
          disabled={agotado}
          onChange={(evento) => {
            setCantidad(evento.target.value);
            setCotizacion(null);
            setAgregado(false);
          }}
          className="mt-2 h-12 w-full rounded-[12px] border border-lila/20 bg-superficie px-4 text-base text-texto outline-none focus-visible:border-lila disabled:opacity-50"
        />

        <button
          type="button"
          disabled={agotado || calculando}
          onClick={calcular}
          className="mt-3 h-11 w-full cursor-pointer rounded-full border border-lila/40 bg-transparent text-sm font-medium text-texto transition-colors hover:bg-violeta/18 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {calculando ? "Calculando…" : "Calcular precio"}
        </button>

        {fallo && (
          <p role="alert" className="mt-3 text-[13px] text-oro">
            {fallo}
          </p>
        )}

        {cotizacion?.rechazo && (
          <p role="alert" className="mt-3 rounded-xl border border-oro/28 bg-oro/8 p-3 text-[13px] text-texto-suave">
            {cotizacion.rechazo}
          </p>
        )}

        {cotizacion && !cotizacion.rechazo && (
          <div className="mt-4 rounded-xl border border-lila/16 p-4">
            <p className="text-[13px] text-texto-suave">
              {formatearCantidad(cotizacion.cantidad, producto.unidadMedida)} a{" "}
              {formatearPesos(cotizacion.precioUnitario)}
            </p>
            <dl className="mt-3 flex flex-col gap-1.5 text-[13px]">
              <Fila termino="Neto" valor={formatearPesos(cotizacion.neto)} />
              <Fila termino="IVA" valor={formatearPesos(cotizacion.iva)} />
              <Fila termino="Total" valor={formatearPesos(cotizacion.total)} destacado />
            </dl>

            {cotizacion.aviso && (
              <p className="mt-3 text-[12px] text-oro">{cotizacion.aviso}</p>
            )}
          </div>
        )}

        <button
          type="button"
          disabled={agotado || numero === null || Boolean(cotizacion?.rechazo)}
          onClick={alCarrito}
          className="mt-4 h-12 w-full cursor-pointer rounded-full bg-violeta text-sm font-semibold text-white transition-colors hover:bg-violeta-hover disabled:cursor-not-allowed disabled:opacity-50"
        >
          {agotado ? "Sin existencias" : "Agregar al carrito"}
        </button>

        {agregado && (
          <p role="status" className="mt-3 text-center text-[13px] text-texto-suave">
            Agregado al carrito.
          </p>
        )}
      </aside>
    </div>
  );
}

function Fila({
  termino,
  valor,
  destacado = false,
}: {
  termino: string;
  valor: string;
  destacado?: boolean;
}) {
  return (
    <div className="flex justify-between">
      <dt className="text-texto-suave">{termino}</dt>
      <dd className={destacado ? "font-semibold text-texto" : "text-texto"}>{valor}</dd>
    </div>
  );
}

/** Acepta coma decimal, que es como se escribe un decimal en Chile. */
function leerCantidad(texto: string): number | null {
  const numero = Number(texto.trim().replace(",", "."));
  return Number.isFinite(numero) && numero > 0 ? numero : null;
}
