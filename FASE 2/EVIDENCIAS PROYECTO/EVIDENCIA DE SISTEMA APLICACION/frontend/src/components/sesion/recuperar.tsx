"use client";

import Link from "next/link";
import { useState } from "react";

import { Campo, type TemaDeFormulario } from "@/components/campo";
import { ErrorDeApi } from "@/lib/api/errores";
import { pedirEnlaceDeContrasena, restablecerContrasena } from "@/lib/api/sesion";

import { PIEL } from "./formulario";

/*
 * «¿Olvidaste tu contraseña?», en sus dos pasos.
 *
 * Primero se pide el enlace con el correo; después, desde el enlace del correo,
 * se elige la contraseña nueva. Sirven igual en una tienda (oscuro, y el
 * enlace vuelve a ella) y en el acceso de DealCommerce (claro).
 */

function general(error: ErrorDeApi | null): string | undefined {
  if (!error) return undefined;
  return Object.keys(error.detalles).length === 0 ? error.message : (error.de("general") ?? undefined);
}

/** Paso 1: el correo, para mandar el enlace. */
export function PedirEnlace({
  tema = "oscuro",
  tienda,
  hrefEntrar,
}: {
  tema?: TemaDeFormulario;
  /** Slug de la tienda desde la que se pide, para que el enlace vuelva a ella. */
  tienda?: string;
  hrefEntrar: string;
}) {
  const piel = PIEL[tema];
  const [email, setEmail] = useState("");
  const [error, setError] = useState<ErrorDeApi | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [listo, setListo] = useState<string | null>(null);

  async function enviar(evento: React.FormEvent) {
    evento.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      setListo(await pedirEnlaceDeContrasena(email.trim(), tienda));
    } catch (falla) {
      setError(falla instanceof ErrorDeApi ? falla : new ErrorDeApi("error", "No pudimos enviar el enlace."));
    } finally {
      setEnviando(false);
    }
  }

  if (listo) {
    return (
      <div className="flex flex-col gap-5">
        <h1 className={piel.titulo}>Revisa tu correo</h1>
        <p role="status" className={piel.aviso}>
          {listo} Si no llega en unos minutos, revisa la carpeta de spam.
        </p>
        <Link href={hrefEntrar} className={piel.enlace}>
          Volver a iniciar sesión
        </Link>
      </div>
    );
  }

  return (
    <form onSubmit={enviar} className="flex flex-col gap-5">
      <h1 className={piel.titulo}>¿Olvidaste tu contraseña?</h1>
      <p className={tema === "claro" ? "text-[14px] text-pizarra" : "text-[14px] text-texto-suave"}>
        Escribe el correo de tu cuenta y te enviamos un enlace para crear una contraseña nueva.
      </p>

      {general(error) && (
        <p role="alert" className={piel.aviso}>
          {general(error)}
        </p>
      )}

      <Campo
        tema={tema}
        id="email"
        etiqueta="Correo"
        tipo="email"
        valor={email}
        onCambio={setEmail}
        error={error?.de("email")}
        autoComplete="email"
      />

      <button type="submit" disabled={enviando || !email.trim()} className={piel.boton}>
        {enviando ? "Enviando…" : "Enviar enlace"}
      </button>

      <Link href={hrefEntrar} className={piel.enlace}>
        Volver a iniciar sesión
      </Link>
    </form>
  );
}

/** Paso 2: la contraseña nueva, con el uid y el token del enlace. */
export function ElegirContrasena({
  tema = "oscuro",
  uid,
  token,
  hrefEntrar,
  hrefPedirOtro,
}: {
  tema?: TemaDeFormulario;
  uid: string;
  token: string;
  hrefEntrar: string;
  hrefPedirOtro: string;
}) {
  const piel = PIEL[tema];
  const [password, setPassword] = useState("");
  const [repetida, setRepetida] = useState("");
  const [error, setError] = useState<ErrorDeApi | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [listo, setListo] = useState(false);

  const noCoinciden = repetida.length > 0 && repetida !== password;

  async function enviar(evento: React.FormEvent) {
    evento.preventDefault();
    if (password !== repetida) return;
    setError(null);
    setEnviando(true);
    try {
      await restablecerContrasena(uid, token, password);
      setListo(true);
    } catch (falla) {
      setError(falla instanceof ErrorDeApi ? falla : new ErrorDeApi("error", "No pudimos guardar la contraseña."));
    } finally {
      setEnviando(false);
    }
  }

  if (!uid || !token) {
    return (
      <div className="flex flex-col gap-5">
        <h1 className={piel.titulo}>Enlace incompleto</h1>
        <p className={piel.aviso}>Abre el enlace tal como llegó en el correo, o pide uno nuevo.</p>
        <Link href={hrefPedirOtro} className={piel.enlace}>
          Pedir un enlace nuevo
        </Link>
      </div>
    );
  }

  if (listo) {
    return (
      <div className="flex flex-col gap-5">
        <h1 className={piel.titulo}>Contraseña lista</h1>
        <p role="status" className={piel.aviso}>
          Ya puedes entrar con tu contraseña nueva.
        </p>
        <Link href={hrefEntrar} className={`flex items-center justify-center ${piel.boton} hover:no-underline`}>
          Iniciar sesión
        </Link>
      </div>
    );
  }

  const errorGeneral = general(error);

  return (
    <form onSubmit={enviar} className="flex flex-col gap-5">
      <h1 className={piel.titulo}>Crea tu contraseña nueva</h1>

      {errorGeneral && (
        <div role="alert" className={piel.aviso}>
          {errorGeneral}{" "}
          {error?.de("general") && (
            <Link href={hrefPedirOtro} className="font-semibold underline">
              Pedir otro enlace
            </Link>
          )}
        </div>
      )}

      <Campo
        tema={tema}
        id="password"
        etiqueta="Contraseña nueva"
        tipo="password"
        valor={password}
        onCambio={setPassword}
        error={error?.de("password")}
        ayuda="Al menos 8 caracteres, que no sean solo números."
        autoComplete="new-password"
      />
      <Campo
        tema={tema}
        id="repetida"
        etiqueta="Repite la contraseña"
        tipo="password"
        valor={repetida}
        onCambio={setRepetida}
        error={noCoinciden ? "Las dos contraseñas no coinciden." : undefined}
        autoComplete="new-password"
      />

      <button type="submit" disabled={enviando || !password || password !== repetida} className={piel.boton}>
        {enviando ? "Guardando…" : "Guardar contraseña"}
      </button>
    </form>
  );
}
