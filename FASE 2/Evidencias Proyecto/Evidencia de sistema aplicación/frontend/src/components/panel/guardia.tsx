"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";

import { trabajaEnTienda, useSesion } from "@/components/sesion/usar-sesion";
import { cerrarSesion } from "@/lib/api/sesion";

/*
 * Puerta del panel.
 *
 * Esto NO es la protección del panel: es la cortesía de no mostrar una pantalla
 * que no va a funcionar. Quien protege los datos es el backend, que exige el
 * token y el rol en cada endpoint. Un guardia de frontend se salta escribiendo
 * la dirección o borrando un nodo del DOM.
 */
export function GuardiaDelPanel({ children }: { children: ReactNode }) {
  const { sesion, hidratado } = useSesion();
  const router = useRouter();
  const ruta = usePathname();

  const puedeEntrar = trabajaEnTienda(sesion);
  const hayQueEntrar = hidratado && !sesion;

  useEffect(() => {
    if (hayQueEntrar) {
      router.replace(`/panel/entrar?volver=${encodeURIComponent(ruta)}`);
    }
  }, [hayQueEntrar, router, ruta]);

  // Antes de que el navegador lea el almacenamiento, "sin sesión" no quiere
  // decir que no haya: quiere decir que todavía no se sabe.
  if (!hidratado || hayQueEntrar) {
    return <Espera />;
  }

  if (!puedeEntrar) {
    return <CuentaSinPanel />;
  }

  return <>{children}</>;
}

function Espera() {
  return (
    <p className="py-16 text-center text-sm text-texto-suave" role="status">
      Cargando…
    </p>
  );
}

/**
 * Hay sesión, pero es de un comprador.
 *
 * Se explica en vez de redirigir: mandarlo de vuelta al formulario con la
 * sesión iniciada lo dejaría dando vueltas sin entender por qué.
 */
function CuentaSinPanel() {
  return (
    <div className="mx-auto max-w-[460px] py-16 text-center">
      <h1 className="font-serif text-[28px] text-texto">Esta cuenta no tiene panel</h1>
      <p className="mt-3 text-sm text-texto-suave">
        El panel es para el dueño y los vendedores de una tienda. Tu cuenta es de comprador.
      </p>

      <div className="mt-6 flex justify-center gap-3">
        <button
          type="button"
          onClick={cerrarSesion}
          className="h-11 cursor-pointer rounded-full border border-lila/40 px-5 text-[13px] text-texto transition-colors hover:bg-violeta/18"
        >
          Cerrar sesión
        </button>
        <Link
          href="/"
          className="flex h-11 items-center rounded-full bg-violeta px-5 text-[13px] font-semibold text-white"
        >
          Ir al inicio
        </Link>
      </div>
    </div>
  );
}
