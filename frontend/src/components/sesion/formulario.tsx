"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Campo, type TemaDeFormulario } from "@/components/campo";
import { ErrorDeApi } from "@/lib/api/errores";
import { iniciarSesion, registrarComprador } from "@/lib/api/sesion";
import type { Sesion } from "@/lib/sesion";

/*
 * Formulario de inicio de sesión y de creación de cuenta.
 *
 * Es el mismo componente para los dos casos porque son el mismo formulario con
 * dos campos de diferencia, y porque los errores, el envío y el destino después
 * de entrar se resuelven igual.
 *
 * La validación de verdad la hace el backend y sus mensajes ya vienen en
 * español: acá no se reescribe ningún texto de error, solo se ubica junto al
 * campo que corresponde.
 */

export type ModoDeSesion = "entrar" | "crear-cuenta";

/*
 * Los dos accesos usan este mismo formulario con distinta piel: el de
 * DealCommerce lleva la marca de la plataforma y el de cada tienda, la de esa
 * tienda. Lo que cambia son los colores y la tipografía, no el formulario.
 */
const PIEL = {
  claro: {
    titulo: "font-jakarta text-[32px] font-extrabold tracking-[-0.03em] text-marino",
    aviso: "rounded-[12px] border border-ambar bg-trigo px-4 py-3 text-[13px] text-marino",
    boton:
      "h-12 cursor-pointer rounded-[12px] bg-acero text-sm font-semibold text-white transition-colors hover:bg-acero-hondo disabled:cursor-not-allowed disabled:opacity-50",
    enlace: "text-center text-[13px] text-acero hover:underline",
  },
  oscuro: {
    titulo: "font-serif text-[32px] font-medium text-texto",
    aviso: "rounded-xl border border-oro/35 bg-oro/8 px-4 py-3 text-[13px] text-texto",
    boton:
      "h-12 cursor-pointer rounded-full bg-violeta text-sm font-semibold text-white transition-colors hover:bg-violeta-hover disabled:cursor-not-allowed disabled:opacity-50",
    enlace: "text-center text-[13px] text-lila hover:underline",
  },
} as const;

const TITULOS: Record<ModoDeSesion, { titulo: string; boton: string; enviando: string }> = {
  entrar: { titulo: "Iniciar sesión", boton: "Entrar", enviando: "Entrando…" },
  "crear-cuenta": { titulo: "Crear cuenta", boton: "Crear cuenta", enviando: "Creando…" },
};

export function FormularioDeSesion({
  modo,
  destino,
  hrefAlternativa,
  textoAlternativa,
  tema = "oscuro",
}: {
  modo: ModoDeSesion;
  /**
   * A dónde ir cuando la sesión queda iniciada.
   *
   * Puede ser una función del rol: en el acceso de DealCommerce no es lo mismo
   * entrar como administrador de la plataforma que como dueño de una tienda.
   */
  destino: string | ((sesion: Sesion) => string);
  /** Enlace al otro formulario; null cuando no corresponde ofrecerlo. */
  hrefAlternativa: string | null;
  textoAlternativa?: string;
  /** Claro para DealCommerce, oscuro para la vitrina de la tienda. */
  tema?: TemaDeFormulario;
}) {
  const router = useRouter();
  const textos = TITULOS[modo];
  const piel = PIEL[tema];
  const creando = modo === "crear-cuenta";

  const [nombre, setNombre] = useState("");
  const [email, setEmail] = useState("");
  const [rut, setRut] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState<ErrorDeApi | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function enviar(evento: React.FormEvent) {
    evento.preventDefault();
    setError(null);
    setEnviando(true);

    try {
      const sesion = creando
        ? await registrarComprador({ nombre, email, password, rut: rut || undefined })
        : await iniciarSesion(email, password);

      // `replace` y no `push`: volver atrás no debería llevar al formulario de
      // una sesión que ya está iniciada.
      router.replace(typeof destino === "function" ? destino(sesion) : destino);
      router.refresh();
    } catch (falla) {
      setError(falla instanceof ErrorDeApi ? falla : new ErrorDeApi("error", "No pudimos completar la operación."));
      setEnviando(false);
    }
  }

  // Los errores que no son de un campo se muestran arriba: credenciales que no
  // coinciden, demasiados intentos, sin conexión.
  const general = error && Object.keys(error.detalles).length === 0 ? error.message : error?.de("general");

  return (
    <form onSubmit={enviar} noValidate={false} className="flex flex-col gap-5">
      <h1 className={piel.titulo}>{textos.titulo}</h1>

      {general && (
        <p role="alert" className={piel.aviso}>
          {general}
        </p>
      )}

      {creando && (
        <Campo
          tema={tema}
          id="nombre"
          etiqueta="Nombre"
          valor={nombre}
          onCambio={setNombre}
          error={error?.de("nombre")}
          autoComplete="name"
        />
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

      {creando && (
        <Campo
          tema={tema}
          id="rut"
          etiqueta="RUT"
          valor={rut}
          onCambio={setRut}
          error={error?.de("rut")}
          ayuda="Sirve para la boleta y el despacho. Con guion y sin puntos: 12345678-5."
          requerido={false}
        />
      )}

      <Campo
        tema={tema}
        id="password"
        etiqueta="Contraseña"
        tipo="password"
        valor={password}
        onCambio={setPassword}
        error={error?.de("password")}
        autoComplete={creando ? "new-password" : "current-password"}
      />

      <button
        type="submit"
        disabled={enviando}
        className={piel.boton}
      >
        {enviando ? textos.enviando : textos.boton}
      </button>

      {hrefAlternativa && (
        <Link href={hrefAlternativa} className={piel.enlace}>
          {textoAlternativa}
        </Link>
      )}
    </form>
  );
}
