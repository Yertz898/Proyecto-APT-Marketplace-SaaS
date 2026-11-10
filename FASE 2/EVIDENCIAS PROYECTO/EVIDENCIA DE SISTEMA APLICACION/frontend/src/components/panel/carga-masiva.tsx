"use client";

import { useEffect, useState } from "react";

import {
  cancelarCarga,
  confirmarCarga,
  descargarPlantilla,
  obtenerLimitesDeCarga,
  validarCarga,
  validarFotos,
} from "@/lib/api/panel";
import { formatearTamano, revisarArchivo, TIPOS_DE_CARGA } from "@/lib/cargas";
import type { LimitesCarga, ResumenCarga, ResumenFotos, TipoCarga } from "@/lib/tipos-panel";

import { Cabecera } from "./piezas";
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

export function CargaMasiva({ tipo }: { tipo: TipoCarga }) {
  const configuracion = TIPOS_DE_CARGA[tipo];

  // Los límites los dice el backend, y se piden acá y no en servidor porque
  // van con la sesión. Mientras no lleguen, la pantalla usa lo que sabe y
  // omite el aviso de tamaño en vez de inventar un número.
  const [limites, setLimites] = useState<LimitesCarga | null>(null);
  const extensiones = configuracion.extensiones;

  const [archivo, setArchivo] = useState<File | null>(null);
  const [rechazo, setRechazo] = useState<string | null>(null);
  const [estado, setEstado] = useState<Estado>({ paso: "elegir" });

  useEffect(() => {
    obtenerLimitesDeCarga().then(setLimites);
  }, []);

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
      <div className="mt-3">
        <Cabecera titulo={configuracion.titulo} descripcion={configuracion.descripcion} />
      </div>

      {configuracion.columnas.length > 0 && (
        <section className="rounded-[14px] border border-arena bg-white p-5">
          <h2 className="text-[13px] font-semibold text-marino">1. Descargar la plantilla</h2>
          <p className="mt-2 text-[13px] text-pizarra">
            Trae los encabezados exactos y una fila de ejemplo. Usa siempre esta plantilla: así ninguna tienda
            tiene que adivinar los nombres de las columnas.
          </p>
          <p className="mt-3 flex flex-wrap gap-2">
            {configuracion.columnas.map((columna) => (
              <code key={columna} className="rounded-md border border-arena-honda bg-hueso px-2 py-1 text-xs text-pizarra">
                {columna}
              </code>
            ))}
          </p>
          {/*
            * Un enlace no sirve: la plantilla se pide con la sesión puesta, y
            * un <a> no lleva el token. Se descarga desde el cliente.
            */}
          <button
            type="button"
            onClick={() => void descargarPlantilla(tipo)}
            className="mt-4 inline-flex h-11 cursor-pointer items-center rounded-[12px] border border-niebla px-5 text-[13px] font-semibold text-acero transition-colors hover:bg-cielo"
          >
            Descargar plantilla
          </button>
        </section>
      )}

      <section className="mt-4 rounded-[14px] border border-arena bg-white p-5">
        <h2 className="text-[13px] font-semibold text-marino">
          {configuracion.columnas.length > 0 ? "2. Subir el archivo" : "1. Subir el archivo"}
        </h2>

        <p className="mt-2 text-[13px] text-pizarra">
          Se acepta {extensiones.join(" o ")}
          {limites ? `, hasta ${formatearTamano(limites.tamanoMaximoBytes)}.` : "."}
          {tipo !== "fotos" && " Recomendamos .xlsx: conserva los tipos de dato y evita problemas de separadores."}
        </p>

        <input
          type="file"
          accept={extensiones.join(",")}
          aria-label="Archivo a cargar"
          onChange={(evento) => elegirArchivo(evento.target.files?.[0] ?? null)}
          className="mt-4 block w-full cursor-pointer rounded-[12px] border border-dashed border-arena-honda bg-hueso p-4 text-[13px] text-pizarra file:mr-4 file:cursor-pointer file:rounded-[10px] file:border-0 file:bg-acero file:px-4 file:py-2 file:text-[13px] file:font-semibold file:text-white"
        />

        {rechazo && (
          <p role="alert" className="mt-3 rounded-[12px] border border-ambar bg-trigo p-3.5 text-[13px] text-marino">
            {rechazo}
          </p>
        )}

        {archivo && (
          <p className="mt-3 text-[13px] text-pizarra">
            Elegido: <span className="font-semibold text-marino">{archivo.name}</span> ({formatearTamano(archivo.size)})
          </p>
        )}

        <button
          type="button"
          disabled={!archivo || estado.paso === "validando"}
          onClick={revisar}
          className="mt-4 h-11 cursor-pointer rounded-[12px] bg-acero px-6 text-sm font-semibold text-white transition-colors hover:bg-acero-hondo disabled:cursor-not-allowed disabled:opacity-50"
        >
          {estado.paso === "validando" ? "Revisando…" : "Revisar sin aplicar"}
        </button>
      </section>

      {estado.paso === "error" && (
        <p role="alert" className="mt-4 rounded-[14px] border border-ambar bg-trigo p-5 text-[13px] leading-[1.6] text-marino">
          {estado.mensaje}
        </p>
      )}

      {estado.paso === "aplicada" && (
        <p className="mt-4 rounded-[14px] border border-niebla bg-cielo p-5 text-[13px] font-semibold text-acero">
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
