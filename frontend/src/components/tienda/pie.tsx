import type { IdentidadTienda } from "@/lib/tipos";

import { EnlaceExterno } from "./enlace-externo";
import { IconoInstagram, IconoWhatsapp } from "./iconos";
import { Marca } from "./marca";

const CLASES_ICONO = "fill-texto-suave transition-[fill] duration-200 hover:fill-lila";

/**
 * Pie de página de la tienda.
 *
 * Solo lleva lo que la plataforma puede afirmar por sí sola: la marca de la
 * tienda, sus redes si las cargó y el aviso de sobre qué plataforma opera. Las
 * columnas de enlaces del mockup eran contenido de Joyas_ye y salieron del
 * código: vuelven cuando cada tienda pueda definirlas desde su panel.
 */
export function Pie({ tienda }: { tienda: IdentidadTienda }) {
  const { redes } = tienda;
  const anio = new Date().getFullYear();

  return (
    <footer className="border-t border-violeta bg-tinta-honda">
      <div className="mx-auto flex max-w-[1280px] flex-col gap-6 px-5 py-10 lg:flex-row lg:items-center lg:px-6">
        <Marca tienda={tienda} lugar="pie" />

        {(redes.instagram || redes.whatsapp) && (
          <div className="flex gap-3.5 lg:ml-auto">
            {redes.instagram && (
              <EnlaceExterno enlace={redes.instagram} etiqueta="Instagram">
                <IconoInstagram tamano={22} className={CLASES_ICONO} />
              </EnlaceExterno>
            )}
            {redes.whatsapp && (
              <EnlaceExterno enlace={redes.whatsapp} etiqueta="WhatsApp">
                <IconoWhatsapp tamano={22} className={CLASES_ICONO} />
              </EnlaceExterno>
            )}
          </div>
        )}
      </div>

      <div className="mx-auto flex max-w-[1280px] flex-col gap-2 border-t border-texto/8 px-5 py-6 text-xs text-texto-suave lg:flex-row lg:justify-between lg:px-6">
        <span>
          © {anio} {tienda.nombre}
        </span>
        <span>Tienda operada sobre DealCommerce</span>
      </div>
    </footer>
  );
}
