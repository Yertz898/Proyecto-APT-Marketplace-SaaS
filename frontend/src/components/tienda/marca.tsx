import Image from "next/image";

import type { IdentidadTienda } from "@/lib/tipos";
import { cn } from "@/lib/utils";

const MEDIDAS = {
  encabezado: "text-[25px]",
  movil: "text-[21px]",
  pie: "text-[23px]",
} as const;

type Props = {
  tienda: Pick<IdentidadTienda, "nombre" | "logo">;
  lugar: keyof typeof MEDIDAS;
};

/**
 * Logo y nombre de la tienda.
 *
 * Si la tienda todavía no subió su logo, se muestra solo el nombre: no se dibuja
 * ninguna marca de relleno.
 */
export function Marca({ tienda, lugar }: Props) {
  const { logo } = tienda;

  return (
    <div className="flex items-center gap-[9px]">
      {logo && <Image src={logo.url} alt={logo.alt} width={120} height={32} className="h-8 w-auto" />}
      <span className={cn("font-serif text-texto", MEDIDAS[lugar])}>{tienda.nombre}</span>
    </div>
  );
}
