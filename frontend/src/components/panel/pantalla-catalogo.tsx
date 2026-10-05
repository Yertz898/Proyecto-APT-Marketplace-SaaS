"use client";

import { useCallback, useEffect, useState } from "react";

import { obtenerCatalogoDelPanel, obtenerInventario } from "@/lib/api/catalogo-panel";
import { formatearCantidad, formatearPesos } from "@/lib/formato";
import type {
  EstadoDeProducto,
  PaginaDelPanel,
  ProductoDelPanel,
  ResumenDeInventario,
} from "@/lib/tipos-panel";
import { cn } from "@/lib/utils";

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

export function PantallaCatalogo() {
  const [pagina, setPagina] = useState<PaginaDelPanel | null>(null);
  const [inventario, setInventario] = useState<ResumenDeInventario | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);

  // El efecto solo dispara las peticiones: quien escribe el estado es la
  // respuesta, nunca el cuerpo del efecto.
  const cargar = useCallback(() => {
    Promise.all([obtenerCatalogoDelPanel(), obtenerInventario()])
      .then(([catalogo, resumen]) => {
        setPagina(catalogo);
        setInventario(resumen);
        setFallo(null);
      })
      .catch((error: unknown) =>
        setFallo(error instanceof Error ? error.message : "No pudimos cargar el catálogo."),
      );
  }, []);

  useEffect(cargar, [cargar]);

  const cabecera = (
    <Cabecera
      titulo="Catálogo"
      descripcion="Tus productos, su precio y su inventario."
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

  return (
    <>
      {cabecera}

      <Inventario resumen={inventario} />

      {pagina.productos.length === 0 ? (
        <div className="mt-4">
          <Vacio
            titulo="Todavía no tienes productos"
            detalle="Súbelos desde una planilla y quedan publicados en tu tienda."
            accion={{ href: "/panel/cargas", etiqueta: "Ir a carga masiva" }}
          />
        </div>
      ) : (
        <Tabla productos={pagina.productos} />
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

function Tabla({ productos }: { productos: ProductoDelPanel[] }) {
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
          </tr>
        </thead>
        <tbody>
          {productos.map((producto) => (
            <tr key={producto.codigo} className="border-t border-arena text-pizarra">
              <td className="px-4 py-3 font-mono text-[12px] whitespace-nowrap text-marino">
                {producto.codigo}
              </td>
              <td className="px-4 py-3">
                <span className="font-semibold text-marino">{producto.nombre}</span>
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
