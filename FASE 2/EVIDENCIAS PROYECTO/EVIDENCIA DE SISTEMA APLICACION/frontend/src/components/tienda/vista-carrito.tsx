"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { confirmarPedido, cotizarCarrito } from "@/lib/api/carrito";
import { formatearPesos } from "@/lib/formato";
import type {
  CarritoCotizado,
  DatosDeContacto,
  LineaCarrito,
  PedidoConfirmado,
} from "@/lib/tipos";

import { useCarrito } from "./carrito";
import { EnlaceExterno } from "./enlace-externo";

export function VistaCarrito({ slugTienda }: { slugTienda: string }) {
  const { lineas, quitar, vaciar } = useCarrito();
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
    direccion_entrega: "",
    notas: "",
  });

  const faltanDatos =
    contacto.nombre_contacto.trim() === "" || contacto.telefono_contacto.trim() === "";

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
      setPedido(await confirmarPedido(slugTienda, lineas, contacto));
      setError(null);
      vaciar();
    } catch (problema) {
      setError(problema instanceof Error ? problema.message : "No se pudo confirmar el pedido.");
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
        <section className="rounded-2xl border border-lila/16 p-5">
          <h2 className="text-[13px] font-semibold text-texto">Tus datos</h2>
          <p className="mt-1.5 text-xs leading-[1.5] text-texto-suave">
            Para coordinar el pago y la entrega. No se cobra en línea.
          </p>

          <div className="mt-4 flex flex-col gap-3">
            <Campo
              id="nombre-contacto"
              etiqueta="Nombre"
              valor={contacto.nombre_contacto}
              onCambio={(valor) => escribir("nombre_contacto", valor)}
              autoComplete="name"
            />
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
        </section>

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

        <button
          type="button"
          disabled={
            confirmando || faltanDatos || cotizacion === null || cotizacion.rechazo !== null
          }
          onClick={confirmar}
          className="mt-5 h-12 w-full cursor-pointer rounded-full bg-violeta text-sm font-semibold text-white transition-colors hover:bg-violeta-hover disabled:cursor-not-allowed disabled:opacity-50"
        >
          {confirmando ? "Confirmando…" : "Confirmar pedido"}
        </button>

        <p className="mt-3 text-center text-xs text-texto-suave">
          {faltanDatos
            ? "Completa tu nombre y tu WhatsApp para confirmar."
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
}: {
  id: string;
  etiqueta: string;
  valor: string;
  onCambio: (valor: string) => void;
  autoComplete?: string;
  inputMode?: "tel" | "text";
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
        className="h-11 rounded-xl border border-lila/20 bg-transparent px-3 text-sm text-texto outline-none transition-colors focus-visible:border-lila"
      />
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