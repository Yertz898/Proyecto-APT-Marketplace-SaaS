"use client";

import { useEffect, useState, type FormEvent } from "react";

import { ErrorDeApi } from "@/lib/api/errores";
import {
  confirmarDosPasos,
  desactivarDosPasos,
  iniciarDosPasos,
  obtenerDosPasos,
  type EstadoDosPasos,
} from "@/lib/api/gestion";

import { Aviso, Boton, Campo, mensajeDe } from "./controles";
import { Tarjeta } from "./piezas";

/*
 * Verificación en dos pasos con Google Authenticator, en «Tu cuenta».
 *
 * Opcional, para el dueño de una tienda y la administración. Activarla es
 * escanear el QR y confirmar el primer código; desde ahí, entrar pide la
 * contraseña y el código. Los códigos de respaldo se muestran una sola vez.
 */

type Resultado = { tipo: "ok" | "error"; texto: string } | null;

function textoDeError(error: unknown, ...campos: string[]): string {
  if (error instanceof ErrorDeApi) {
    for (const campo of campos) {
      const texto = error.de(campo);
      if (texto) return texto;
    }
    return error.message;
  }
  return mensajeDe(error);
}

export function DosPasos() {
  const [estado, setEstado] = useState<EstadoDosPasos | null>(null);
  const [alta, setAlta] = useState<{ secreto: string; qr: string } | null>(null);
  const [respaldo, setRespaldo] = useState<string[] | null>(null);
  const [desactivando, setDesactivando] = useState(false);
  const [codigo, setCodigo] = useState("");
  const [password, setPassword] = useState("");
  const [ocupado, setOcupado] = useState(false);
  const [resultado, setResultado] = useState<Resultado>(null);

  useEffect(() => {
    obtenerDosPasos().then(setEstado, () => setEstado({ activa: false, codigosDeRespaldo: 0 }));
  }, []);

  async function empezar() {
    setOcupado(true);
    setResultado(null);
    try {
      setAlta(await iniciarDosPasos());
    } catch (error) {
      setResultado({ tipo: "error", texto: textoDeError(error, "general") });
    } finally {
      setOcupado(false);
    }
  }

  async function confirmar(evento: FormEvent) {
    evento.preventDefault();
    setOcupado(true);
    setResultado(null);
    try {
      const { codigosDeRespaldo } = await confirmarDosPasos(codigo);
      setRespaldo(codigosDeRespaldo);
      setAlta(null);
      setCodigo("");
      setEstado({ activa: true, codigosDeRespaldo: codigosDeRespaldo.length });
    } catch (error) {
      setResultado({ tipo: "error", texto: textoDeError(error, "codigo", "general") });
    } finally {
      setOcupado(false);
    }
  }

  async function desactivar(evento: FormEvent) {
    evento.preventDefault();
    setOcupado(true);
    setResultado(null);
    try {
      await desactivarDosPasos(password, codigo);
      setEstado({ activa: false, codigosDeRespaldo: 0 });
      setDesactivando(false);
      setPassword("");
      setCodigo("");
      setRespaldo(null);
      setResultado({ tipo: "ok", texto: "Desactivaste la verificación en dos pasos." });
    } catch (error) {
      setResultado({ tipo: "error", texto: textoDeError(error, "password", "codigo", "general") });
    } finally {
      setOcupado(false);
    }
  }

  if (!estado) return null;

  return (
    <Tarjeta className="mt-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="max-w-[560px]">
          <p className="text-[13px] font-semibold text-marino">Verificación en dos pasos</p>
          <p className="mt-1 text-[14px] leading-[1.55] text-pizarra">
            Además de la contraseña, al entrar te pedimos un código de Google Authenticator (u otra app de
            códigos). Así, aunque alguien sepa tu contraseña, no puede entrar sin tu teléfono.
          </p>
        </div>
        <span
          className={
            estado.activa
              ? "rounded-full border border-jade/30 bg-jade-claro px-2.5 py-0.5 text-[12px] font-semibold text-jade"
              : "rounded-full border border-arena bg-hueso px-2.5 py-0.5 text-[12px] font-semibold text-pizarra"
          }
        >
          {estado.activa ? "Activa" : "Inactiva"}
        </span>
      </div>

      {respaldo && (
        <div className="mt-4 rounded-xl border border-ambar bg-trigo p-4">
          <p className="text-[13px] font-semibold text-marino">Guarda tus códigos de respaldo</p>
          <p className="mt-1 text-[13px] text-pizarra">
            Sirven para entrar si pierdes el teléfono. Cada uno funciona una sola vez y no los volveremos a
            mostrar.
          </p>
          <ul className="mt-3 grid list-none grid-cols-2 gap-1.5 p-0 font-mono text-[14px] text-marino sm:grid-cols-4">
            {respaldo.map((c) => (
              <li key={c} className="rounded-md bg-white px-2 py-1 text-center">
                {c}
              </li>
            ))}
          </ul>
          <Boton
            variante="secundario"
            className="mt-3"
            onClick={() => navigator.clipboard?.writeText(respaldo.join("\n"))}
          >
            Copiar los códigos
          </Boton>
        </div>
      )}

      {!estado.activa && !alta && (
        <Boton className="mt-4" disabled={ocupado} onClick={empezar}>
          Activar con Google Authenticator
        </Boton>
      )}

      {alta && (
        <form onSubmit={confirmar} className="mt-4 grid gap-5 md:grid-cols-[200px_minmax(0,1fr)] md:items-start">
          {/* eslint-disable-next-line @next/next/no-img-element -- data URI generado en el momento */}
          <img
            src={alta.qr}
            alt="Código QR para Google Authenticator"
            className="w-[200px] rounded-lg border border-arena bg-white p-2"
          />
          <div className="flex flex-col gap-3">
            <ol className="list-decimal pl-5 text-[14px] leading-[1.6] text-marino">
              <li>Abre Google Authenticator y toca «+» y después «Escanear un código QR».</li>
              <li>Escanea el código de la izquierda.</li>
              <li>Escribe acá el código de 6 dígitos que aparece en la app.</li>
            </ol>
            <p className="text-[12.5px] text-pizarra">
              ¿No puedes escanear? Ingresa esta clave a mano:{" "}
              <span className="font-mono break-all text-marino">{alta.secreto}</span>
            </p>
            <Campo
              id="codigo-alta"
              etiqueta="Código de la app"
              inputMode="numeric"
              autoComplete="one-time-code"
              value={codigo}
              onChange={(e) => setCodigo(e.target.value)}
              maxLength={6}
            />
            <div className="flex flex-wrap gap-2.5">
              <Boton type="submit" disabled={ocupado || codigo.trim().length !== 6}>
                {ocupado ? "Comprobando…" : "Confirmar y activar"}
              </Boton>
              <Boton variante="secundario" onClick={() => setAlta(null)}>
                Cancelar
              </Boton>
            </div>
          </div>
        </form>
      )}

      {estado.activa && !desactivando && (
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <p className="text-[13px] text-pizarra">Te quedan {estado.codigosDeRespaldo} códigos de respaldo sin usar.</p>
          <Boton variante="secundario" onClick={() => setDesactivando(true)}>
            Desactivar
          </Boton>
        </div>
      )}

      {estado.activa && desactivando && (
        <form onSubmit={desactivar} className="mt-4 grid max-w-[520px] gap-3">
          <Campo
            id="clave-desactivar"
            etiqueta="Tu contraseña"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <Campo
            id="codigo-desactivar"
            etiqueta="Código de la app o de respaldo"
            autoComplete="one-time-code"
            value={codigo}
            onChange={(e) => setCodigo(e.target.value)}
          />
          <div className="flex flex-wrap gap-2.5">
            <Boton type="submit" variante="peligro" disabled={ocupado || !password || !codigo}>
              Desactivar la verificación
            </Boton>
            <Boton variante="secundario" onClick={() => setDesactivando(false)}>
              Cancelar
            </Boton>
          </div>
        </form>
      )}

      {resultado && <Aviso tipo={resultado.tipo}>{resultado.texto}</Aviso>}
    </Tarjeta>
  );
}
