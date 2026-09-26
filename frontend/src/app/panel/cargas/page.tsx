import Link from "next/link";

import { HistorialDeCargas } from "@/components/panel/historial";
import { obtenerHistorialDeCargas } from "@/lib/api/panel";
import { TIPOS_DE_CARGA } from "@/lib/cargas";

/** Índice de la carga masiva: un tipo de carga por tarjeta, más el historial. */
export default async function PaginaCargas() {
  const historial = await obtenerHistorialDeCargas();

  return (
    <>
      <h1 className="font-serif text-[32px] font-medium text-texto">Carga masiva</h1>
      <p className="mt-2 max-w-[640px] text-sm text-texto-suave">
        Cada tipo de carga tiene su propia plantilla y su propia revisión. Ningún archivo se aplica sin que lo
        confirmes.
      </p>

      <div className="mt-8 grid gap-4 md:grid-cols-3">
        {Object.entries(TIPOS_DE_CARGA).map(([tipo, configuracion]) => (
          <Link
            key={tipo}
            href={`/panel/cargas/${tipo}`}
            className="flex flex-col rounded-2xl border border-lila/12 bg-superficie p-5 transition-colors hover:border-lila/45"
          >
            <span className="font-serif text-[21px] text-texto">{configuracion.titulo}</span>
            <span className="mt-2 flex-1 text-[13px] leading-[1.55] text-texto-suave">
              {configuracion.descripcion}
            </span>
            <span className="mt-4 text-xs text-lila">
              {configuracion.extensiones.join(" o ")} →
            </span>
          </Link>
        ))}
      </div>

      <section className="mt-12">
        <h2 className="font-serif text-[22px] text-texto">Historial</h2>
        <HistorialDeCargas cargas={historial} />
      </section>
    </>
  );
}
