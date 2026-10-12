"use client";

import Link from "next/link";
import { useState } from "react";

import { ErrorDeApi } from "@/lib/api/errores";
import { pedirAcceso } from "@/lib/api/solicitudes";

import { Campo } from "./campo";
import { TIENDA_DE_EJEMPLO } from "./enlaces";

/*
 * Formulario para pedir acceso a la plataforma.
 *
 * Esta pantalla no estaba en el canvas: el diseño llega hasta el botón. Se armó
 * con los mismos colores, tipografías y medidas del resto de la portada.
 *
 * Se piden cuatro datos y nada más. Cada campo de un formulario de contacto es
 * gente que no lo termina, y para escribirle a alguien basta con saber quién es
 * y dónde ubicarlo; el resto se pregunta en esa conversación.
 */
export function FormularioDeAcceso() {
  const [negocio, setNegocio] = useState("");
  const [nombre, setNombre] = useState("");
  const [email, setEmail] = useState("");
  const [telefono, setTelefono] = useState("");
  const [mensaje, setMensaje] = useState("");

  const [enviada, setEnviada] = useState(false);
  const [error, setError] = useState<ErrorDeApi | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function enviar(evento: React.FormEvent) {
    evento.preventDefault();
    setError(null);
    setEnviando(true);

    try {
      await pedirAcceso({ negocio, nombre, email, telefono, mensaje: mensaje || undefined });
      setEnviada(true);
    } catch (falla) {
      setError(
        falla instanceof ErrorDeApi
          ? falla
          : new ErrorDeApi("error", "No pudimos enviar tu solicitud. Vuelve a probar."),
      );
    } finally {
      setEnviando(false);
    }
  }

  if (enviada) {
    return <Recibida nombre={nombre} />;
  }

  // Un error sin campo asociado se muestra arriba: sin conexión, o demasiados
  // envíos seguidos desde la misma red.
  const general = error && Object.keys(error.detalles).length === 0 ? error.message : null;

  return (
    <form onSubmit={enviar} className="flex flex-col gap-5">
      {general && (
        <p role="alert" className="rounded-[12px] border border-ambar bg-trigo px-4 py-3 text-[15px] text-marino">
          {general}
        </p>
      )}

      <Campo
        id="negocio"
        etiqueta="Nombre del negocio"
        valor={negocio}
        onCambio={setNegocio}
        error={error?.de("negocio")}
        autoComplete="organization"
      />

      <Campo
        id="nombre"
        etiqueta="Tu nombre"
        valor={nombre}
        onCambio={setNombre}
        error={error?.de("nombre")}
        autoComplete="name"
      />

      <Campo
        id="email"
        etiqueta="Correo"
        tipo="email"
        valor={email}
        onCambio={setEmail}
        error={error?.de("email")}
        autoComplete="email"
      />

      <Campo
        id="telefono"
        etiqueta="Teléfono o WhatsApp"
        tipo="tel"
        valor={telefono}
        onCambio={setTelefono}
        error={error?.de("telefono")}
        ayuda="Es por donde te vamos a contactar."
        autoComplete="tel"
      />

      <Campo
        id="mensaje"
        etiqueta="¿Qué vendes?"
        valor={mensaje}
        onCambio={setMensaje}
        error={error?.de("mensaje")}
        requerido={false}
        multilinea
        placeholder="Abarrotes, cosmética, insumos… y cómo vendes hoy."
      />

      <button
        type="submit"
        disabled={enviando}
        className="h-[52px] cursor-pointer rounded-[12px] bg-acero text-base font-semibold text-white transition-colors hover:bg-acero-hondo disabled:cursor-not-allowed disabled:opacity-50"
      >
        {enviando ? "Enviando…" : "Enviar solicitud"}
      </button>

      <p className="text-[13px] leading-[1.5] text-pizarra">
        Te escribimos para conocer tu negocio y ayudarte con la primera carga del catálogo. No compartimos tus
        datos con nadie.
      </p>
    </form>
  );
}

function Recibida({ nombre }: { nombre: string }) {
  return (
    <div role="status" className="flex flex-col items-start gap-4 rounded-[16px] border border-arena bg-white p-8">
      <span className="flex size-12 items-center justify-center rounded-full bg-jade-claro">
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="#1E7F53"
          strokeWidth="2.2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M4 12.5l5 5L20 6.5" />
        </svg>
      </span>

      <h2 className="font-jakarta text-[26px] leading-[1.15] font-extrabold">
        Recibimos tu solicitud{nombre ? `, ${nombre.split(" ")[0]}` : ""}
      </h2>

      <p className="text-base leading-[1.55] text-pizarra text-pretty">
        Te vamos a escribir para conocer tu negocio y acompañarte en la primera carga de tu catálogo.
      </p>

      <Link
        href={TIENDA_DE_EJEMPLO}
        className="mt-2 inline-flex h-12 items-center gap-2 rounded-[12px] border border-niebla bg-white px-6 text-[15px] font-semibold text-acero no-underline hover:border-acero hover:no-underline"
      >
        Mientras tanto, mira una tienda de ejemplo <span aria-hidden="true">→</span>
      </Link>
    </div>
  );
}
