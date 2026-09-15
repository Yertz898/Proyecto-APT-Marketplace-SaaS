import type { ReactNode } from "react";

import type { ColumnaPie, ContenidoTienda } from "@/lib/tipos";
import { cn } from "@/lib/utils";

import { EnlaceExterno } from "./enlace-externo";
import { IconoInstagram, IconoWhatsapp } from "./iconos";
import { Marca } from "./marca";

const CLASES_ICONO_RED = "fill-texto-suave transition-[fill] duration-200 hover:fill-lila";

/** Pie de página de la tienda (mockup 1A en escritorio, 1D en móvil). */
export function Pie({ tienda }: { tienda: ContenidoTienda }) {
  const { pie, redes } = tienda;

  return (
    <footer className="border-t border-violeta bg-tinta-honda">
      <div className="hidden lg:block">
        <div className="mx-auto grid max-w-[1280px] grid-cols-[1.4fr_.8fr_.8fr_.8fr_1.2fr] gap-10 px-6 pt-[58px] pb-[30px]">
          <div>
            <Marca tienda={tienda} lugar="pie" />
            <p className="mt-3.5 max-w-[250px] text-[13px] leading-[1.6] text-texto-suave">{pie.descripcion}</p>
            <Redes redes={redes} tamano={22} className="mt-[18px]" />
          </div>

          {pie.columnas.map((columna) => (
            <Columna key={columna.titulo} columna={columna} />
          ))}

          <div>
            <TituloColumna>{pie.escribenos.titulo}</TituloColumna>
            <p className="mt-3.5 text-[13px] leading-[1.6] text-texto-suave">{pie.escribenos.texto}</p>
            <BotonWhatsapp enlace={redes.whatsapp} className="mt-4 h-[46px] px-5 text-[13px]">
              {pie.escribenos.boton}
            </BotonWhatsapp>
          </div>
        </div>

        <div className="mx-auto flex max-w-[1280px] justify-between border-t border-texto/8 px-6 pt-[22px] pb-[34px] text-xs text-texto-suave">
          <span>{pie.derechos}</span>
          <span>Tienda operada sobre DealCommerce</span>
        </div>
      </div>

      <div className="px-5 pt-[30px] pb-[26px] lg:hidden">
        <Marca tienda={tienda} lugar="pie-movil" />
        <p className="mt-2.5 text-[13px] leading-[1.6] text-texto-suave">{pie.movil.descripcion}</p>
        <BotonWhatsapp enlace={redes.whatsapp} className="mt-[18px] h-12 w-full justify-center text-sm">
          {pie.escribenos.boton}
        </BotonWhatsapp>

        <div className="mt-6 grid grid-cols-2 gap-[22px]">
          {pie.movil.columnas.map((columna) => (
            <Columna key={columna.titulo} columna={columna} movil />
          ))}
        </div>

        <Redes redes={redes} tamano={21} className="mt-[22px]" />

        <p className="mt-[22px] border-t border-texto/8 pt-4 text-[11px] leading-[1.6] text-texto-suave">
          {pie.movil.derechos}
          <br />
          Tienda operada sobre DealCommerce
        </p>
      </div>
    </footer>
  );
}

function TituloColumna({ children, movil = false }: { children: ReactNode; movil?: boolean }) {
  return (
    <div className={cn("font-semibold tracking-[.14em] text-texto uppercase", movil ? "text-[10px]" : "text-[11px]")}>
      {children}
    </div>
  );
}

function Columna({ columna, movil = false }: { columna: ColumnaPie; movil?: boolean }) {
  return (
    <div>
      <TituloColumna movil={movil}>{columna.titulo}</TituloColumna>
      <ul className={cn("flex flex-col text-[13px]", movil ? "mt-3 gap-[9px]" : "mt-3.5 gap-2.5")}>
        {columna.enlaces.map((enlace) => (
          <li key={enlace}>
            <span
              data-pendiente="pie"
              aria-disabled="true"
              className="cursor-default text-lila transition-colors hover:text-lila-claro"
            >
              {enlace}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function Redes({
  redes,
  tamano,
  className,
}: {
  redes: ContenidoTienda["redes"];
  tamano: number;
  className?: string;
}) {
  return (
    <div className={cn("flex gap-3.5", className)}>
      <EnlaceExterno enlace={redes.instagram} etiqueta="Instagram">
        <IconoInstagram tamano={tamano} className={CLASES_ICONO_RED} />
      </EnlaceExterno>
      <EnlaceExterno enlace={redes.whatsapp} etiqueta="WhatsApp">
        <IconoWhatsapp tamano={tamano} className={CLASES_ICONO_RED} />
      </EnlaceExterno>
    </div>
  );
}

function BotonWhatsapp({
  enlace,
  className,
  children,
}: {
  enlace: string | null;
  className?: string;
  children: ReactNode;
}) {
  return (
    <EnlaceExterno
      enlace={enlace}
      className={cn(
        "flex cursor-pointer items-center gap-2.5 rounded-full bg-violeta font-semibold text-white transition-colors hover:bg-violeta-hover",
        className,
      )}
    >
      <IconoWhatsapp tamano={18} solido className="fill-white" />
      {children}
    </EnlaceExterno>
  );
}
