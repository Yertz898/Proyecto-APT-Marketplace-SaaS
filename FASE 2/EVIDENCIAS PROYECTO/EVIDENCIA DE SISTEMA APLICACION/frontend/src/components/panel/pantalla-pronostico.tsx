"use client";

import { useCallback, useEffect, useState } from "react";

import { obtenerPronostico } from "@/lib/api/pedidos";
import { formatearCantidad } from "@/lib/formato";
import type { PronosticoDeDemanda, ProyeccionDeProducto } from "@/lib/tipos-panel";
import { cn } from "@/lib/utils";

import { Grafico, LineaDeTiempo, SERIE } from "./graficos";
import { Cabecera, Cargando, Error as Aviso, Tarjeta, Vacio } from "./piezas";

/*
 * Cuánto se va a vender el próximo mes, y qué se queda sin stock antes.
 *
 * Esta pantalla muestra **estimaciones**, a diferencia del panel de ventas,
 * que muestra hechos. Por eso dice en pantalla con qué se calculó cada
 * número: mientras el dueño no pueda distinguir una medición de una
 * proyección, no sabe cuánto confiar en lo que está viendo.
 *
 * Lo que no hace es rellenar. Un producto sin historia suficiente aparece
 * igual, diciendo que no se puede proyectar y cuántos meses le faltan. Un
 * cero ahí se leería como «no se va a vender», que es una afirmación bien
 * distinta de «todavía no sabemos».
 */

/** A partir de cuántos días por delante el quiebre deja de ser urgente. */
const DIAS_TRANQUILOS = 30;

export function PantallaPronostico() {
  const [pronostico, setPronostico] = useState<PronosticoDeDemanda | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);

  const cargar = useCallback(() => {
    obtenerPronostico()
      .then((suyo) => {
        setPronostico(suyo);
        setFallo(null);
      })
      .catch((error: unknown) =>
        setFallo(
          error instanceof Error ? error.message : "No pudimos calcular el pronóstico.",
        ),
      );
  }, []);

  useEffect(cargar, [cargar]);

  const cabecera = (
    <Cabecera
      titulo="Pronóstico"
      descripcion="Cuánto se espera vender el próximo mes y qué se va a agotar."
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

  if (pronostico === null) {
    return (
      <>
        {cabecera}
        <Cargando texto="Mirando tu historial de ventas…" />
      </>
    );
  }

  const conProyeccion = pronostico.productos.filter((p) => p.suficiente);
  const sinDatos = pronostico.productos.filter((p) => !p.suficiente);
  // El techo más alto de los tres, redondeado como lo haría cada gráfico por
  // su cuenta, para que los tres compartan el eje.
  const topeComun = Math.max(
    ...conProyeccion.flatMap((p) => [
      ...p.serie.map((punto) => punto.cantidad),
      p.esperado ?? 0,
    ]),
    1,
  );
  const porAgotarse = conProyeccion.filter(
    (p) => p.diasHastaQuiebre !== null && p.diasHastaQuiebre <= DIAS_TRANQUILOS,
  );

  if (pronostico.productos.length === 0) {
    return (
      <>
        {cabecera}
        <Vacio
          titulo="Todavía no hay productos publicados"
          detalle="El pronóstico se calcula sobre lo que tienes en la vitrina."
        />
      </>
    );
  }

  return (
    <>
      {cabecera}

      {porAgotarse.length > 0 && (
        <div className="mt-4 rounded-[14px] border border-ambar bg-trigo p-4">
          <h2 className="text-[13px] font-semibold text-marino">
            Se te va a acabar pronto
          </h2>
          <ul className="mt-2.5 flex flex-col gap-1.5">
            {porAgotarse.map((producto) => (
              <li key={producto.codigo} className="text-[13px] text-marino">
                <span className="font-semibold">{producto.nombre}</span>
                {": "}
                {producto.diasHastaQuiebre === 0
                  ? "ya no queda al ritmo actual"
                  : `quedan unos ${producto.diasHastaQuiebre} días al ritmo actual`}
              </li>
            ))}
          </ul>
        </div>
      )}

      {conProyeccion.length > 0 && (
        <Tarjeta className="mt-4">
          <Grafico
            titulo="Lo que vendiste y lo que viene"
            detalle={`Un gráfico por producto y todos a la misma escala, para que se puedan comparar. La línea llena es lo que pasó; el punto hueco del final es la estimación del próximo mes, calculada con ${conProyeccion[0].metodo}.`}
            tabla={{
              columnas: ["Producto", "Meses", "Esperado el próximo mes"],
              filas: conProyeccion.map((producto) => [
                producto.nombre,
                producto.mesesConVentas,
                formatearCantidad(producto.esperado ?? 0, producto.unidad),
              ]),
            }}
          >
            <div className="flex flex-col gap-4">
              {conProyeccion.map((producto, i) => (
                <div key={producto.codigo}>
                  <p className="flex items-center gap-1.5 text-xs text-pizarra">
                    <span
                      aria-hidden="true"
                      style={{ background: SERIE[i % SERIE.length] }}
                      className="block h-[2px] w-4 shrink-0 rounded-full"
                    />
                    {producto.nombre}
                  </p>
                  <LineaDeTiempo
                    compacta
                    tope={topeComun}
                    formatear={(valor) => formatearCantidad(valor, producto.unidad)}
                    series={[
                      {
                        nombre: producto.nombre,
                        color: SERIE[i % SERIE.length],
                        puntos: [
                          ...producto.serie.map((punto) => ({
                            etiqueta: mesCorto(punto.mes),
                            valor: punto.cantidad,
                          })),
                          {
                            etiqueta: "próx.",
                            valor: producto.esperado ?? 0,
                            atenuado: true,
                          },
                        ],
                      },
                    ]}
                  />
                </div>
              ))}
            </div>
          </Grafico>
        </Tarjeta>
      )}

      <Tarjeta className="mt-3">
        <h2 className="text-[13px] font-semibold text-marino">
          Lo que se espera vender
        </h2>
        <p className="mt-1 text-xs leading-[1.5] text-pizarra">
          {conProyeccion.length > 0
            ? `Calculado con ${conProyeccion[0].metodo}. Es una estimación, no una medición.`
            : "Todavía no hay ningún producto con historial suficiente."}
        </p>

        {conProyeccion.length > 0 && (
          <ul className="mt-3.5 flex flex-col gap-2.5">
            {conProyeccion.map((producto) => (
              <Fila key={producto.codigo} producto={producto} />
            ))}
          </ul>
        )}
      </Tarjeta>

      {sinDatos.length > 0 && (
        <Tarjeta className="mt-3">
          <h2 className="text-[13px] font-semibold text-marino">
            Sin datos suficientes ({sinDatos.length})
          </h2>
          <p className="mt-1 text-xs leading-[1.5] text-pizarra">
            Hacen falta {pronostico.minimoDeMeses} meses con ventas para proyectar.
            Con menos, el número diría más sobre el azar que sobre tu negocio.
          </p>

          <ul className="mt-3.5 flex flex-col gap-1.5">
            {sinDatos.slice(0, 12).map((producto) => (
              <li
                key={producto.codigo}
                className="flex justify-between gap-4 text-[13px]"
              >
                <span className="min-w-0 truncate text-pizarra">{producto.nombre}</span>
                <span className="shrink-0 text-pizarra">
                  {producto.mesesConVentas === 0
                    ? "sin ventas"
                    : `${producto.mesesConVentas} ${producto.mesesConVentas === 1 ? "mes" : "meses"}`}
                </span>
              </li>
            ))}
          </ul>

          {sinDatos.length > 12 && (
            <p className="mt-3 text-xs text-pizarra">
              y {sinDatos.length - 12} más.
            </p>
          )}
        </Tarjeta>
      )}
    </>
  );
}

function Fila({ producto }: { producto: ProyeccionDeProducto }) {
  const urgente =
    producto.diasHastaQuiebre !== null && producto.diasHastaQuiebre <= DIAS_TRANQUILOS;

  return (
    <li className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1 border-b border-arena pb-2.5 last:border-0 last:pb-0">
      <span className="min-w-0">
        <span className="block truncate text-[13px] text-marino">{producto.nombre}</span>
        <span className="text-xs text-pizarra">
          {producto.mesesConVentas} meses de ventas
          {producto.stock !== null &&
            ` · quedan ${formatearCantidad(producto.stock, producto.unidad)}`}
        </span>
      </span>

      <span className="shrink-0 text-right">
        <span className="block text-[13px] font-semibold text-marino">
          {formatearCantidad(producto.esperado ?? 0, producto.unidad)}
        </span>
        <span className={cn("text-xs", urgente ? "text-ambar-hondo" : "text-pizarra")}>
          {producto.diasHastaQuiebre === null
            ? "no llevas inventario"
            : `stock para ${producto.diasHastaQuiebre} días`}
        </span>
      </span>
    </li>
  );
}

/** «2026-03» se lee «mar 26», que es lo que cabe en un eje. */
function mesCorto(mes: string): string {
  const [ano, numero] = mes.split("-");
  const nombres = [
    "ene",
    "feb",
    "mar",
    "abr",
    "may",
    "jun",
    "jul",
    "ago",
    "sep",
    "oct",
    "nov",
    "dic",
  ];
  return `${nombres[Number(numero) - 1] ?? mes} ${ano.slice(2)}`;
}
