"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { obtenerHistorialDeCargas } from "@/lib/api/panel";
import { TIPOS_DE_CARGA } from "@/lib/cargas";
import type { CargaHistorial } from "@/lib/tipos-panel";

import { HistorialDeCargas } from "./historial";
import { Cabecera } from "./piezas";

/*
 * Índice de la carga masiva: un tipo por tarjeta, más el historial.
 *
 * Es de cliente y no de servidor porque el historial se pide con la sesión, y
 * la sesión vive en el navegador. En servidor la petición saldría sin token y
 * el historial llegaría siempre vacío, sin que nada fallara a gritos.
 */
export function PantallaCargas() {
  const [historial, setHistorial] = useState<CargaHistorial[]>([]);

  const cargar = useCallback(() => {
    obtenerHistorialDeCargas().then(setHistorial);
  }, []);

  useEffect(cargar, [cargar]);

  return (
    <>
      <Cabecera
        titulo="Carga masiva"
        descripcion="Cada tipo de carga tiene su propia plantilla y su propia revisión. Ningún archivo se aplica sin que lo confirmes."
      />

      <div className="grid gap-4 md:grid-cols-3">
        {Object.entries(TIPOS_DE_CARGA).map(([tipo, configuracion]) => (
          <Link
            key={tipo}
            href={`/panel/cargas/${tipo}`}
            className="flex flex-col rounded-[14px] border border-arena bg-white p-5 text-marino no-underline transition-colors hover:border-niebla hover:bg-cielo hover:no-underline"
          >
            <span className="font-jakarta text-[17px] font-bold">{configuracion.titulo}</span>
            <span className="mt-2 flex-1 text-[13px] leading-[1.55] text-pizarra">
              {configuracion.descripcion}
            </span>
            <span className="mt-4 text-xs font-semibold text-acero">
              {configuracion.extensiones.join(" o ")} →
            </span>
          </Link>
        ))}
      </div>

      <section className="mt-12">
        <h2 className="font-jakarta text-[20px] font-bold text-marino">Historial</h2>
        <HistorialDeCargas cargas={historial} />
      </section>
    </>
  );
}
