"use client";

import { useCallback, useEffect, useState } from "react";

import { obtenerSegmentos } from "@/lib/api/pedidos";
import { formatearPesos } from "@/lib/formato";
import type { NombreDeSegmento, SegmentacionDeCompradores } from "@/lib/tipos-panel";
import { cn } from "@/lib/utils";

import { Cabecera, Cargando, Error as Aviso, Tarjeta, Vacio } from "./piezas";

/*
 * Quiénes compran seguido, quiénes se están yendo y quiénes ya se fueron.
 *
 * La lista está ordenada por lo que más conviene mirar: primero quien más
 * gastó y lleva tiempo sin volver. No es una pantalla para leer entera, es
 * una lista de a quién escribirle.
 *
 * El umbral se muestra siempre. El número que decide quién está «perdido»
 * sale de los datos de cada tienda, y el dueño tiene derecho a saber de
 * dónde salió antes de darle a alguien por perdido.
 */

const TITULO: Record<NombreDeSegmento, string> = {
  habitual: "Habituales",
  nuevo: "Nuevos",
  en_riesgo: "En riesgo",
  perdido: "Perdidos",
};

const ETIQUETA: Record<NombreDeSegmento, string> = {
  habitual: "border-arena bg-hueso text-pizarra",
  nuevo: "border-niebla bg-cielo text-acero",
  en_riesgo: "border-ambar bg-trigo text-ambar-hondo",
  perdido: "border-niebla bg-hueso text-pizarra",
};

const ORDEN: NombreDeSegmento[] = ["en_riesgo", "habitual", "nuevo", "perdido"];

export function PantallaSegmentos() {
  const [segmentos, setSegmentos] = useState<SegmentacionDeCompradores | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);

  const cargar = useCallback(() => {
    obtenerSegmentos()
      .then((suyos) => {
        setSegmentos(suyos);
        setFallo(null);
      })
      .catch((error: unknown) =>
        setFallo(
          error instanceof Error ? error.message : "No pudimos agrupar a tus clientes.",
        ),
      );
  }, []);

  useEffect(cargar, [cargar]);

  const cabecera = (
    <Cabecera
      titulo="Segmentos"
      descripcion="Quiénes te compran seguido y quiénes dejaron de hacerlo."
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

  if (segmentos === null) {
    return (
      <>
        {cabecera}
        <Cargando texto="Mirando quién volvió y quién no…" />
      </>
    );
  }

  if (segmentos.clientes.length === 0) {
    return (
      <>
        {cabecera}
        <Vacio
          titulo="Todavía no hay compradores que agrupar"
          detalle="Cuando empiecen a comprar, acá vas a ver quiénes vuelven y quiénes no."
        />
      </>
    );
  }

  return (
    <>
      {cabecera}

      <div className="mt-4 grid gap-3 sm:grid-cols-4">
        {ORDEN.map((segmento) => (
          <Tarjeta key={segmento}>
            <p className="text-xs text-pizarra">{TITULO[segmento]}</p>
            <p className="mt-1.5 text-[22px] font-semibold text-marino">
              {segmentos.conteo[segmento]}
            </p>
            <p className="mt-1 text-xs leading-[1.45] text-pizarra">
              {segmentos.descripciones[segmento]}
            </p>
          </Tarjeta>
        ))}
      </div>

      <p className="mt-3 text-xs leading-[1.5] text-pizarra">
        Se considera que alguien dejó de comprar al pasar{" "}
        <strong className="font-semibold text-marino">
          {segmentos.umbralDeDias} días
        </strong>{" "}
        sin volver, y perdido al doble.{" "}
        {segmentos.umbralCalculado
          ? "Ese plazo sale de tus propios datos: nueve de cada diez veces, tus clientes vuelven antes."
          : "Ese plazo es el valor por omisión: todavía no tienes suficientes compras repetidas para calcular el tuyo."}{" "}
        Calculado con {segmentos.metodo}.
      </p>

      <Tarjeta className="mt-4">
        <h2 className="text-[13px] font-semibold text-marino">A quién escribirle</h2>
        <p className="mt-1 text-xs text-pizarra">
          Primero quien más gastó y lleva tiempo sin volver.
        </p>

        <ul className="mt-3.5 flex flex-col gap-2">
          {segmentos.clientes.map((cliente) => (
            <li
              key={cliente.nombre}
              className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1 border-b border-arena pb-2 last:border-0 last:pb-0"
            >
              <span className="flex min-w-0 items-center gap-2.5">
                <span className="truncate text-[13px] text-marino">
                  {cliente.nombre}
                </span>
                <span
                  className={cn(
                    "shrink-0 rounded-full border px-2 py-0.5 text-[11px] font-semibold",
                    ETIQUETA[cliente.segmento],
                  )}
                >
                  {TITULO[cliente.segmento]}
                </span>
              </span>

              <span className="shrink-0 text-right">
                <span className="block text-[13px] text-marino">
                  {formatearPesos(cliente.monto)}
                </span>
                <span className="text-xs text-pizarra">
                  {cliente.frecuencia}{" "}
                  {cliente.frecuencia === 1 ? "compra" : "compras"} · hace{" "}
                  {cliente.recencia} días
                </span>
              </span>
            </li>
          ))}
        </ul>
      </Tarjeta>
    </>
  );
}
