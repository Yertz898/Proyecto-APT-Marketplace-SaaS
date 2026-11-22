"use client";

import Link from "next/link";
import { useEffect } from "react";

import { useCarrito } from "./carrito";
import { EnlaceExterno } from "./enlace-externo";

/*
 * El resultado de un pago con Webpay, con los colores de la tienda.
 *
 * Si el pago se aprobó, recién acá se vacía el carrito: si el cliente anuló en
 * Webpay, vuelve con sus productos para intentarlo de nuevo o coordinar por
 * WhatsApp.
 */

const MENSAJES: Record<string, { titulo: string; texto: string; aprobado: boolean }> = {
  autorizado: {
    titulo: "¡Pago aprobado!",
    texto: "Tu pedido quedó confirmado. La tienda ya lo ve en su panel y te contactará para la entrega.",
    aprobado: true,
  },
  rechazado: {
    titulo: "El pago no se aprobó",
    texto: "Tu banco o Transbank rechazó el pago, así que el pedido se anuló y no se cobró nada.",
    aprobado: false,
  },
  abortado: {
    titulo: "Anulaste el pago",
    texto: "No se cobró nada y el pedido se anuló. Tus productos siguen en el carrito.",
    aprobado: false,
  },
  vencido: {
    titulo: "Se acabó el tiempo para pagar",
    texto: "No se cobró nada y el pedido se anuló. Tus productos siguen en el carrito.",
    aprobado: false,
  },
};

export function ResultadoDelPago({
  slug,
  folio,
  estado,
  whatsapp,
}: {
  slug: string;
  folio: string;
  estado: string;
  whatsapp: string | null;
}) {
  const { vaciar } = useCarrito();
  const mensaje = MENSAJES[estado] ?? {
    titulo: "No pudimos confirmar el pago",
    texto: "Si se descontó dinero, escríbele a la tienda con tu número de pedido.",
    aprobado: false,
  };

  useEffect(() => {
    if (mensaje.aprobado) vaciar();
  }, [mensaje.aprobado, vaciar]);

  return (
    <div className="rounded-2xl border border-lila/16 p-7" role="status">
      <span
        className={`flex size-12 items-center justify-center rounded-full text-xl font-bold text-white ${
          mensaje.aprobado ? "bg-violeta" : "bg-superficie ring-1 ring-lila/30"
        }`}
        aria-hidden="true"
      >
        {mensaje.aprobado ? "✓" : "!"}
      </span>
      <h1 className="mt-5 font-serif text-[34px] leading-tight text-texto">{mensaje.titulo}</h1>
      {folio && <p className="mt-2 text-sm text-texto-suave">Pedido {folio}</p>}
      <p className="mt-4 text-[15px] leading-[1.6] text-texto-suave">{mensaje.texto}</p>

      <div className="mt-7 flex flex-wrap gap-3">
        {mensaje.aprobado ? (
          <Link
            href={`/t/${slug}/productos`}
            className="flex h-11 items-center rounded-full bg-violeta px-5 text-sm font-semibold text-white hover:bg-violeta-hover hover:no-underline"
          >
            Seguir comprando
          </Link>
        ) : (
          <Link
            href={`/t/${slug}/carrito`}
            className="flex h-11 items-center rounded-full bg-violeta px-5 text-sm font-semibold text-white hover:bg-violeta-hover hover:no-underline"
          >
            Volver al carrito
          </Link>
        )}
        {whatsapp && (
          <EnlaceExterno
            enlace={whatsapp}
            className="flex h-11 items-center rounded-full border border-lila/40 px-5 text-sm text-texto hover:bg-violeta/15"
          >
            Escribirle a la tienda
          </EnlaceExterno>
        )}
      </div>
    </div>
  );
}
