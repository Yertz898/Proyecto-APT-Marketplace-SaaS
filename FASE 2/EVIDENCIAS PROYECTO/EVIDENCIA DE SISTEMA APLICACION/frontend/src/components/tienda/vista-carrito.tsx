"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { useSesion } from "@/components/sesion/usar-sesion";
import { confirmarPedido, cotizarCarrito } from "@/lib/api/carrito";
import { ErrorDeApi } from "@/lib/api/errores";
import { formatearPesos } from "@/lib/formato";
import { formatearRut, rutValido } from "@/lib/rut";
import type {
  CarritoCotizado,
  DatosDeContacto,
  LineaCarrito,
  PedidoConfirmado,
} from "@/lib/tipos";

import { useCarrito } from "./carrito";
import { EnlaceExterno } from "./enlace-externo";



const CORREO = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * Manda al navegador a Webpay.
 *
 * Transbank pide llegar con un POST de formulario que lleve el token: un
 * enlace (GET) no sirve. Se arma el formulario, se envía y la página se va.
 */
function irAWebpay(url: string, token: string) {
  const formulario = document.createElement("form");
  formulario.method = "POST";
  formulario.action = url;
  const campo = document.createElement("input");
  campo.type = "hidden";
  campo.name = "token_ws";
  campo.value = token;
  formulario.appendChild(campo);
  document.body.appendChild(formulario);
  formulario.submit();
}

export function VistaCarrito({ slugTienda, aceptaWebpay = false }: { slugTienda: string; aceptaWebpay?: boolean }) {
  const { lineas, quitar, vaciar } = useCarrito();
  // Con Webpay se paga en línea; con WhatsApp se coordina como siempre.
  const [metodo, setMetodo] = useState<"whatsapp" | "webpay">(aceptaWebpay ? "webpay" : "whatsapp");
  const { sesion, hidratado } = useSesion();
  // Se compra con cuenta o como visitante: la tienda tiene que saber quién
  // pidió. Con sesión se usa la cuenta; sin ella, la persona elige.
  const [comoVisitante, setComoVisitante] = useState(false);
  const conCuenta = Boolean(sesion);
  const volver = encodeURIComponent(`/t/${slugTienda}/carrito`);
  const [cotizacion, setCotizacion] = useState<CarritoCotizado | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pedido, setPedido] = useState<PedidoConfirmado | null>(null);
  const [confirmando, setConfirmando] = useState(false);

  // El pago se coordina fuera de la plataforma, así que sin nombre ni
  // teléfono el pedido no sirve para nada: la tienda no tendría a quién
  // escribirle. Por eso el botón no se habilita hasta que están los dos.
  const [contacto, setContacto] = useState<DatosDeContacto>({
    nombre_contacto: "",
    telefono_contacto: "",
    email_contacto: "",
    rut_contacto: "",
    direccion_entrega: "",
    notas: "",
  });

  // Con cuenta, el nombre y el correo salen de ella si la persona no los
  // cambió: no tiene sentido pedirle lo que ya sabemos.
  const nombre = contacto.nombre_contacto || (conCuenta ? (sesion?.usuario.nombre ?? "") : "");
  const correo = contacto.email_contacto || (conCuenta ? (sesion?.usuario.email ?? "") : "");
  const rut = contacto.rut_contacto ?? "";

  const rutMalo = !conCuenta && rut.trim() !== "" && !rutValido(rut);
  const correoMalo = !conCuenta && correo.trim() !== "" && !CORREO.test(correo.trim());

  const faltanDatos =
    nombre.trim() === "" ||
    contacto.telefono_contacto.trim() === "" ||
    (!conCuenta && (!rutValido(rut) || !CORREO.test(correo.trim())));
  const eligiendo = hidratado && !conCuenta && !comoVisitante;

  function escribir(campo: keyof DatosDeContacto, valor: string) {
    setContacto((previo) => ({ ...previo, [campo]: valor }));
  }

  useEffect(() => {
    if (lineas.length === 0) {
      return;
    }

    let vigente = true;

    cotizarCarrito(slugTienda, lineas)
      .then((resultado) => {
        if (!vigente) return;
        setCotizacion(resultado);
        setError(null);
      })
      .catch((problema: unknown) => {
        if (!vigente) return;
        setCotizacion(null);
        setError(problema instanceof Error ? problema.message : "No se pudo cotizar el carrito.");
      });

    return () => {
      vigente = false;
    };
  }, [lineas, slugTienda]);

  async function confirmar() {
    setConfirmando(true);
    try {
      const confirmado = await confirmarPedido(slugTienda, lineas, {
        ...contacto,
        nombre_contacto: nombre.trim(),
        email_contacto: correo.trim(),
        rut_contacto: conCuenta ? "" : rut,
        metodo,
      });
      if (confirmado.webpay) {
        // El carrito se vacía recién cuando el pago vuelve aprobado: si el
        // cliente anula en Webpay, vuelve con sus productos.
        irAWebpay(confirmado.webpay.url, confirmado.webpay.token);
        return;
      }
      setPedido(confirmado);
      setError(null);
      vaciar();
    } catch (problema) {
      const detalle = problema instanceof ErrorDeApi ? Object.values(problema.detalles)[0]?.[0] : null;
      setError(detalle ?? (problema instanceof Error ? problema.message : "No se pudo confirmar el pedido."));
    } finally {
      setConfirmando(false);
    }
  }

  if (pedido) {
    return (
      <div className="rounded-2xl border border-lila/16 p-6">
        <h2 className="font-serif text-[26px] text-texto">Pedido {pedido.numero}</h2>
        <p className="mt-2 text-sm leading-[1.6] text-texto-suave">{pedido.mensaje}</p>
        {pedido.enlaceWhatsapp && (
          <EnlaceExterno
            enlace={pedido.enlaceWhatsapp}
            className="mt-5 flex h-12 w-full max-w-xs items-center justify-center rounded-full bg-violeta text-sm font-semibold text-white"
          >
            Coordinar el pago por WhatsApp
          </EnlaceExterno>
        )}
      </div>
    );
  }

  if (lineas.length === 0) {
    return (
      <div className="rounded-2xl border border-lila/12 bg-superficie p-6">
        <p className="text-sm text-texto-suave">Tu carrito está vacío.</p>
        <div className="mt-4">
          <Link href={`/t/${slugTienda}/productos`} className="text-[13px] text-lila">
            Ver el catálogo
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_340px] lg:items-start">
      <ul className="flex flex-col gap-3">
        {lineas.map((linea, indice) => (
          <li
            key={linea.codigo}
            className="flex items-start justify-between gap-4 rounded-xl border border-lila/12 bg-superficie p-4"
          >
            <div>
              <p className="text-sm text-texto">{nombreDeLinea(cotizacion, indice, linea)}</p>
              <p className="mt-1 text-xs text-texto-suave">{detalleDeLinea(cotizacion, indice, linea)}</p>
              {cotizacion?.lineas[indice]?.rechazo && (
                <p role="alert" className="mt-2 text-xs text-oro">
                  {cotizacion.lineas[indice].rechazo}
                </p>
              )}
            </div>

            <div className="flex flex-none flex-col items-end gap-2">
              {cotizacion?.lineas[indice] && (
                <span className="text-sm text-texto">{formatearPesos(cotizacion.lineas[indice].neto)}</span>
              )}
              <button
                type="button"
                onClick={() => quitar(indice)}
                className="cursor-pointer text-xs text-texto-suave transition-colors hover:text-texto"
              >
                Quitar
              </button>
            </div>
          </li>
        ))}
      </ul>

      <aside className="flex flex-col gap-5">
        {eligiendo ? (
          <section className="rounded-2xl border border-lila/16 p-5">
            <h2 className="text-[13px] font-semibold text-texto">¿Cómo quieres comprar?</h2>
            <p className="mt-1.5 text-xs leading-[1.5] text-texto-suave">
              Con una cuenta ves tus pedidos y no repites tus datos la próxima vez.
            </p>
            <div className="mt-4 flex flex-col gap-2.5">
              <Link
                href={`/t/${slugTienda}/entrar?volver=${volver}`}
                className="flex h-11 items-center justify-center rounded-full bg-violeta text-sm font-semibold text-white hover:bg-violeta-hover hover:no-underline"
              >
                Iniciar sesión
              </Link>
              <Link
                href={`/t/${slugTienda}/crear-cuenta?volver=${volver}`}
                className="flex h-11 items-center justify-center rounded-full border border-lila/40 text-sm font-semibold text-texto hover:bg-violeta/15 hover:no-underline"
              >
                Crear una cuenta
              </Link>
              <button
                type="button"
                onClick={() => setComoVisitante(true)}
                className="h-11 cursor-pointer rounded-full text-sm font-semibold text-lila hover:underline"
              >
                Comprar como visitante
              </button>
            </div>
          </section>
        ) : (
        <section className="rounded-2xl border border-lila/16 p-5">
          <h2 className="text-[13px] font-semibold text-texto">
            {conCuenta ? `Comprando como ${sesion?.usuario.nombre}` : "Tus datos (visitante)"}
          </h2>
          <p className="mt-1.5 text-xs leading-[1.5] text-texto-suave">
            Para coordinar la entrega{aceptaWebpay ? "" : " y el pago. No se cobra en línea"}.
          </p>

          <div className="mt-4 flex flex-col gap-3">
            {!conCuenta && (
              <Campo
                id="rut-contacto"
                etiqueta="RUT"
                valor={rut}
                // Se le van poniendo los puntos y el guion mientras se escribe.
                onCambio={(valor) => escribir("rut_contacto", formatearRut(valor))}
                error={rutMalo ? "Revisa el RUT: el dígito verificador no calza." : null}
              />
            )}
            <Campo
              id="nombre-contacto"
              etiqueta="Nombre"
              valor={nombre}
              onCambio={(valor) => escribir("nombre_contacto", valor)}
              autoComplete="name"
            />
            {!conCuenta && (
              <Campo
                id="correo-contacto"
                etiqueta="Correo electrónico"
                valor={correo}
                onCambio={(valor) => escribir("email_contacto", valor)}
                autoComplete="email"
                error={correoMalo ? "Revisa el correo." : null}
              />
            )}
            <Campo
              id="telefono-contacto"
              etiqueta="WhatsApp"
              valor={contacto.telefono_contacto}
              onCambio={(valor) => escribir("telefono_contacto", valor)}
              autoComplete="tel"
              inputMode="tel"
            />
            <Campo
              id="direccion-entrega"
              etiqueta="Dirección (opcional)"
              valor={contacto.direccion_entrega ?? ""}
              onCambio={(valor) => escribir("direccion_entrega", valor)}
              autoComplete="street-address"
            />
            <Campo
              id="notas-pedido"
              etiqueta="Notas (opcional)"
              valor={contacto.notas ?? ""}
              onCambio={(valor) => escribir("notas", valor)}
            />
          </div>
          {!conCuenta && (
            <button
              type="button"
              onClick={() => setComoVisitante(false)}
              className="mt-3 cursor-pointer text-xs text-lila hover:underline"
            >
              Prefiero iniciar sesión
            </button>
          )}
        </section>
        )}

        <section className="rounded-2xl border border-lila/16 p-5">
        <h2 className="text-[13px] font-semibold text-texto">Resumen</h2>

        {cotizacion ? (
          <dl className="mt-4 flex flex-col gap-1.5 text-[13px]">
            <Fila termino="Neto" valor={formatearPesos(cotizacion.neto)} />
            <Fila termino="IVA" valor={formatearPesos(cotizacion.iva)} />
            <Fila termino="Total" valor={formatearPesos(cotizacion.total)} destacado />
          </dl>
        ) : (
          <p className="mt-4 text-[13px] leading-[1.6] text-texto-suave">
            {error ?? "Calculando el total…"}
          </p>
        )}

        {cotizacion?.avisoTramo && (
          <p className="mt-4 rounded-lg border border-oro/28 bg-oro/8 p-3 text-xs leading-[1.5] text-texto-suave">
            {cotizacion.avisoTramo}
          </p>
        )}

        {cotizacion?.rechazo && (
          <p role="alert" className="mt-4 text-xs text-texto-suave">
            {cotizacion.rechazo}
          </p>
        )}

        {aceptaWebpay && (
          <fieldset className="mt-5 flex flex-col gap-2">
            <legend className="mb-1 text-[13px] font-semibold text-texto">¿Cómo quieres pagar?</legend>
            {(
              [
                ["webpay", "Pagar ahora con Webpay", "Tarjeta de débito, crédito o prepago."],
                ["whatsapp", "Coordinar por WhatsApp", "Transferencia o el medio que acuerdes con la tienda."],
              ] as const
            ).map(([valor, titulo, detalle]) => (
              <label
                key={valor}
                className={`flex cursor-pointer items-start gap-3 rounded-xl border p-3 transition-colors ${
                  metodo === valor ? "border-violeta bg-violeta/12" : "border-lila/16 hover:border-lila/40"
                }`}
              >
                <input
                  type="radio"
                  name="metodo-de-pago"
                  value={valor}
                  checked={metodo === valor}
                  onChange={() => setMetodo(valor)}
                  className="mt-0.5 accent-violeta"
                />
                <span>
                  <span className="block text-[13px] font-semibold text-texto">{titulo}</span>
                  <span className="block text-xs text-texto-suave">{detalle}</span>
                </span>
              </label>
            ))}
          </fieldset>
        )}

        <button
          type="button"
          disabled={
            confirmando || eligiendo || faltanDatos || cotizacion === null || cotizacion.rechazo !== null
          }
          onClick={confirmar}
          className="mt-5 h-12 w-full cursor-pointer rounded-full bg-violeta text-sm font-semibold text-white transition-colors hover:bg-violeta-hover disabled:cursor-not-allowed disabled:opacity-50"
        >
          {confirmando
            ? metodo === "webpay"
              ? "Abriendo Webpay…"
              : "Confirmando…"
            : metodo === "webpay"
              ? "Ir a pagar con Webpay"
              : "Confirmar pedido"}
        </button>

        <p className="mt-3 text-center text-xs text-texto-suave">
          {eligiendo
            ? "Elige cómo quieres comprar para seguir."
            : faltanDatos
            ? conCuenta
              ? "Completa tu nombre y tu WhatsApp para confirmar."
              : "Completa tu RUT, nombre, correo y WhatsApp para confirmar."
            : metodo === "webpay"
              ? "Pagas en el sitio seguro de Transbank. Ambiente de pruebas: no se cobra dinero real."
              : "No se cobra en línea: el pago se coordina al confirmar."}
        </p>
        </section>
      </aside>
    </div>
  );
}

function nombreDeLinea(cotizacion: CarritoCotizado | null, indice: number, linea: LineaCarrito): string {
  return cotizacion?.lineas[indice]?.nombre ?? linea.codigo;
}

function detalleDeLinea(cotizacion: CarritoCotizado | null, indice: number, linea: LineaCarrito): string {
  return cotizacion?.lineas[indice]?.detalle ?? String(linea.cantidad);
}

function Campo({
  id,
  etiqueta,
  valor,
  onCambio,
  autoComplete,
  inputMode,
  error,
}: {
  id: string;
  etiqueta: string;
  valor: string;
  onCambio: (valor: string) => void;
  autoComplete?: string;
  inputMode?: "tel" | "text";
  error?: string | null;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="text-xs text-texto-suave">
        {etiqueta}
      </label>
      <input
        id={id}
        type="text"
        value={valor}
        autoComplete={autoComplete}
        inputMode={inputMode}
        onChange={(evento) => onCambio(evento.target.value)}
        aria-invalid={Boolean(error)}
        className="h-11 rounded-xl border border-lila/20 bg-transparent px-3 text-sm text-texto outline-none transition-colors focus-visible:border-lila"
      />
      {error && <p className="text-xs text-oro">{error}</p>}
    </div>
  );
}

function Fila({ termino, valor, destacado = false }: { termino: string; valor: string; destacado?: boolean }) {
  return (
    <div className="flex justify-between">
      <dt className="text-texto-suave">{termino}</dt>
      <dd className={destacado ? "font-semibold text-texto" : "text-texto"}>{valor}</dd>
    </div>
  );
}