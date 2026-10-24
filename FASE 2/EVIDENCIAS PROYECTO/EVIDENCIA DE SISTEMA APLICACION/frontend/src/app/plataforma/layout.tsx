import type { Metadata } from "next";

import { BarraDePlataforma } from "@/components/plataforma/barra";
import { GuardiaDePlataforma } from "@/components/plataforma/guardia";

export const metadata: Metadata = {
  title: { default: "Administración", template: "%s · DealCommerce" },
};

/*
 * Administración de DealCommerce.
 *
 * Es de la plataforma, no de una tienda: desde acá se ven todas las tiendas
 * suscritas. Por eso lleva la marca de DealCommerce y no la de ninguna tienda,
 * y vive fuera de /panel, que es el panel de una tienda concreta.
 */
export default function LayoutDePlataforma({ children }: LayoutProps<"/plataforma">) {
  return (
    <div
      data-tema="claro"
      className="@container flex min-h-dvh w-full flex-col bg-hueso font-inter text-marino"
    >
      <BarraDePlataforma />
      <main className="mx-auto w-full max-w-[1280px] flex-1 px-[clamp(20px,5.5cqi,80px)] py-10">
        <GuardiaDePlataforma>{children}</GuardiaDePlataforma>
      </main>
    </div>
  );
}
