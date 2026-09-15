import Image from "next/image";

import type { ContenidoTienda } from "@/lib/tipos";
import { cn } from "@/lib/utils";

import { IconoMarca } from "./iconos";

// Medidas de la marca en cada lugar donde aparece en el mockup.
const MEDIDAS = {
  encabezado: { icono: 22, texto: "text-[25px] tracking-[.02em]", separacion: "gap-[9px]" },
  movil: { icono: 18, texto: "text-[21px]", separacion: "gap-[7px]" },
  pie: { icono: 20, texto: "text-[23px]", separacion: "gap-[9px]" },
  "pie-movil": { icono: 18, texto: "text-[21px]", separacion: "gap-2" },
} as const;

type Props = {
  tienda: Pick<ContenidoTienda, "nombre" | "logo">;
  lugar: keyof typeof MEDIDAS;
};

/** Logo y nombre de la tienda. Sin logo cargado usa la marca dibujada en el mockup. */
export function Marca({ tienda, lugar }: Props) {
  const medidas = MEDIDAS[lugar];
  const { logo } = tienda;

  return (
    <div className={cn("flex items-center", medidas.separacion)}>
      {logo ? (
        <Image src={logo.src} alt={logo.incluyeNombre ? tienda.nombre : ""} width={logo.ancho} height={logo.alto} />
      ) : (
        <IconoMarca tamano={medidas.icono} />
      )}
      {!logo?.incluyeNombre && <span className={cn("font-serif text-texto", medidas.texto)}>{tienda.nombre}</span>}
    </div>
  );
}
