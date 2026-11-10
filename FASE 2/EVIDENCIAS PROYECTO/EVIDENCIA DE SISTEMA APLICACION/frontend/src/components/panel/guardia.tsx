"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";

import { esAdminDePlataforma, trabajaEnTienda, useSesion } from "@/components/sesion/usar-sesion";
import { cerrarSesion } from "@/lib/api/sesion";

import { BloqueadaPorPlan, Cargando, SinPermiso } from "./piezas";
import { planAlcanza, rolAlcanza, seccionDe } from "./secciones";

/*
 * Puerta del panel.
 *
 * Esto NO protege nada: es la cortesía de no mostrar una pantalla que no va a
 * funcionar. Quien protege los datos es el backend, que exige el token, el rol
 * y el plan en cada endpoint. Un guardia de frontend se salta escribiendo la
 * dirección o borrando un nodo del DOM.
 *
 * Por eso lo que hace acá es explicar, no esconder: quien no tiene acceso ve
 * por qué y qué puede hacer al respecto.
 */
export function GuardiaDelPanel({ children }: { children: ReactNode }) {
  const { sesion, hidratado } = useSesion();
  const router = useRouter();
  const ruta = usePathname();

  const hayQueEntrar = hidratado && !sesion;

  useEffect(() => {
    if (hayQueEntrar) {
      router.replace(`/panel/entrar?volver=${encodeURIComponent(ruta)}`);
    }
  }, [hayQueEntrar, router, ruta]);

  // Antes de que el navegador lea el almacenamiento, "sin sesión" no quiere
  // decir que no haya: quiere decir que todavía no se sabe.
  if (!hidratado || hayQueEntrar) {
    return <Cargando />;
  }

  if (!trabajaEnTienda(sesion)) {
    return <CuentaSinPanel esDePlataforma={esAdminDePlataforma(sesion)} />;
  }

  const seccion = seccionDe(ruta);
  if (seccion) {
    if (!rolAlcanza(sesion?.usuario.rol, seccion)) {
      return (
        <SinPermiso detalle={`«${seccion.etiqueta}» es solo para el dueño de la tienda.`} />
      );
    }
    if (!planAlcanza(sesion?.usuario.tienda?.plan, seccion.plan)) {
      return <BloqueadaPorPlan plan={seccion.plan} etiqueta={seccion.etiqueta} />;
    }
  }

  return <>{children}</>;
}

/**
 * Hay sesión, pero no es de alguien que trabaje en esta tienda.
 *
 * Se explica en vez de redirigir: mandar de vuelta al formulario con la sesión
 * iniciada deja dando vueltas sin entender por qué. Y a quien sí tiene un lugar
 * a dónde ir, se le ofrece.
 */
function CuentaSinPanel({ esDePlataforma }: { esDePlataforma: boolean }) {
  return (
    <div className="mx-auto max-w-[460px] py-16 text-center">
      <h1 className="font-jakarta text-[26px] font-extrabold text-marino">
        Esta cuenta no tiene panel
      </h1>
      <p className="mt-3 text-sm text-pizarra">
        {esDePlataforma
          ? "Tu cuenta administra la plataforma, no una tienda en particular."
          : "El panel es para el dueño y los vendedores de una tienda. Tu cuenta es de comprador."}
      </p>

      <div className="mt-6 flex justify-center gap-3">
        <button
          type="button"
          onClick={cerrarSesion}
          className="h-11 cursor-pointer rounded-[12px] border border-niebla px-5 text-[13px] font-semibold text-acero transition-colors hover:bg-cielo"
        >
          Cerrar sesión
        </button>
        <Link
          href={esDePlataforma ? "/plataforma" : "/"}
          className="flex h-11 items-center rounded-[12px] bg-acero px-5 text-[13px] font-semibold text-white no-underline hover:no-underline"
        >
          {esDePlataforma ? "Ir a la administración" : "Ir al inicio"}
        </Link>
      </div>
    </div>
  );
}
