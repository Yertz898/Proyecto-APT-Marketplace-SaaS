"use client";

import { useState, type ReactNode } from "react";

import { Checkbox } from "@/components/ui/checkbox";
import { Sheet, SheetClose, SheetContent, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { formatearPesos } from "@/lib/formato";
import type { FiltrosCatalogo } from "@/lib/tipos";
import { cn } from "@/lib/utils";

import { clasesPanelLateral } from "./panel-lateral";

/*
 * Filtros del catálogo (mockup 1B). En móvil se abren en el mismo panel lateral
 * que el menú de 1D, porque el mockup no dibuja el catálogo en móvil.
 *
 * Por ahora la selección es estado local y no filtra nada: no existe la API.
 * Al conectarla, la selección pasa a la URL y el servidor devuelve el catálogo
 * ya filtrado, que es donde corresponde hacerlo.
 */

type Seleccion = {
  categorias: string[];
  materiales: string[];
  precio: number[] | null;
  soloMayorista: boolean;
};

const SIN_SELECCION: Seleccion = { categorias: [], materiales: [], precio: null, soloMayorista: false };

const CLASES_CASILLA = "size-4 rounded-[4px] border-lila/35 dark:bg-transparent data-checked:border-violeta dark:data-checked:bg-violeta";

function alternar(lista: string[], valor: string): string[] {
  return lista.includes(valor) ? lista.filter((elemento) => elemento !== valor) : [...lista, valor];
}

export function FiltrosEscritorio({ filtros }: { filtros: FiltrosCatalogo }) {
  const [seleccion, setSeleccion] = useState(SIN_SELECCION);

  return (
    <aside aria-label="Filtros" className="hidden rounded-2xl border border-lila/12 bg-superficie p-[22px] lg:block">
      <PanelFiltros filtros={filtros} seleccion={seleccion} onCambio={setSeleccion} />
    </aside>
  );
}

export function FiltrosMovil({ filtros }: { filtros: FiltrosCatalogo }) {
  const [seleccion, setSeleccion] = useState(SIN_SELECCION);

  return (
    <Sheet>
      <SheetTrigger
        render={
          <button
            type="button"
            className="flex h-[42px] cursor-pointer items-center gap-2.5 rounded-[10px] border border-lila/20 bg-superficie px-4 text-[13px] text-texto lg:hidden"
          />
        }
      >
        Filtros
      </SheetTrigger>

      <SheetContent
        side="left"
        showCloseButton={false}
        overlayClassName={clasesPanelLateral.fondo}
        className={clasesPanelLateral.panel}
      >
        <div className="mb-[26px] flex items-center justify-between">
          <SheetTitle className="font-serif text-[22px] font-normal text-texto">Filtros</SheetTitle>
          <SheetClose
            render={
              <button
                type="button"
                aria-label="Cerrar filtros"
                className="size-[34px] cursor-pointer rounded-full border border-lila/25 bg-transparent text-[15px] text-texto"
              />
            }
          >
            ×
          </SheetClose>
        </div>

        <PanelFiltros filtros={filtros} seleccion={seleccion} onCambio={setSeleccion} sinTitulo />
      </SheetContent>
    </Sheet>
  );
}

function PanelFiltros({
  filtros,
  seleccion,
  onCambio,
  sinTitulo = false,
}: {
  filtros: FiltrosCatalogo;
  seleccion: Seleccion;
  onCambio: (seleccion: Seleccion) => void;
  sinTitulo?: boolean;
}) {
  const { precioMinimo, precioMaximo } = filtros;
  const hayRango = precioMinimo !== null && precioMaximo !== null;
  const precio = seleccion.precio ?? (hayRango ? [precioMinimo, precioMaximo] : [0, 100]);

  const nombreCategoria = (slug: string) =>
    filtros.categorias.find((categoria) => categoria.slug === slug)?.nombre ?? slug;

  const activos = [
    ...seleccion.categorias.map((slug) => ({
      clave: `categoria-${slug}`,
      texto: nombreCategoria(slug),
      quitar: () => onCambio({ ...seleccion, categorias: alternar(seleccion.categorias, slug) }),
    })),
    ...seleccion.materiales.map((material) => ({
      clave: `material-${material}`,
      texto: material,
      quitar: () => onCambio({ ...seleccion, materiales: alternar(seleccion.materiales, material) }),
    })),
  ];

  return (
    <>
      <div className={cn("flex items-center", sinTitulo ? "justify-end" : "justify-between")}>
        {!sinTitulo && (
          <span className="text-[11px] font-semibold tracking-[.14em] text-texto uppercase">Filtros</span>
        )}
        <button type="button" onClick={() => onCambio(SIN_SELECCION)} className="cursor-pointer text-xs text-lila">
          Limpiar
        </button>
      </div>

      {activos.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {activos.map((activo) => (
            <button
              key={activo.clave}
              type="button"
              onClick={activo.quitar}
              aria-label={`Quitar filtro ${activo.texto}`}
              className="flex cursor-pointer items-center gap-[7px] rounded-2xl border border-lila/40 bg-violeta/20 px-2.5 py-1.5 text-xs text-texto"
            >
              {activo.texto} ×
            </button>
          ))}
        </div>
      )}

      <Seccion titulo="Categoría" primera>
        {filtros.categorias.map((categoria) => {
          const marcada = seleccion.categorias.includes(categoria.slug);
          return (
            <label key={categoria.slug} className="flex cursor-pointer items-center gap-2.5">
              <Checkbox
                checked={marcada}
                onCheckedChange={() =>
                  onCambio({ ...seleccion, categorias: alternar(seleccion.categorias, categoria.slug) })
                }
                className={CLASES_CASILLA}
              />
              <span className={cn(marcada && "text-texto")}>{categoria.nombre}</span>
              <span className="ml-auto">{categoria.cantidadProductos}</span>
            </label>
          );
        })}
      </Seccion>

      <Seccion titulo="Material">
        {filtros.materiales.map((material) => {
          const marcado = seleccion.materiales.includes(material);
          return (
            <label key={material} className="flex cursor-pointer items-center gap-2.5">
              <Checkbox
                checked={marcado}
                onCheckedChange={() => onCambio({ ...seleccion, materiales: alternar(seleccion.materiales, material) })}
                className={CLASES_CASILLA}
              />
              <span className={cn(marcado && "text-texto")}>{material}</span>
            </label>
          );
        })}
      </Seccion>

      <div className="mt-6 border-t border-texto/8 pt-5">
        <div className="text-[13px] font-semibold text-texto">Precio</div>
        <Slider
          className="mt-4"
          min={hayRango ? precioMinimo : 0}
          max={hayRango ? precioMaximo : 100}
          value={precio}
          disabled={!hayRango}
          onValueChange={(valor) =>
            onCambio({ ...seleccion, precio: Array.isArray(valor) ? [...valor] : [valor] })
          }
        />
        {hayRango && (
          <div className="mt-3 flex justify-between text-xs text-texto-suave">
            <span>{formatearPesos(precio[0])}</span>
            <span>{formatearPesos(precio[1])}</span>
          </div>
        )}
      </div>

      <label className="mt-6 flex cursor-pointer items-center gap-3 border-t border-texto/8 pt-5">
        <Switch
          size="lg"
          checked={seleccion.soloMayorista}
          onCheckedChange={(marcado) => onCambio({ ...seleccion, soloMayorista: marcado })}
        />
        <span className="text-[13px] text-texto">Solo con precio mayorista</span>
      </label>
    </>
  );
}

function Seccion({ titulo, primera = false, children }: { titulo: string; primera?: boolean; children: ReactNode }) {
  return (
    <div className={cn("border-t border-texto/8 pt-5", primera ? "mt-[26px]" : "mt-6")}>
      <div className="text-[13px] font-semibold text-texto">{titulo}</div>
      <div className="mt-3 flex flex-col gap-[11px] text-[13px] text-texto-suave">{children}</div>
    </div>
  );
}
