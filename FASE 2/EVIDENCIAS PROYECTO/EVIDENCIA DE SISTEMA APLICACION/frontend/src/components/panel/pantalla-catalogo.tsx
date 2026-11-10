"use client";

import Image from "next/image";
import { useCallback, useEffect, useState } from "react";

import {
  obtenerCatalogoDelPanel,
  obtenerCategorias,
  obtenerInventario,
} from "@/lib/api/catalogo-panel";
import { formatearCantidad, formatearPesos } from "@/lib/formato";
import type {
  CategoriaDelPanel,
  EstadoDeProducto,
  PaginaDelPanel,
  ProductoDelPanel,
  ResumenDeInventario,
} from "@/lib/tipos-panel";
import { cn } from "@/lib/utils";

import { FormularioDeProducto } from "./formulario-producto";
import { Cabecera, Cargando, Error as Aviso, Tarjeta, Vacio } from "./piezas";

/*
 * El catálogo de la tienda en el panel.
 *
 * Muestra lo que la vitrina esconde —lo desactivado y lo agotado—, porque es
 * justamente lo que pide atención, y lo ordena así: primero lo que hay que
 * mirar.
 *
 * Lo que no está acá es la alerta por demanda proyectada. Esa necesita el
 * pronóstico, que todavía no existe, y un número sin respaldo en una pantalla
 * de inventario es peor que no tenerlo.
 */

const ETIQUETA: Record<EstadoDeProducto, { texto: string; clase: string }> = {
  publicado: { texto: "Publicado", clase: "border-arena bg-hueso text-pizarra" },
  ultima: { texto: "Queda uno", clase: "border-ambar bg-trigo text-ambar-hondo" },
  agotado: { texto: "Agotado", clase: "border-ambar bg-trigo text-ambar-hondo" },
  desactivado: { texto: "Desactivado", clase: "border-niebla bg-cielo text-acero" },
};

/** Qué formulario está abierto, si es que hay alguno. */
type Edicion = { modo: "nuevo" } | { modo: "editar"; producto: ProductoDelPanel };

export function PantallaCatalogo() {
  const [pagina, setPagina] = useState<PaginaDelPanel | null>(null);
  const [inventario, setInventario] = useState<ResumenDeInventario | null>(null);
  const [categorias, setCategorias] = useState<CategoriaDelPanel[]>([]);
  const [edicion, setEdicion] = useState<Edicion | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);

  // El efecto solo dispara las peticiones: quien escribe el estado es la
  // respuesta, nunca el cuerpo del efecto.
  const cargar = useCallback(() => {
    Promise.all([obtenerCatalogoDelPanel(), obtenerInventario(), obtenerCategorias()])
      .then(([catalogo, resumen, suyas]) => {
        setPagina(catalogo);
        setInventario(resumen);
        setCategorias(suyas);
        setFallo(null);
      })
      .catch((error: unknown) =>
        setFallo(error instanceof Error ? error.message : "No pudimos cargar el catálogo."),
      );
  }, []);

  useEffect(cargar, [cargar]);

  function guardado() {
    setEdicion(null);
    cargar();
  }

  const cabecera = (
    <Cabecera
      titulo="Catálogo"
      descripcion="Tus productos, su precio y su inventario."
      acciones={
        edicion ? undefined : (
          <button
            type="button"
            onClick={() => setEdicion({ modo: "nuevo" })}
            className="h-11 cursor-pointer rounded-[12px] bg-acero px-5 text-[13px] font-semibold text-white transition-colors hover:bg-acero-hondo"
          >
            Agregar producto
          </button>
        )
      }
    />
  );

  if (fallo) {
    return (
      <>
        {cabecera}
        <Aviso mensaje={fallo} onReintentar={cargar} />
      </>
    );
  }

  if (!pagina || !inventario) {
    return (
      <>
        {cabecera}
        <Cargando />
      </>
    );
  }

  if (edicion) {
    return (
      <>
        <Cabecera
          titulo={edicion.modo === "nuevo" ? "Producto nuevo" : edicion.producto.nombre}
          descripcion={
            edicion.modo === "nuevo"
              ? "Lo que escribas acá es lo que verá quien entre a tu tienda."
              : "Los cambios se aplican a tu vitrina al guardar."
          }
        />
        <Tarjeta>
          <FormularioDeProducto
            producto={edicion.modo === "editar" ? edicion.producto : undefined}
            categorias={categorias}
            onGuardado={guardado}
            onCancelar={() => setEdicion(null)}
          />
        </Tarjeta>
      </>
    );
  }

  return (
    <>
      {cabecera}

      <Inventario resumen={inventario} />

      {pagina.productos.length === 0 ? (
        <div className="mt-4">
          <Vacio
            titulo="Todavía no tienes productos"
            detalle="Agrega el primero a mano, o súbelos todos desde una planilla."
            accion={{ href: "/panel/cargas", etiqueta: "Ir a carga masiva" }}
          />
        </div>
      ) : (
        <Tabla
          productos={pagina.productos}
          onEditar={(producto) => setEdicion({ modo: "editar", producto })}
        />
      )}
    </>
  );
}

function Inventario({ resumen }: { resumen: ResumenDeInventario }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <Cifra titulo="Publicados" valor={resumen.publicados} />
      <Cifra titulo="Queda uno" valor={resumen.ultimaUnidad} alerta={resumen.ultimaUnidad > 0} />
      <Cifra titulo="Agotados" valor={resumen.agotados} alerta={resumen.agotados > 0} />
      <Cifra titulo="Desactivados" valor={resumen.desactivados} />
    </div>
  );
}

function Cifra({
  titulo,
  valor,
  alerta = false,
}: {
  titulo: string;
  valor: number;
  alerta?: boolean;
}) {
  return (
    <Tarjeta className={cn("p-5", alerta && "border-ambar bg-trigo")}>
      <p className="text-[11px] font-semibold tracking-[0.06em] text-pizarra uppercase">
        {titulo}
      </p>
      <p className="mt-1 font-jakarta text-[28px] font-extrabold text-marino">{valor}</p>
    </Tarjeta>
  );
}

function Tabla({
  productos,
  onEditar,
}: {
  productos: ProductoDelPanel[];
  onEditar: (producto: ProductoDelPanel) => void;
}) {
  return (
    <div className="mt-4 overflow-x-auto rounded-[14px] border border-arena bg-white">
      <table className="w-full min-w-[720px] text-left text-[13px]">
        <thead className="bg-hueso text-[11px] tracking-[.08em] text-pizarra uppercase">
          <tr>
            <th className="px-4 py-3 font-semibold">Código</th>
            <th className="px-4 py-3 font-semibold">Producto</th>
            <th className="px-4 py-3 font-semibold">Se vende</th>
            <th className="px-4 py-3 font-semibold">Precio neto</th>
            <th className="px-4 py-3 font-semibold">Inventario</th>
            <th className="px-4 py-3 font-semibold">Estado</th>
            <th className="px-4 py-3 font-semibold">
              <span className="sr-only">Editar</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {productos.map((producto) => (
            <tr key={producto.codigo} className="border-t border-arena text-pizarra">
              <td className="px-4 py-3 font-mono text-[12px] whitespace-nowrap text-marino">
                {producto.codigo}
              </td>
              <td className="px-4 py-3">
                <span className="flex items-center gap-2.5">
                  {producto.foto && (
                    <Image
                      src={producto.foto.url}
                      alt=""
                      width={32}
                      height={32}
                      className="size-8 shrink-0 rounded-[6px] border border-arena object-cover"
                    />
                  )}
                  <span className="font-semibold text-marino">{producto.nombre}</span>
                </span>
                {producto.categoria && (
                  <span className="block text-[12px]">{producto.categoria}</span>
                )}
              </td>
              <td className="px-4 py-3 whitespace-nowrap">
                {comoSeVende(producto)}
                {producto.tramos > 0 && (
                  <span className="block text-[12px]">
                    {producto.tramos} {producto.tramos === 1 ? "tramo" : "tramos"}
                  </span>
                )}
              </td>
              <td className="px-4 py-3 whitespace-nowrap text-marino">
                {formatearPesos(producto.precioNeto)}
              </td>
              <td className="px-4 py-3 whitespace-nowrap">{inventarioDe(producto)}</td>
              <td className="px-4 py-3">
                <Etiqueta estado={producto.estado} />
              </td>
              <td className="px-4 py-3 text-right">
                <button
                  type="button"
                  onClick={() => onEditar(producto)}
                  className="cursor-pointer rounded-[10px] border border-niebla px-3 py-1.5 text-[12px] font-semibold text-acero transition-colors hover:bg-cielo"
                >
                  Editar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Etiqueta({ estado }: { estado: EstadoDeProducto }) {
  const { texto, clase } = ETIQUETA[estado];
  return (
    <span
      className={cn(
        "inline-block rounded-full border px-2.5 py-1 text-[11px] font-semibold whitespace-nowrap",
        clase,
      )}
    >
      {texto}
    </span>
  );
}

/** El nombre de la forma de venta, con la unidad cuando aporta. */
function comoSeVende(producto: ProductoDelPanel): string {
  if (producto.formaVenta === "peso") {
    return `Por peso (${producto.unidadMedida})`;
  }
  return producto.formaVenta === "lote" ? "Por lote" : "Por unidad";
}

/**
 * Qué decir del inventario.
 *
 * «Sin control» no es cero: es que la tienda no lleva la cuenta de este
 * producto, y confundir una cosa con la otra haría creer que se agotó.
 */
function inventarioDe(producto: ProductoDelPanel): string {
  if (!producto.controlaStock || producto.stock === null) {
    return "Sin control";
  }
  return formatearCantidad(producto.stock, producto.unidadMedida);
}
