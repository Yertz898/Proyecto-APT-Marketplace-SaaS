import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { CargaMasiva } from "@/components/panel/carga-masiva";
import { obtenerLimitesDeCarga } from "@/lib/api/panel";
import { esTipoDeCarga, TIPOS_DE_CARGA } from "@/lib/cargas";

export async function generateMetadata({ params }: PageProps<"/panel/cargas/[tipo]">): Promise<Metadata> {
  const { tipo } = await params;
  return esTipoDeCarga(tipo) ? { title: TIPOS_DE_CARGA[tipo].titulo } : {};
}

/** Pantalla de un tipo de carga: descargar plantilla, subir, revisar y confirmar. */
export default async function PaginaCarga({ params }: PageProps<"/panel/cargas/[tipo]">) {
  const { tipo } = await params;

  if (!esTipoDeCarga(tipo)) {
    notFound();
  }

  const limites = await obtenerLimitesDeCarga();

  return (
    <>
      <nav aria-label="Ubicación" className="text-xs text-texto-suave">
        <Link href="/panel/cargas" className="transition-colors hover:text-texto">
          Carga masiva
        </Link>
        {" · "}
        <span className="text-texto">{TIPOS_DE_CARGA[tipo].titulo}</span>
      </nav>

      <CargaMasiva tipo={tipo} limites={limites} />
    </>
  );
}
