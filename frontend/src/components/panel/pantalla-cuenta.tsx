"use client";

import { useSesion } from "@/components/sesion/usar-sesion";
import { cerrarSesion } from "@/lib/api/sesion";
import { Cabecera, Cargando, SinConectar, Tarjeta } from "./piezas";

export function PantallaCuenta() {
  const { sesion, hidratado } = useSesion();

  if (!hidratado || !sesion) return <Cargando />;

  return (
    <>
      <Cabecera titulo="Tu cuenta" descripcion="Tus datos y tu sesión." />

      <Tarjeta>
        <p className="text-[13px] font-semibold text-marino">{sesion.usuario.nombre}</p>
        <p className="mt-1 text-[14px] text-pizarra">
          {sesion.usuario.email} · {sesion.usuario.rolNombre}
        </p>
        <button
          type="button"
          onClick={cerrarSesion}
          className="mt-4 h-11 cursor-pointer rounded-[12px] border border-niebla px-5 text-[14px] font-semibold text-acero transition-colors hover:bg-cielo"
        >
          Cerrar sesión
        </button>
      </Tarjeta>

      <div className="mt-4">
        <SinConectar seccion="El cambio de contraseña" />
      </div>
    </>
  );
}
