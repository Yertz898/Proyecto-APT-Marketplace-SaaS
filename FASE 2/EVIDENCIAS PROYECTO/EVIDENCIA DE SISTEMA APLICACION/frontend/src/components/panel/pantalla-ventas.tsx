"use client";

import { useCallback, useEffect, useState } from "react";

import { obtenerResumenDeVentas } from "@/lib/api/pedidos";
import { formatearPesos } from "@/lib/formato";
import type { ResumenDeVentas } from "@/lib/tipos-panel";
import { cn } from "@/lib/utils";

import { Cabecera, Cargando, Error as Aviso, Tarjeta, Vacio } from "./piezas";

/*
 * Las ventas de la tienda.
 *
 * Todo lo de esta pantalla está **medido**: sale de sumar pedidos que
 * existen. El pronóstico de demanda y los segmentos de compradores no están
 * acá a propósito; cuando existan irán en sus propias pantallas, porque en
 * una sola nadie distinguiría qué número se midió y cuál se estimó.
 *
 * Los tres indicadores responden a tres preguntas del dueño: cuánto llevo
 * este mes, qué me conviene reponer y qué tengo detenido.
 */

export function PantallaVentas() {
  const [resumen, setResumen] = useState<ResumenDeVentas | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);

  const cargar = useCallback(() => {
    obtenerResumenDeVentas()
      .then((suyo) => {
        setResumen(suyo);
        setFallo(null);
      })
      .catch((error: unknown) =>
        setFallo(
          error instanceof Error ? error.message : "No pudimos cargar tus ventas.",
        ),
      );
  }, []);

  useEffect(cargar, [cargar]);

  const cabecera = (
    <Cabecera
      titulo="Panel de ventas"
      descripcion="Cuánto vendiste, qué se mueve y qué está detenido."
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

  if (resumen === null) {
    return (
      <>
        {cabecera}
        <Cargando texto="Sumando tus pedidos…" />
      </>
    );
  }

  const sinVentas = resumen.ventas.pedidos === 0 && resumen.porCoordinar.pedidos === 0;

  return (
    <>
      {cabecera}

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <Indicador
          titulo={`Ventas de ${resumen.mes.etiqueta}`}
          valor={formatearPesos(resumen.ventas.total)}
          detalle={`${resumen.ventas.pedidos} ${plural(resumen.ventas.pedidos, "pedido", "pedidos")} · ${formatearPesos(resumen.ventas.neto)} neto`}
          comparacion={resumen.mesAnterior.variacion}
        />
        <Indicador
          titulo="Por coordinar"
          valor={formatearPesos(resumen.porCoordinar.total)}
          detalle={`${resumen.porCoordinar.pedidos} ${plural(resumen.porCoordinar.pedidos, "pedido pendiente", "pedidos pendientes")}`}
        />
        <Indicador
          titulo="Mes anterior"
          valor={formatearPesos(resumen.mesAnterior.total)}
          detalle={`${resumen.mesAnterior.pedidos} ${plural(resumen.mesAnterior.pedidos, "pedido", "pedidos")}`}
        />
      </div>

      <p className="mt-3 text-xs leading-[1.5] text-pizarra">
        Un pedido cuenta como venta cuando lo confirmas. Los pendientes van aparte,
        porque el pago se coordina fuera de la plataforma; los anulados no se cuentan.
      </p>

      {sinVentas ? (
        <div className="mt-4">
          <Vacio
            titulo="Todavía no hay ventas que mostrar"
            detalle="Cuando alguien confirme un pedido en tu vitrina, acá vas a ver cuánto llevas en el mes y qué productos se mueven."
          />
        </div>
      ) : (
        <div className="mt-4 grid gap-3 lg:grid-cols-2">
          <Tarjeta>
            <h2 className="text-[13px] font-semibold text-marino">
              Lo que más te dejó
            </h2>
            <p className="mt-1 text-xs text-pizarra">
              Últimos {resumen.diasDeVentana} días, ordenado por dinero y no por
              unidades.
            </p>

            {resumen.masVendidos.length === 0 ? (
              <p className="mt-4 text-[13px] text-pizarra">
                Sin ventas en este período.
              </p>
            ) : (
              <ul className="mt-3.5 flex flex-col gap-2.5">
                {resumen.masVendidos.map((producto) => (
                  <li key={producto.codigo} className="flex justify-between gap-4">
                    <span className="min-w-0">
                      <span className="block truncate text-[13px] text-marino">
                        {producto.nombre}
                      </span>
                      <span className="text-xs text-pizarra">
                        {sinCerosDeAdorno(producto.cantidad)}{" "}
                        {plural(Number(producto.cantidad), "vendido", "vendidos")}
                      </span>
                    </span>
                    <span className="shrink-0 text-[13px] font-semibold text-marino">
                      {formatearPesos(producto.neto)}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </Tarjeta>

          <Tarjeta>
            <h2 className="text-[13px] font-semibold text-marino">Sin movimiento</h2>
            <p className="mt-1 text-xs text-pizarra">
              Publicados hace más de {resumen.diasDeVentana} días y sin vender en ese
              tiempo.
            </p>

            {resumen.sinMovimiento.length === 0 ? (
              <p className="mt-4 text-[13px] text-pizarra">
                Todo lo que llevas publicado se ha vendido al menos una vez.
              </p>
            ) : (
              <ul className="mt-3.5 flex flex-col gap-2.5">
                {resumen.sinMovimiento.map((producto) => (
                  <li key={producto.codigo} className="flex justify-between gap-4">
                    <span className="min-w-0">
                      <span className="block truncate text-[13px] text-marino">
                        {producto.nombre}
                      </span>
                      <span className="text-xs text-pizarra">
                        {producto.diasSinVender === null
                          ? "Nunca se ha vendido"
                          : `Última venta hace ${producto.diasSinVender} días`}
                      </span>
                    </span>
                    <span className="shrink-0 text-[13px] text-pizarra">
                      {formatearPesos(producto.precioNeto)}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </Tarjeta>
        </div>
      )}
    </>
  );
}

function Indicador({
  titulo,
  valor,
  detalle,
  comparacion,
}: {
  titulo: string;
  valor: string;
  detalle: string;
  /** Variación contra el mes anterior, entre 0 y 1. Null si no hay con qué comparar. */
  comparacion?: number | null;
}) {
  return (
    <Tarjeta>
      <p className="text-xs text-pizarra">{titulo}</p>
      <p className="mt-1.5 text-[22px] font-semibold text-marino">{valor}</p>
      <p className="mt-1 text-xs text-pizarra">{detalle}</p>

      {comparacion !== undefined && comparacion !== null && (
        <p
          className={cn(
            "mt-2 text-xs font-semibold",
            comparacion >= 0 ? "text-acero" : "text-ambar-hondo",
          )}
        >
          {comparacion >= 0 ? "▲" : "▼"} {Math.abs(Math.round(comparacion * 100))}%
          <span className="font-normal text-pizarra"> contra el mes anterior</span>
        </p>
      )}
    </Tarjeta>
  );
}

function plural(cuantos: number, singular: string, plural: string): string {
  return cuantos === 1 ? singular : plural;
}

/** «10.00» se lee «10»; «650.00» se lee «650». */
function sinCerosDeAdorno(cantidad: string): string {
  const numero = Number(cantidad);
  if (!Number.isFinite(numero)) {
    return cantidad;
  }
  return numero.toLocaleString("es-CL", { maximumFractionDigits: 3 });
}
