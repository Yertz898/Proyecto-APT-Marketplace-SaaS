"use client";

import Image from "next/image";
import { useState } from "react";

import { formatearPesos } from "@/lib/formato";
import type { Imagen, ProductoDetalle, TramoPrecio } from "@/lib/tipos";
import { rangoDeTramo, tramoParaCantidad } from "@/lib/tramos";
import { cn } from "@/lib/utils";

import { useCarrito } from "./carrito";
import { EnlaceExterno } from "./enlace-externo";
import { IconoInfo, IconoWhatsapp } from "./iconos";

/*
 * Ficha de producto (mockup 1C).
 *
 * El precio que se muestra al cambiar la cantidad es solo para orientar al
 * comprador: el precio que vale es el que calcula el backend al crear el pedido.
 * Qué tramos llegan hasta acá también lo decide el backend, según la aprobación
 * mayorista del comprador (CONVENCIONES.md > Precio mayorista).
 *
 * En móvil el mockup no dibuja esta pantalla: las dos columnas se apilan y la
 * descripción queda al final.
 */

type Props = {
  producto: ProductoDetalle;
  enlaceWhatsapp: string | null;
};

const CLASES_PASO =
  "size-10 cursor-pointer rounded-[9px] bg-transparent text-xl text-texto transition-colors hover:bg-violeta/22";

function tieneStock(producto: ProductoDetalle, material: string, talla: string): boolean {
  return producto.variantes.some(
    (variante) => variante.material === material && variante.talla === talla && variante.stock > 0,
  );
}

function clasesOpcion(seleccionada: boolean, agotada: boolean) {
  return cn(
    "h-11 rounded-xl border px-[18px] text-sm font-medium transition-[background-color,border-color] duration-160 ease-[ease]",
    agotada
      ? "cursor-not-allowed border-dashed border-texto-suave/30 bg-superficie/50 text-texto-apagado line-through"
      : seleccionada
        ? "cursor-pointer border-lila bg-violeta/28 text-texto"
        : "cursor-pointer border-lila/18 bg-superficie text-texto-suave",
  );
}

export function FichaProducto({ producto, enlaceWhatsapp }: Props) {
  const { agregar } = useCarrito();
  const tramos = [...producto.tramos].sort((a, b) => a.cantidadMinima - b.cantidadMinima);
  const primerMaterial = producto.materiales[0] ?? "";

  const [material, setMaterial] = useState(primerMaterial);
  const [talla, setTalla] = useState(
    () => producto.tallas.find((opcion) => tieneStock(producto, primerMaterial, opcion)) ?? producto.tallas[0] ?? "",
  );
  const [cantidad, setCantidad] = useState(1);
  const [imagenActiva, setImagenActiva] = useState(0);

  const conStock = tieneStock(producto, material, talla);
  const variante = producto.variantes.find(
    (opcion) => opcion.material === material && opcion.talla === talla,
  );
  const tramo = tramoParaCantidad(tramos, cantidad);
  const indiceTramo = tramo ? tramos.indexOf(tramo) : -1;
  const hayMayorista = tramos.length > 1;

  return (
    <div className="mx-auto grid max-w-[1280px] items-start gap-10 px-5 pt-[26px] pb-[70px] lg:grid-cols-[minmax(0,1fr)_520px] lg:gap-14 lg:px-6">
      <div>
        <Galeria
          imagenes={producto.imagenes}
          activa={imagenActiva}
          onSeleccion={setImagenActiva}
          hayMayorista={hayMayorista}
        />
        <SobreLaPieza producto={producto} className="hidden lg:block" />
      </div>

      <div>
        <p className="text-[11px] font-semibold tracking-[.16em] text-lila uppercase">
          {producto.categoria.nombre}
          {producto.coleccion ? ` · ${producto.coleccion}` : ""}
        </p>
        <h1 className="mt-3.5 font-serif text-[36px] leading-[1.1] font-medium text-texto lg:text-[46px]">
          {producto.nombre}
        </h1>
        {variante && <p className="mt-2.5 text-[13px] text-texto-suave">SKU {variante.sku}</p>}

        {tramo && (
          <>
            <p className="mt-[26px] flex items-baseline gap-3">
              <span className="font-serif text-[44px] font-semibold text-oro">
                {formatearPesos(tramo.precioUnitario)}
              </span>
              <span className="text-[13px] text-texto-suave">por unidad · IVA incluido</span>
            </p>
            <p className="mt-2 text-[13px] text-lila">
              {indiceTramo === 0
                ? hayMayorista
                  ? `Precio al detalle · desde ${tramos[1].cantidadMinima} unidades baja el valor`
                  : "Precio al detalle"
                : `Tramo mayorista aplicado (${rangoDeTramo(tramos, indiceTramo).replace(" unidades", "")})`}
            </p>
          </>
        )}

        <div className="mt-8 border-t border-texto/8 pt-[26px]">
          <div className="flex items-baseline justify-between gap-4">
            <span className="text-[13px] font-semibold text-texto">Material</span>
            <span className="text-xs text-texto-suave">El stock depende de la combinación</span>
          </div>
          <div className="mt-3.5 flex flex-wrap gap-2.5">
            {producto.materiales.map((opcion) => (
              <button
                key={opcion}
                type="button"
                aria-pressed={material === opcion}
                onClick={() => setMaterial(opcion)}
                className={clasesOpcion(material === opcion, false)}
              >
                {opcion}
              </button>
            ))}
          </div>

          <div className="mt-6 text-[13px] font-semibold text-texto">Talla</div>
          <div className="mt-3.5 flex flex-wrap gap-2.5">
            {producto.tallas.map((opcion) => {
              const agotada = !tieneStock(producto, material, opcion);
              return (
                <button
                  key={opcion}
                  type="button"
                  aria-pressed={talla === opcion && !agotada}
                  disabled={agotada}
                  onClick={() => setTalla(opcion)}
                  className={clasesOpcion(talla === opcion && !agotada, agotada)}
                >
                  Talla {opcion}
                </button>
              );
            })}
          </div>

          <p className="mt-3.5 flex items-center gap-[9px] text-xs text-texto-suave">
            <span
              aria-hidden="true"
              className={cn("size-[7px] rounded-full", conStock ? "bg-violeta" : "bg-texto-suave")}
            />
            {conStock
              ? `En stock · ${material} talla ${talla}`
              : `Sin stock en ${material} talla ${talla} · elige otra combinación`}
          </p>
        </div>

        <div className="mt-7 border-t border-texto/8 pt-[26px]">
          <div className="flex items-center gap-[18px]">
            <div className="flex items-center gap-0.5 rounded-xl border border-lila/20 bg-superficie p-1">
              <button
                type="button"
                aria-label="Quitar una unidad"
                onClick={() => setCantidad((actual) => Math.max(1, actual - 1))}
                className={CLASES_PASO}
              >
                −
              </button>
              <span aria-live="polite" className="min-w-[52px] text-center text-base font-semibold text-texto">
                {cantidad}
              </span>
              <button
                type="button"
                aria-label="Agregar una unidad"
                onClick={() => setCantidad((actual) => actual + 1)}
                className={CLASES_PASO}
              >
                +
              </button>
            </div>

            {tramo && (
              <div>
                <div className="text-xs text-texto-suave">Total del pedido</div>
                <div className="font-serif text-[28px] font-semibold text-texto">
                  {formatearPesos(tramo.precioUnitario * cantidad)}
                </div>
              </div>
            )}
          </div>

          {tramos.length > 0 && <TablaTramos tramos={tramos} activo={indiceTramo} />}

          <div className="mt-[22px] flex flex-col gap-3">
            <button
              type="button"
              disabled={!conStock}
              onClick={() => agregar(cantidad)}
              className="h-[54px] cursor-pointer rounded-full bg-violeta text-[15px] font-semibold text-white transition-colors hover:bg-violeta-hover disabled:cursor-not-allowed disabled:opacity-50"
            >
              Agregar al carrito
            </button>

            <EnlaceExterno
              enlace={enlaceWhatsapp}
              className="flex h-[54px] cursor-pointer items-center justify-center gap-2.5 rounded-full border border-lila/38 bg-transparent text-sm font-medium text-texto transition-colors hover:bg-violeta/16"
            >
              <IconoWhatsapp tamano={17} solido className="fill-lila" />
              Consultar por WhatsApp
            </EnlaceExterno>

            <p className="text-center text-xs text-texto-suave">
              El pago se coordina por WhatsApp al confirmar el pedido.
            </p>
          </div>
        </div>
      </div>

      <SobreLaPieza producto={producto} className="mt-0 lg:hidden" />
    </div>
  );
}

function Galeria({
  imagenes,
  activa,
  onSeleccion,
  hayMayorista,
}: {
  imagenes: Imagen[];
  activa: number;
  onSeleccion: (indice: number) => void;
  hayMayorista: boolean;
}) {
  const principal = imagenes[activa];

  return (
    <>
      <div className="relative flex h-[360px] items-center justify-center overflow-hidden rounded-[20px] border border-lila/14 bg-[radial-gradient(80%_80%_at_35%_25%,#332A4C_0%,#14121B_72%)] lg:h-[560px]">
        {principal && (
          <Image
            src={principal.url}
            alt={principal.alt}
            fill
            sizes="(min-width: 1024px) 700px, 100vw"
            className="object-cover"
          />
        )}
        {hayMayorista && (
          <span className="absolute top-[18px] left-[18px] rounded-[20px] border border-oro/50 bg-tinta/70 px-[11px] py-1.5 text-[10px] font-semibold tracking-[.08em] text-oro">
            PRECIO MAYORISTA DISPONIBLE
          </span>
        )}
      </div>

      {imagenes.length > 1 && (
        <div className="mt-4 grid grid-cols-4 gap-3.5">
          {imagenes.map((imagen, indice) => (
            <button
              key={imagen.url}
              type="button"
              aria-label={`Ver imagen ${indice + 1}`}
              aria-pressed={indice === activa}
              onClick={() => onSeleccion(indice)}
              className={cn(
                "relative h-20 cursor-pointer overflow-hidden rounded-[14px] bg-[radial-gradient(90%_90%_at_35%_25%,#332A4C,#14121B)] lg:h-[118px]",
                indice === activa ? "border-2 border-violeta" : "border border-lila/16",
              )}
            >
              <Image src={imagen.url} alt="" fill sizes="160px" className="object-cover" />
            </button>
          ))}
        </div>
      )}
    </>
  );
}

function TablaTramos({ tramos, activo }: { tramos: TramoPrecio[]; activo: number }) {
  return (
    <div className="mt-[22px] overflow-hidden rounded-[14px] border border-lila/16">
      <div className="flex items-center justify-between bg-superficie px-[18px] py-3.5">
        <span className="text-[13px] font-semibold text-texto">Precio por volumen</span>
        <span className="text-[11px] tracking-[.08em] text-texto-suave uppercase">Por unidad</span>
      </div>

      {tramos.map((tramo, indice) => {
        const encendido = indice === activo;
        return (
          <div
            key={tramo.cantidadMinima}
            className={cn(
              "grid grid-cols-[1fr_auto_96px] items-center gap-3.5 border-t border-lila/12 px-[18px] py-[15px] transition-[background-color] duration-200 ease-[ease]",
              encendido && "bg-violeta/20 shadow-[inset_3px_0_0_#A78BFA]",
            )}
          >
            <span className={cn("text-sm", encendido ? "font-semibold text-texto" : "text-texto-suave")}>
              {rangoDeTramo(tramos, indice)}
            </span>
            <span className={cn("font-serif text-[21px] font-semibold", encendido ? "text-oro" : "text-texto-suave")}>
              {formatearPesos(tramo.precioUnitario)}
            </span>
            <span
              className={cn(
                "justify-self-end rounded-[20px] border px-[9px] py-1 text-[10px] tracking-[.08em] uppercase",
                indice === 0 ? "border-lila/28 text-lila" : "border-oro/40 text-oro",
              )}
            >
              {tramo.etiqueta}
            </span>
          </div>
        );
      })}

      {tramos.length > 1 && (
        <div className="flex items-start gap-2.5 border-t border-oro/22 bg-oro/7 px-[18px] py-[13px]">
          <IconoInfo className="mt-px flex-none" />
          <span className="text-xs leading-[1.55] text-texto-suave">
            Los tramos de {tramos[1].cantidadMinima} unidades o más requieren cuenta mayorista aprobada. Puedes pedir la
            aprobación en un paso al confirmar.
          </span>
        </div>
      )}
    </div>
  );
}

function SobreLaPieza({ producto, className }: { producto: ProductoDetalle; className?: string }) {
  return (
    <section className={cn("mt-[34px] border-t border-texto/8 pt-7", className)}>
      <h2 className="font-serif text-[26px] font-medium text-texto">Sobre esta pieza</h2>
      <p className="mt-3 max-w-[620px] text-sm leading-[1.75] text-texto-suave">{producto.descripcion}</p>

      {producto.caracteristicas.length > 0 && (
        <dl className="mt-[22px] grid grid-cols-1 gap-3.5 sm:grid-cols-3">
          {producto.caracteristicas.map((caracteristica) => (
            <div key={caracteristica.nombre} className="rounded-xl border border-lila/12 bg-superficie p-4">
              <dt className="text-[11px] tracking-[.1em] text-texto-suave uppercase">{caracteristica.nombre}</dt>
              <dd className="mt-1.5 text-sm text-texto">{caracteristica.valor}</dd>
            </div>
          ))}
        </dl>
      )}
    </section>
  );
}
