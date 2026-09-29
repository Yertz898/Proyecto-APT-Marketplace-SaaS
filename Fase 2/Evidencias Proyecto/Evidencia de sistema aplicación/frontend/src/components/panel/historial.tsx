import { formatearFecha } from "@/lib/formato";
import type { CargaHistorial } from "@/lib/tipos-panel";
import { TIPOS_DE_CARGA } from "@/lib/cargas";

/** Historial de cargas: fecha, usuario, archivo y resultado. */
export function HistorialDeCargas({ cargas }: { cargas: CargaHistorial[] }) {
  if (cargas.length === 0) {
    return (
      <p className="mt-4 rounded-xl border border-lila/12 bg-superficie p-5 text-[13px] text-texto-suave">
        Todavía no hay cargas registradas.
      </p>
    );
  }

  return (
    <div className="mt-4 overflow-x-auto rounded-xl border border-lila/12">
      <table className="w-full min-w-[640px] text-left text-[13px]">
        <thead className="bg-superficie text-[11px] tracking-[.08em] text-texto-suave uppercase">
          <tr>
            <th className="px-4 py-3 font-semibold">Fecha</th>
            <th className="px-4 py-3 font-semibold">Tipo</th>
            <th className="px-4 py-3 font-semibold">Archivo</th>
            <th className="px-4 py-3 font-semibold">Usuario</th>
            <th className="px-4 py-3 font-semibold">Resultado</th>
          </tr>
        </thead>
        <tbody>
          {cargas.map((carga) => (
            <tr key={carga.id} className="border-t border-lila/12 text-texto-suave">
              <td className="px-4 py-3 whitespace-nowrap">{formatearFecha(carga.fecha)}</td>
              <td className="px-4 py-3">{TIPOS_DE_CARGA[carga.tipo].titulo}</td>
              <td className="px-4 py-3 text-texto">{carga.archivo}</td>
              <td className="px-4 py-3">{carga.usuario}</td>
              <td className="px-4 py-3">{carga.resultado}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
