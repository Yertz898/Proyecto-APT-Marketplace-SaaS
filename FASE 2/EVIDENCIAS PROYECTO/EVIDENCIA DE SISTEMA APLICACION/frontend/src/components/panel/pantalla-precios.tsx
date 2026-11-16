"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";

import { obtenerCatalogoDelPanel } from "@/lib/api/catalogo-panel";
import { ErrorDeApi } from "@/lib/api/errores";
import { borrarTramo, crearTramo, obtenerTramos, type TramoDelPanel } from "@/lib/api/gestion";
import { formatearPesos } from "@/lib/formato";
import type { PaginaDelPanel, ProductoDelPanel } from "@/lib/tipos-panel";
import { cn } from "@/lib/utils";

import { Aviso, Boton, CLASE_ENTRADA, Campo, mensajeDe } from "./controles";
import { Cabecera, Cargando, Error, Tarjeta, Vacio } from "./piezas";

/*
 * Los precios por volumen de cada producto.
 *
 * Un tramo dice «desde tal cantidad, el precio unitario neto es tal». No hay
 * descuentos: si hace falta otro precio, es otro tramo. Quien calcula qué
 * tramo aplica es siempre el backend; acá solo se definen.
 */

const UNIDADES: Record<TramoDelPanel["unidadUmbral"], string> = {
  cantidad: "unidades o lotes",
  peso: "gramos",
  monto: "pesos de compra",
};

export function PantallaPrecios() {
  const [pagina, setPagina] = useState(1);
  const [catalogo, setCatalogo] = useState<PaginaDelPanel | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);
  const [elegido, setElegido] = useState<ProductoDelPanel | null>(null);

  useEffect(() => {
    obtenerCatalogoDelPanel({ pagina }).then(setCatalogo, (error) => setFallo(mensajeDe(error)));
  }, [pagina]);

  return (
    <>
      <Cabecera
        titulo="Precios"
        descripcion="Precios más bajos desde cierta cantidad. Elige un producto para ver o cambiar sus tramos."
      />

      {fallo && <Error mensaje={fallo} />}
      {!fallo && !catalogo && <Cargando />}
      {catalogo && catalogo.productos.length === 0 && (
        <Vacio titulo="Todavía no tienes productos" accion={{ href: "/panel/catalogo", etiqueta: "Ir al catálogo" }} />
      )}

      {catalogo && catalogo.productos.length > 0 && (
        <div className="grid gap-4 lg:grid-cols-[340px_minmax(0,1fr)] lg:items-start">
          <Tarjeta className="p-0">
            <ul className="max-h-[620px] divide-y divide-arena overflow-y-auto">
              {catalogo.productos.map((producto) => (
                <li key={producto.codigo}>
                  <button
                    type="button"
                    onClick={() => setElegido(producto)}
                    className={cn(
                      "w-full cursor-pointer px-4 py-3 text-left transition-colors hover:bg-hueso",
                      elegido?.codigo === producto.codigo && "bg-cielo",
                    )}
                  >
                    <span className="block text-[14px] font-semibold text-marino">{producto.nombre}</span>
                    <span className="text-[12px] text-pizarra">
                      {producto.codigo} · {formatearPesos(producto.precioNeto)} ·{" "}
                      {producto.tramos === 0 ? "sin tramos" : `${producto.tramos} tramo${producto.tramos === 1 ? "" : "s"}`}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
            {catalogo.totalPaginas > 1 && (
              <div className="flex items-center justify-between border-t border-arena px-4 py-3 text-[13px]">
                <button type="button" className="cursor-pointer text-acero disabled:opacity-40" disabled={pagina <= 1} onClick={() => setPagina(pagina - 1)}>
                  ← Anterior
                </button>
                <span className="text-pizarra">
                  {catalogo.paginaActual} de {catalogo.totalPaginas}
                </span>
                <button
                  type="button"
                  className="cursor-pointer text-acero disabled:opacity-40"
                  disabled={pagina >= catalogo.totalPaginas}
                  onClick={() => setPagina(pagina + 1)}
                >
                  Siguiente →
                </button>
              </div>
            )}
          </Tarjeta>

          {elegido ? (
            <TramosDe key={elegido.codigo} producto={elegido} />
          ) : (
            <Vacio titulo="Elige un producto" detalle="Sus tramos de precio aparecen acá." />
          )}
        </div>
      )}
    </>
  );
}

function TramosDe({ producto }: { producto: ProductoDelPanel }) {
  const [tramos, setTramos] = useState<TramoDelPanel[] | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);
  const unidadSugerida: TramoDelPanel["unidadUmbral"] = producto.formaVenta === "peso" ? "peso" : "cantidad";
  const [umbral, setUmbral] = useState("");
  const [unidad, setUnidad] = useState<TramoDelPanel["unidadUmbral"]>(unidadSugerida);
  const [precio, setPrecio] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [errorDeAlta, setErrorDeAlta] = useState<string | null>(null);

  const cargar = useCallback(() => {
    obtenerTramos(producto.codigo).then(setTramos, (error) => setFallo(mensajeDe(error)));
  }, [producto.codigo]);
  useEffect(cargar, [cargar]);

  async function agregar(evento: FormEvent) {
    evento.preventDefault();
    setGuardando(true);
    setErrorDeAlta(null);
    try {
      const nuevo = await crearTramo(producto.codigo, {
        umbral: umbral.replace(",", "."),
        unidadUmbral: unidad,
        precioNeto: Number(precio),
      });
      setTramos((actual) => [...(actual ?? []), nuevo]);
      setUmbral("");
      setPrecio("");
    } catch (error) {
      const detalle = error instanceof ErrorDeApi ? Object.values(error.detalles)[0]?.[0] : null;
      setErrorDeAlta(detalle ?? mensajeDe(error));
    } finally {
      setGuardando(false);
    }
  }

  async function quitar(id: number) {
    try {
      await borrarTramo(id);
      setTramos((actual) => actual?.filter((t) => t.id !== id) ?? null);
    } catch (error) {
      setFallo(mensajeDe(error));
    }
  }

  const ordenados = [...(tramos ?? [])].sort((a, b) => Number(a.umbral) - Number(b.umbral));

  return (
    <Tarjeta>
      <p className="font-jakarta text-[18px] font-bold text-marino">{producto.nombre}</p>
      <p className="mt-1 text-[13px] text-pizarra">
        Precio base: {formatearPesos(producto.precioNeto)} neto. Cada tramo lo reemplaza desde la cantidad que indiques.
      </p>

      {fallo && <Aviso tipo="error">{fallo}</Aviso>}
      {!tramos && !fallo && <Cargando />}

      {tramos && (
        <table className="mt-5 w-full text-left text-[14px]">
          <thead>
            <tr className="border-b border-arena text-[12px] text-pizarra">
              <th className="py-2 font-semibold">Desde</th>
              <th className="py-2 font-semibold">Precio unitario neto</th>
              <th className="py-2" />
            </tr>
          </thead>
          <tbody>
            {ordenados.length === 0 && (
              <tr>
                <td colSpan={3} className="py-4 text-pizarra">
                  Sin tramos: se cobra siempre el precio base.
                </td>
              </tr>
            )}
            {ordenados.map((tramo) => (
              <tr key={tramo.id} className="border-b border-arena">
                <td className="py-2.5 text-marino">
                  {Number(tramo.umbral).toLocaleString("es-CL")} {UNIDADES[tramo.unidadUmbral]}
                </td>
                <td className="py-2.5 font-semibold text-marino">{formatearPesos(tramo.precioNeto)}</td>
                <td className="py-2.5 text-right">
                  <button type="button" className="cursor-pointer text-[13px] font-semibold text-acero" onClick={() => quitar(tramo.id)}>
                    Quitar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <form onSubmit={agregar} className="mt-6 grid gap-3 sm:grid-cols-[1fr_1fr_1fr_auto] sm:items-end">
        <Campo
          id="umbral"
          etiqueta="Desde"
          inputMode="decimal"
          value={umbral}
          onChange={(e) => /^\d{0,9}([.,]\d{0,2})?$/.test(e.target.value) && setUmbral(e.target.value)}
        />
        <label className="text-[13px] font-semibold text-marino">
          Medido en
          <select className={CLASE_ENTRADA} value={unidad} onChange={(e) => setUnidad(e.target.value as TramoDelPanel["unidadUmbral"])}>
            {Object.entries(UNIDADES).map(([valor, nombre]) => (
              <option key={valor} value={valor}>
                {nombre}
              </option>
            ))}
          </select>
        </label>
        <Campo
          id="precio-tramo"
          etiqueta="Precio neto"
          inputMode="numeric"
          value={precio}
          onChange={(e) => /^\d{0,9}$/.test(e.target.value) && setPrecio(e.target.value)}
        />
        <Boton type="submit" disabled={guardando || !umbral || !precio}>
          Agregar
        </Boton>
      </form>
      {errorDeAlta && <Aviso tipo="error">{errorDeAlta}</Aviso>}
    </Tarjeta>
  );
}
