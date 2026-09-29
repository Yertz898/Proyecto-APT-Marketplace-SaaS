"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { useSesion } from "@/components/sesion/usar-sesion";
import { cerrarSesion } from "@/lib/api/sesion";
import { cn } from "@/lib/utils";

/*
 * Entrada y salida de la cuenta, en el encabezado de la tienda.
 *
 * El enlace lleva de vuelta a la página donde estaba: quien iba a reservar una
 * hora no debería quedar en la portada después de entrar.
 *
 * Mientras el navegador no haya leído la sesión se muestra igual "Iniciar
 * sesión". Es lo mismo que verá quien no tenga cuenta, y corregirlo dura un
 * cuadro; esconder el botón dejaría el encabezado saltando en cada carga.
 */
export function Cuenta({
  slug,
  variante,
  onNavegar,
}: {
  slug: string;
  variante: "escritorio" | "movil";
  onNavegar?: () => void;
}) {
  const { sesion } = useSesion();
  const ruta = usePathname();

  const movil = variante === "movil";
  const clases = cn(
    "cursor-pointer border border-lila/40 bg-transparent font-medium text-texto transition-colors hover:bg-violeta/18",
    movil
      ? "mt-[26px] flex h-[46px] w-full items-center justify-center rounded-[23px] text-[13px]"
      : "flex h-10 items-center rounded-[20px] px-[18px] text-[13px]",
  );

  if (sesion) {
    return (
      <div className={cn(movil ? "mt-[26px]" : "flex items-center gap-3")}>
        <span className={cn("text-[13px] text-texto-suave", movil ? "block" : "hidden xl:inline")}>
          {sesion.usuario.nombre}
        </span>
        <button
          type="button"
          onClick={() => {
            cerrarSesion();
            onNavegar?.();
          }}
          className={cn(clases, movil && "mt-3")}
        >
          Cerrar sesión
        </button>
      </div>
    );
  }

  return (
    <Link
      href={`/t/${slug}/entrar?volver=${encodeURIComponent(ruta)}`}
      onClick={onNavegar}
      className={clases}
    >
      Iniciar sesión
    </Link>
  );
}
