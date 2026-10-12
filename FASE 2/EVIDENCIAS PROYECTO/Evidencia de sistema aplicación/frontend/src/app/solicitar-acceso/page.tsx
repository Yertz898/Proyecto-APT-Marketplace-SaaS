import type { Metadata } from "next";

import { Pie } from "@/components/portada/cierre";
import { Encabezado } from "@/components/portada/encabezado";
import { FormularioDeAcceso } from "@/components/portada/formulario-acceso";

export const metadata: Metadata = {
  title: "Solicitar acceso · DealCommerce",
  description: "Cuéntanos de tu negocio y te ayudamos a montar tu catálogo mayorista en línea.",
};

/**
 * Solicitud de acceso a la plataforma.
 *
 * Es el destino del botón principal de la portada. En DealCommerce nadie se
 * registra solo como vendedor: las cuentas de dueño y de vendedor las crea el
 * equipo, y esto es lo que pasa antes.
 */
export default function PaginaSolicitarAcceso() {
  return (
    <div data-tema="claro" className="@container flex min-h-dvh w-full flex-col bg-hueso font-inter text-marino">
      <Encabezado />

      <main className="mx-auto w-full max-w-[560px] flex-1 px-[clamp(20px,5.5cqi,80px)] py-[clamp(40px,5cqi,72px)]">
        <div className="mb-8 flex flex-col gap-3">
          <span className="text-[13px] font-semibold tracking-[0.06em] text-acero uppercase">
            Solicitar acceso
          </span>
          <h1 className="font-jakarta text-[clamp(30px,3.3cqi,44px)] leading-[1.08] font-extrabold tracking-[-0.03em] text-balance">
            Cuéntanos de tu negocio
          </h1>
          <p className="text-[17px] leading-[1.55] text-pizarra text-pretty">
            Estamos abriendo DealCommerce de a poco, acompañando a cada tienda en su primera carga.
          </p>
        </div>

        <FormularioDeAcceso />
      </main>

      <Pie />
    </div>
  );
}
