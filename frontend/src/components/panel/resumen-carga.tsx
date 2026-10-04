"use client";

import { useState } from "react";

import { Checkbox } from "@/components/ui/checkbox";
import type { ResumenCarga, ResumenFotos } from "@/lib/tipos-panel";

/*
 * Revisión previa de una carga. Todavía no se escribió nada en la base.
 *
 * Todos los valores que vienen del archivo se muestran como texto. Nunca se
 * interpretan como HTML: el contenido lo escribe una persona fuera del sistema.
 */

const CLASES_TARJETA = "rounded-[12px] border border-arena bg-hueso p-4";
const CLASES_BOTON_PRINCIPAL =
  "h-11 cursor-pointer rounded-[12px] bg-acero px-6 text-sm font-semibold text-white transition-colors hover:bg-acero-hondo";
const CLASES_BOTON_SECUNDARIO =
  "h-11 cursor-pointer rounded-[12px] border border-niebla bg-transparent px-6 text-sm font-semibold text-acero transition-colors hover:bg-cielo";

export function ResumenDeCarga({
  resumen,
  onConfirmar,
  onCancelar,
}: {
  resumen: ResumenCarga;
  onConfirmar: (desactivarAusentes: boolean) => void;
  onCancelar: () => void;
}) {
  const [desactivarAusentes, setDesactivarAusentes] = useState(false);

  return (
    <section className="mt-4 rounded-[14px] border border-arena bg-white p-5">
      <h2 className="text-[13px] font-semibold text-marino">Revisión</h2>
      <p className="mt-2 text-[13px] text-pizarra">
        Esto es lo que va a pasar si confirmas. Todavía no se ha escrito nada.
      </p>

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <Contador titulo="Se crearán" valor={resumen.crear} />
        <Contador titulo="Se actualizarán" valor={resumen.actualizar} />
        <Contador titulo="Se rechazarán" valor={resumen.rechazar} />
      </div>

      {resumen.rechazos.length > 0 && (
        <div className="mt-5">
          <h3 className="text-[13px] font-semibold text-marino">Filas rechazadas</h3>
          <p className="mt-1 text-xs text-pizarra">
            Una fila mala no bloquea a las demás: el resto se aplica igual.
          </p>
          <ul className="mt-3 flex flex-col gap-2">
            {resumen.rechazos.map((rechazo) => (
              <li key={rechazo.fila} className="rounded-[10px] border border-ambar bg-trigo px-3 py-2 text-[13px]">
                <span className="font-semibold text-marino">Fila {rechazo.fila}:</span>{" "}
                <span className="text-pizarra">{rechazo.motivo}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {resumen.ausentes.length > 0 && (
        <label className="mt-5 flex cursor-pointer items-start gap-3 rounded-[12px] border border-arena bg-hueso p-4">
          <Checkbox
            checked={desactivarAusentes}
            onCheckedChange={(marcado) => setDesactivarAusentes(marcado)}
            className="mt-0.5 size-4 rounded-[4px] border-niebla data-checked:border-acero data-checked:bg-acero"
          />
          <span className="text-[13px] text-pizarra">
            <span className="block font-semibold text-marino">
              Desactivar los {resumen.ausentes.length} que no vienen en este archivo
            </span>
            Quedan fuera de la tienda sin borrarse. Si no marcas esto, se ignoran y siguen como están.
          </span>
        </label>
      )}

      <div className="mt-6 flex flex-wrap gap-3">
        <button type="button" onClick={() => onConfirmar(desactivarAusentes)} className={CLASES_BOTON_PRINCIPAL}>
          Confirmar y aplicar
        </button>
        <button type="button" onClick={onCancelar} className={CLASES_BOTON_SECUNDARIO}>
          Cancelar
        </button>
      </div>
    </section>
  );
}

export function ResumenDeFotos({
  resumen,
  onConfirmar,
  onCancelar,
}: {
  resumen: ResumenFotos;
  onConfirmar: () => void;
  onCancelar: () => void;
}) {
  return (
    <section className="mt-4 rounded-[14px] border border-arena bg-white p-5">
      <h2 className="text-[13px] font-semibold text-marino">Revisión</h2>

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <Contador titulo="Fotos emparejadas" valor={resumen.emparejadas} />
        <Contador titulo="Lotes sin foto" valor={resumen.lotesSinFoto.length} />
        <Contador titulo="Fotos sin lote" valor={resumen.fotosSinLote.length} />
      </div>

      <ListaDeCodigos titulo="Lotes que quedarían sin foto" codigos={resumen.lotesSinFoto} />
      <ListaDeCodigos titulo="Fotos que no corresponden a ningún lote" codigos={resumen.fotosSinLote} />

      <div className="mt-6 flex flex-wrap gap-3">
        <button type="button" onClick={onConfirmar} className={CLASES_BOTON_PRINCIPAL}>
          Confirmar y aplicar
        </button>
        <button type="button" onClick={onCancelar} className={CLASES_BOTON_SECUNDARIO}>
          Cancelar
        </button>
      </div>
    </section>
  );
}

function Contador({ titulo, valor }: { titulo: string; valor: number }) {
  return (
    <div className={CLASES_TARJETA}>
      <div className="text-[11px] tracking-[.08em] text-pizarra uppercase">{titulo}</div>
      <div className="mt-1 font-jakarta text-[28px] font-extrabold text-marino">{valor}</div>
    </div>
  );
}

function ListaDeCodigos({ titulo, codigos }: { titulo: string; codigos: string[] }) {
  if (codigos.length === 0) {
    return null;
  }

  return (
    <div className="mt-5">
      <h3 className="text-[13px] font-semibold text-marino">{titulo}</h3>
      <ul className="mt-2 flex flex-wrap gap-2">
        {codigos.map((codigo) => (
          <li key={codigo} className="rounded-md border border-arena-honda bg-hueso px-2 py-1 text-xs text-pizarra">
            {codigo}
          </li>
        ))}
      </ul>
    </div>
  );
}
