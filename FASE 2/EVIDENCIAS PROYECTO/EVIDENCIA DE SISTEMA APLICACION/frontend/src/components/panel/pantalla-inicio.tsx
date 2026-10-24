"use client";

import Link from "next/link";
import { useSesion } from "@/components/sesion/usar-sesion";
import { Cabecera, Cargando, Tarjeta } from "./piezas";
import { NOMBRE_DEL_PLAN } from "./secciones";

/** Inicio del panel: quién eres, qué plan tienes y dónde está tu tienda. */
export function PantallaInicio() {
  const { sesion, hidratado } = useSesion();
  const tienda = sesion?.usuario.tienda;

  if (!hidratado || !tienda) return <Cargando />;

  return (
    <>
      <Cabecera titulo={tienda.nombre} descripcion={`Plan ${NOMBRE_DEL_PLAN[tienda.plan]}.`} />

      <Tarjeta>
        <p className="text-[13px] font-semibold text-marino">Tu tienda en línea</p>
        <p className="mt-1 text-[14px] text-pizarra">
          Este es el enlace que compartes con tus clientes.
        </p>
        <Link
          href={`/t/${tienda.slug}`}
          className="mt-3 inline-flex h-11 items-center rounded-[12px] border border-niebla px-4 text-[14px] font-semibold text-acero no-underline hover:bg-cielo hover:no-underline"
        >
          /t/{tienda.slug}
        </Link>
      </Tarjeta>

      <Tarjeta className="mt-4">
        <p className="text-[13px] font-semibold text-marino">Para empezar</p>
        <p className="mt-1 text-[14px] text-pizarra">
          Sube tu catálogo desde una planilla y queda publicado en tu tienda.
        </p>
        <Link
          href="/panel/cargas"
          className="mt-3 inline-flex h-11 items-center rounded-[12px] bg-acero px-5 text-[14px] font-semibold text-white no-underline hover:bg-acero-hondo hover:no-underline"
        >
          Ir a carga masiva
        </Link>
      </Tarjeta>
    </>
  );
}
