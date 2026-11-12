"use client";

import { useCallback, useEffect, useState, type ReactNode } from "react";

import { obtenerSegmentos } from "@/lib/api/pedidos";
import { formatearPesos } from "@/lib/formato";
import type { NombreDeSegmento, SegmentacionDeCompradores } from "@/lib/tipos-panel";
import { cn } from "@/lib/utils";

import { ATENUADO, BarraSegmentada, SERIE } from "./graficos";
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

/**
 * El color de cada grupo, y acá el color significa algo.
 *
 * No son cuatro colores de serie repartidos por orden: verde es que va bien,
 * ámbar es que hay que mirarlo y gris es que ya no pide nada. «Perdido» va
 * gris a propósito: son mil doscientos y si llevaran color se comerían la
 * pantalla, cuando el grupo sobre el que se puede hacer algo es «en riesgo».
 *
 * El nombre del grupo está escrito al lado en todos los casos, así que la
 * identidad nunca depende solo del color.
 */
const COLOR: Record<NombreDeSegmento, string> = {
  habitual: SERIE[1],
  nuevo: SERIE[0],
  en_riesgo: SERIE[2],
  perdido: ATENUADO,
};

/** Orden de lectura de la barra: del más sano al que ya se fue. */
const ORDEN_DE_LA_BARRA: NombreDeSegmento[] = [
  "habitual",
  "nuevo",
  "en_riesgo",
  "perdido",
];

export function PantallaSegmentos() {
  const [segmentos, setSegmentos] = useState<SegmentacionDeCompradores | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);
  // El filtro acota la lista de abajo, no los recuentos de arriba: esos son
  // de toda la tienda, y moverlos al filtrar haria que no cuadren con nada.
  const [filtro, setFiltro] = useState<NombreDeSegmento | null>(null);

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

  const visibles = filtro
    ? segmentos.clientes.filter((cliente) => cliente.segmento === filtro)
    : segmentos.clientes;
  const mayorGasto = Math.max(...segmentos.clientes.map((c) => c.monto), 1);

  return (
    <>
      {cabecera}

      <div className="mt-4 grid gap-3 sm:grid-cols-4">
        {ORDEN.map((segmento) => (
          <Tarjeta key={segmento}>
            <p className="flex items-center gap-1.5 text-xs text-pizarra">
              <span
                aria-hidden="true"
                style={{ background: COLOR[segmento] }}
                className="block size-2.5 shrink-0 rounded-[3px]"
              />
              {TITULO[segmento]}
            </p>
            <p className="mt-1.5 text-[22px] font-semibold text-marino">
              {segmentos.conteo[segmento]}
            </p>
            <p className="mt-1 text-xs leading-[1.45] text-pizarra">
              {segmentos.descripciones[segmento]}
            </p>
          </Tarjeta>
        ))}
      </div>

      <div className="mt-3">
        <BarraSegmentada
          partes={ORDEN_DE_LA_BARRA.map((segmento) => ({
            nombre: TITULO[segmento],
            valor: segmentos.conteo[segmento],
            color: COLOR[segmento],
          }))}
        />
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
          Primero quien más gastó y lleva tiempo sin volver. La barra compara lo que
          gastó cada uno contra el que más gastó de la lista.
        </p>

        <div className="mt-3 flex flex-wrap gap-2">
          <Filtro activo={filtro === null} onClic={() => setFiltro(null)}>
            Todos ({segmentos.clientes.length})
          </Filtro>
          {ORDEN.map((segmento) => {
            const cuantos = segmentos.clientes.filter(
              (c) => c.segmento === segmento,
            ).length;
            return cuantos === 0 ? null : (
              <Filtro
                key={segmento}
                activo={filtro === segmento}
                color={COLOR[segmento]}
                onClic={() => setFiltro(filtro === segmento ? null : segmento)}
              >
                {TITULO[segmento]} ({cuantos})
              </Filtro>
            );
          })}
        </div>

        <ul className="mt-3.5 flex flex-col gap-2.5">
          {visibles.map((cliente) => (
            <li
              key={cliente.nombre}
              className="border-b border-arena pb-2.5 last:border-0 last:pb-0"
            >
              <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
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
                  <span className="block text-[13px] font-semibold text-marino">
                    {formatearPesos(cliente.monto)}
                  </span>
                  <span className="text-xs text-pizarra">
                    {cliente.frecuencia}{" "}
                    {cliente.frecuencia === 1 ? "compra" : "compras"} · hace{" "}
                    {cliente.recencia} días
                  </span>
                </span>
              </div>

              <span
                aria-hidden="true"
                className="mt-1.5 block h-1.5 w-full overflow-hidden rounded-[2px] bg-lino"
              >
                <span
                  style={{
                    width: `${Math.max((cliente.monto / mayorGasto) * 100, 1.5)}%`,
                    background: COLOR[cliente.segmento],
                  }}
                  className="block h-full rounded-l-[2px] rounded-r-[4px]"
                />
              </span>
            </li>
          ))}
        </ul>
      </Tarjeta>
    </>
  );
}

/** Un filtro de la lista. Van todos en una fila, encima de lo que acotan. */
function Filtro({
  activo,
  color,
  onClic,
  children,
}: {
  activo: boolean;
  color?: string;
  onClic: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      aria-pressed={activo}
      onClick={onClic}
      className={cn(
        "flex cursor-pointer items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs transition-colors",
        activo
          ? "border-acero bg-cielo font-semibold text-acero"
          : "border-arena bg-white text-pizarra hover:border-acero hover:text-acero",
      )}
    >
      {color && (
        <span
          aria-hidden="true"
          style={{ background: color }}
          className="block size-2 shrink-0 rounded-[2px]"
        />
      )}
      {children}
    </button>
  );
}
