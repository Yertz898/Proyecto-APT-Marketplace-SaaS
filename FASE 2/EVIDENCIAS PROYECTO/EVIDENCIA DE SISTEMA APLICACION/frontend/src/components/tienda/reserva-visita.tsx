"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";

import { Campo } from "@/components/campo";
import { useSesion } from "@/components/sesion/usar-sesion";
import { reservarVisita } from "@/lib/api/agenda";
import { ErrorDeApi } from "@/lib/api/errores";
import { formatearDiaLargo, formatearHora } from "@/lib/formato";
import type { HoraDisponible, Visita } from "@/lib/tipos";

/*
 * Panel de reserva de una visita.
 *
 * Pasa por cuatro estados: sin hora elegida, con hora pero sin sesión, con el
 * formulario listo, y la visita ya pedida.
 *
 * El nombre y el correo vienen de la sesión porque ya los dio al registrarse.
 * El teléfono no está en la cuenta, así que se pide.
 */
export function ReservaDeVisita({ slug, hora }: { slug: string; hora: HoraDisponible | null }) {
  const { sesion } = useSesion();

  return (
    <aside className="rounded-2xl border border-lila/16 p-5">
      <h2 className="text-[13px] font-semibold text-texto">Tu visita</h2>

      {!hora ? (
        <p className="mt-3 text-[13px] text-texto-suave">Elige una hora para continuar.</p>
      ) : (
        <>
          <DetalleDeLaHora hora={hora} />
          {sesion ? (
            <Formulario
              slug={slug}
              hora={hora}
              nombre={sesion.usuario.nombre}
              correo={sesion.usuario.email}
            />
          ) : (
            <EntrarPrimero slug={slug} />
          )}
        </>
      )}
    </aside>
  );
}

function DetalleDeLaHora({ hora }: { hora: HoraDisponible }) {
  return (
    <>
      <p className="mt-3 text-sm text-texto first-letter:uppercase">
        {formatearDiaLargo(hora.inicio)}
      </p>
      <p className="text-sm text-texto-suave">
        {formatearHora(hora.inicio)} a {formatearHora(hora.fin)}
      </p>

      {hora.nombreBloque && <p className="mt-2 text-[13px] text-lila">{hora.nombreBloque}</p>}

      <p className="mt-3 text-xs text-texto-suave">
        {hora.confirmacionAutomatica
          ? "Se confirma al instante."
          : "Queda pendiente hasta que la tienda la acepte."}
      </p>
    </>
  );
}

function EntrarPrimero({ slug }: { slug: string }) {
  const ruta = usePathname();

  return (
    <div className="mt-5">
      <Link
        href={`/t/${slug}/entrar?volver=${encodeURIComponent(ruta)}`}
        className="flex h-12 w-full items-center justify-center rounded-full bg-violeta text-sm font-semibold text-white transition-colors hover:bg-violeta-hover"
      >
        Iniciar sesión para reservar
      </Link>
      <p className="mt-3 text-xs leading-[1.5] text-texto-suave">
        La visita queda a tu nombre, así la tienda puede avisarte si algo cambia.
      </p>
    </div>
  );
}

function Formulario({
  slug,
  hora,
  nombre: nombreDeLaCuenta,
  correo: correoDeLaCuenta,
}: {
  slug: string;
  hora: HoraDisponible;
  nombre: string;
  correo: string;
}) {
  const router = useRouter();

  const [nombre, setNombre] = useState(nombreDeLaCuenta);
  const [correo, setCorreo] = useState(correoDeLaCuenta);
  // Solo los 8 dígitos: el +569 va fijo delante y se agrega al enviar.
  const [telefono, setTelefono] = useState("");
  const [motivo, setMotivo] = useState("");

  const [pedida, setPedida] = useState<Visita | null>(null);
  const [error, setError] = useState<ErrorDeApi | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function enviar(evento: React.FormEvent) {
    evento.preventDefault();
    setError(null);
    setEnviando(true);

    try {
      const visita = await reservarVisita(slug, {
        inicio: hora.inicio,
        nombreContacto: nombre,
        correoContacto: correo,
        telefonoContacto: `+569${telefono}`,
        motivo: motivo || undefined,
      });

      setPedida(visita);
      // La hora que acaba de tomar ya no está libre para el resto.
      router.refresh();
    } catch (falla) {
      setError(
        falla instanceof ErrorDeApi
          ? falla
          : new ErrorDeApi("error", "No pudimos pedir la hora. Vuelve a probar."),
      );
    } finally {
      setEnviando(false);
    }
  }

  if (pedida) {
    return <Confirmacion visita={pedida} />;
  }

  // El backend marca el problema en `inicio` cuando la hora se ocupó o dejó de
  // ofrecerse; eso no corresponde a ningún campo del formulario.
  const general = error?.de("inicio") ?? (error && !Object.keys(error.detalles).length ? error.message : null);

  return (
    <form onSubmit={enviar} className="mt-5 flex flex-col gap-4">
      {general && (
        <p role="alert" className="rounded-xl border border-oro/35 bg-oro/8 px-3.5 py-2.5 text-[13px] text-texto">
          {general}
        </p>
      )}

      <Campo
        id="nombre-contacto"
        etiqueta="Nombre"
        valor={nombre}
        // Un nombre no lleva números: lo que no sea letra, espacio, apóstrofo,
        // punto o guion no llega al campo.
        onCambio={(valor) => /^[\p{L} '.-]*$/u.test(valor) && setNombre(valor)}
        error={error?.de("nombreContacto")}
        autoComplete="name"
      />

      <Campo
        id="correo-contacto"
        etiqueta="Correo"
        tipo="email"
        valor={correo}
        onCambio={setCorreo}
        error={error?.de("correoContacto")}
        autoComplete="email"
      />

      <div>
        <label htmlFor="telefono-contacto" className="text-[13px] font-semibold text-texto">
          Teléfono
        </label>
        <div className="mt-2 flex h-12 items-center overflow-hidden rounded-xl border border-lila/20 bg-superficie focus-within:border-lila">
          <span className="flex h-full items-center border-r border-lila/20 px-3 text-sm font-semibold text-texto-suave">
            +569
          </span>
          <input
            id="telefono-contacto"
            type="tel"
            inputMode="numeric"
            autoComplete="tel-local"
            placeholder="12345678"
            maxLength={8}
            value={telefono}
            onChange={(evento) => {
              const digitos = evento.target.value.replace(/\D/g, "").slice(0, 8);
              setTelefono(digitos);
            }}
            aria-invalid={Boolean(error?.de("telefonoContacto"))}
            className="h-full flex-1 bg-transparent px-3 text-base tracking-[0.08em] text-texto outline-none"
          />
        </div>
        {error?.de("telefonoContacto") ? (
          <p className="mt-1.5 text-xs text-oro">{error.de("telefonoContacto")}</p>
        ) : (
          <p className="mt-1.5 text-xs text-texto-suave">Los 8 dígitos de tu celular.</p>
        )}
      </div>

      <div>
        <label htmlFor="motivo" className="text-[13px] font-semibold text-texto">
          Motivo <span className="font-normal text-texto-suave">(opcional)</span>
        </label>
        <textarea
          id="motivo"
          rows={3}
          value={motivo}
          onChange={(evento) => setMotivo(evento.target.value)}
          placeholder="Qué te gustaría ver"
          className="mt-2 w-full resize-none rounded-xl border border-lila/20 bg-superficie px-4 py-3 text-sm text-texto outline-none focus-visible:border-lila"
        />
      </div>

      <button
        type="submit"
        disabled={telefono.length !== 8 || enviando}
        className="h-12 cursor-pointer rounded-full bg-violeta text-sm font-semibold text-white transition-colors hover:bg-violeta-hover disabled:cursor-not-allowed disabled:opacity-50"
      >
        {enviando ? "Pidiendo la hora…" : "Pedir la hora"}
      </button>
    </form>
  );
}

function Confirmacion({ visita }: { visita: Visita }) {
  const confirmada = visita.estado === "confirmada";

  return (
    <div role="status" className="mt-5 rounded-xl border border-lila/30 bg-violeta/12 p-4">
      <p className="text-sm font-semibold text-texto">
        {confirmada ? "Visita confirmada" : "Solicitud enviada"}
      </p>
      <p className="mt-1.5 text-[13px] leading-[1.6] text-texto-suave">
        {confirmada
          ? "Te esperamos en la fecha y hora que elegiste."
          : "La tienda la revisará y te avisará al correo que dejaste."}
      </p>
      <p className="mt-3 text-xs text-texto-suave">
        Avisaremos a {visita.correoContacto}.
      </p>
    </div>
  );
}
