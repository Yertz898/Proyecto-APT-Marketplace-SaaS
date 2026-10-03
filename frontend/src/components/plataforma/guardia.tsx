"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";

import { esAdminDePlataforma, useSesion } from "@/components/sesion/usar-sesion";
import { cerrarSesion } from "@/lib/api/sesion";

/*
 * Puerta de la administración de la plataforma.
 *
 * Igual que la del panel de tienda, esto no protege nada: es la cortesía de no
 * mostrar una pantalla que no va a funcionar. Quien protege los datos es el
 * backend, que exige el rol en cada endpoint.
 */
export function GuardiaDePlataforma({ children }: { children: ReactNode }) {
  const { sesion, hidratado } = useSesion();
  const router = useRouter();
  const ruta = usePathname();

  const hayQueEntrar = hidratado && !sesion;

  useEffect(() => {
    if (hayQueEntrar) {
      router.replace(`/panel/entrar?volver=${encodeURIComponent(ruta)}`);
    }
  }, [hayQueEntrar, router, ruta]);

  if (!hidratado || hayQueEntrar) {
    return (
      <p role="status" className="py-16 text-center text-sm text-pizarra">
        Cargando…
      </p>
    );
  }

  if (!esAdminDePlataforma(sesion)) {
    return <CuentaSinPlataforma esDeTienda={Boolean(sesion?.usuario.tienda)} />;
  }

  return <>{children}</>;
}

/**
 * Hay sesión, pero no es de la plataforma.
 *
 * Se explica en vez de redirigir: a quien trabaja en una tienda se le ofrece su
 * propio panel, que es donde sí tiene algo que hacer.
 */
function CuentaSinPlataforma({ esDeTienda }: { esDeTienda: boolean }) {
  return (
    <div className="mx-auto max-w-[460px] py-16 text-center">
      <h1 className="font-jakarta text-[28px] font-extrabold text-marino">
        Esta cuenta no administra la plataforma
      </h1>
      <p className="mt-3 text-sm text-pizarra">
        {esDeTienda
          ? "Tu cuenta es de una tienda suscrita. Su panel es otro."
          : "Esta sección es para la administración de DealCommerce."}
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
          href={esDeTienda ? "/panel" : "/"}
          className="flex h-11 items-center rounded-[12px] bg-acero px-5 text-[13px] font-semibold text-white no-underline hover:no-underline"
        >
          {esDeTienda ? "Ir a mi panel" : "Ir al inicio"}
        </Link>
      </div>
    </div>
  );
}
