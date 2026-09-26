"use client";

import { useState } from "react";

import { cancelarCarga, confirmarCarga, urlDePlantilla, validarCarga, validarFotos } from "@/lib/api/panel";
import { formatearTamano, revisarArchivo, TIPOS_DE_CARGA } from "@/lib/cargas";
import type { LimitesCarga, ResumenCarga, ResumenFotos, TipoCarga } from "@/lib/tipos-panel";

import { ResumenDeCarga, ResumenDeFotos } from "./resumen-carga";

/*
 * Flujo de una carga masiva: descargar plantilla, subir, revisar y confirmar.
 *
 * Nunca se aplica un archivo directo. El backend valida y devuelve un resumen
 * sin escribir nada; recién al confirmar se escribe.
 *
 * Lo que revisa el navegador (extensión y tamaño) es ayuda para el usuario, no
 * control de seguridad: el backend valida por contenido.
 */

type Estado =
  | { paso: "elegir" }
  | { paso: "validando" }
  | { paso: "revisar"; resumen: ResumenCarga }
  | { paso: "revisarFotos"; resumen: ResumenFotos }
  | { paso: "aplicada" }
  | { paso: "error"; mensaje: string };

export function CargaMasiva({ tipo, limites }: { tipo: TipoCarga; limites: LimitesCarga | null }) {
  const configuracion = TIPOS_DE_CARGA[tipo];
  const extensiones = limites?.extensiones ?? configuracion.extensiones;

  const [archivo, setArchivo] = useState<File | null>(null);
  const [rechazo, setRechazo] = useState<string | null>(null);
  const [estado, setEstado] = useState<Estado>({ paso: "elegir" });

  function elegirArchivo(elegido: File | null) {
    setEstado({ paso: "elegir" });

    if (!elegido) {
      setArchivo(null);
      setRechazo(null);
      return;
    }

    const revision = revisarArchivo(elegido, extensiones, limites);
    if (!revision.ok) {
      setArchivo(null);
      setRechazo(revision.mensaje);
      return;
    }

    setRechazo(null);
    setArchivo(elegido);
  }

  async function revisar() {
    if (!archivo) return;

    setEstado({ paso: "validando" });
    try {
      if (tipo === "fotos") {
        setEstado({ paso: "revisarFotos", resumen: await validarFotos(archivo) });
      } else {
        setEstado({ paso: "revisar", resumen: await validarCarga(tipo, archivo) });
      }
    } catch (error) {
      setEstado({ paso: "error", mensaje: mensajeDeError(error) });
    }
  }

  async function confirmar(cargaId: string, desactivarAusentes: boolean) {
    try {
      await confirmarCarga(cargaId, desactivarAusentes);
      setArchivo(null);
      setEstado({ paso: "aplicada" });
    } catch (error) {
      setEstado({ paso: "error", mensaje: mensajeDeError(error) });
    }
  }

  async function cancelar(cargaId: string) {
    try {
      await cancelarCarga(cargaId);
    } catch (error) {
      setEstado({ paso: "error", mensaje: mensajeDeError(error) });
      return;
    }
    setArchivo(null);
    setEstado({ paso: "elegir" });
  }

  return (
    <>
      <h1 className="mt-3 font-serif text-[32px] font-medium text-texto">{configuracion.titulo}</h1>
      <p className="mt-2 max-w-[640px] text-sm text-texto-suave">{configuracion.descripcion}</p>

      {configuracion.columnas.length > 0 && (
        <section className="mt-8 rounded-2xl border border-lila/12 bg-superficie p-5">
          <h2 className="text-[13px] font-semibold text-texto">1. Descargar la plantilla</h2>
          <p className="mt-2 text-[13px] text-texto-suave">
            Trae los encabezados exactos y una fila de ejemplo. Usa siempre esta plantilla: así ninguna tienda
            tiene que adivinar los nombres de las columnas.
          </p>
          <p className="mt-3 flex flex-wrap gap-2">
            {configuracion.columnas.map((columna) => (
              <code key={columna} className="rounded-md border border-lila/16 px-2 py-1 text-xs text-texto-suave">
                {columna}
              </code>
            ))}
          </p>
          <a
            href={urlDePlantilla(tipo)}
            className="mt-4 inline-flex h-10 items-center rounded-full border border-lila/40 px-5 text-[13px] font-medium text-texto transition-colors hover:bg-violeta/18"
          >
            Descargar plantilla
          </a>
        </section>
      )}

      <section className="mt-4 rounded-2xl border border-lila/12 bg-superficie p-5">
        <h2 className="text-[13px] font-semibold text-texto">
          {configuracion.columnas.length > 0 ? "2. Subir el archivo" : "1. Subir el archivo"}
        </h2>

        <p className="mt-2 text-[13px] text-texto-suave">
          Se acepta {extensiones.join(" o ")}
          {limites ? `, hasta ${formatearTamano(limites.tamanoMaximoBytes)}.` : "."}
          {tipo !== "fotos" && " Recomendamos .xlsx: conserva los tipos de dato y evita problemas de separadores."}
        </p>

        <input
          type="file"
          accept={extensiones.join(",")}
          aria-label="Archivo a cargar"
          onChange={(evento) => elegirArchivo(evento.target.files?.[0] ?? null)}
          className="mt-4 block w-full cursor-pointer rounded-xl border border-dashed border-lila/25 bg-transparent p-4 text-[13px] text-texto-suave file:mr-4 file:cursor-pointer file:rounded-full file:border-0 file:bg-violeta file:px-4 file:py-2 file:text-[13px] file:font-semibold file:text-white"
        />

        {rechazo && (
          <p role="alert" className="mt-3 rounded-xl border border-oro/28 bg-oro/8 p-3.5 text-[13px] text-texto-suave">
            {rechazo}
          </p>
        )}

        {archivo && (
          <p className="mt-3 text-[13px] text-texto-suave">
            Elegido: <span className="text-texto">{archivo.name}</span> ({formatearTamano(archivo.size)})
          </p>
        )}

        <button
          type="button"
          disabled={!archivo || estado.paso === "validando"}
          onClick={revisar}
          className="mt-4 h-11 cursor-pointer rounded-full bg-violeta px-6 text-sm font-semibold text-white transition-colors hover:bg-violeta-hover disabled:cursor-not-allowed disabled:opacity-50"
        >
          {estado.paso === "validando" ? "Revisando…" : "Revisar sin aplicar"}
        </button>
      </section>

      {estado.paso === "error" && (
        <p role="alert" className="mt-4 rounded-2xl border border-oro/28 bg-oro/8 p-5 text-[13px] leading-[1.6] text-texto-suave">
          {estado.mensaje}
        </p>
      )}

      {estado.paso === "aplicada" && (
        <p className="mt-4 rounded-2xl border border-lila/25 bg-violeta/12 p-5 text-[13px] text-texto">
          La carga se aplicó.
        </p>
      )}

      {estado.paso === "revisar" && (
        <ResumenDeCarga
          resumen={estado.resumen}
          onConfirmar={(desactivarAusentes) => confirmar(estado.resumen.cargaId, desactivarAusentes)}
          onCancelar={() => cancelar(estado.resumen.cargaId)}
        />
      )}

      {estado.paso === "revisarFotos" && (
        <ResumenDeFotos
          resumen={estado.resumen}
          onConfirmar={() => confirmar(estado.resumen.cargaId, false)}
          onCancelar={() => cancelar(estado.resumen.cargaId)}
        />
      )}
    </>
  );
}

function mensajeDeError(error: unknown): string {
  return error instanceof Error ? error.message : "No se pudo completar la operación.";
}
