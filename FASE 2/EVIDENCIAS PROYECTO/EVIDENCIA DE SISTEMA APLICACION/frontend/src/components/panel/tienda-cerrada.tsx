"use client";

import { useState } from "react";

import { escribirALaPlataforma } from "@/lib/api/gestion";
import { cerrarSesion } from "@/lib/api/sesion";
import type { UsuarioSesion } from "@/lib/tipos";

import { Aviso, Boton, mensajeDe } from "./controles";
import { Tarjeta } from "./piezas";

/*
 * Lo único que ve el dueño de una tienda que cerró la administración.
 *
 * Su tienda, su nombre y su correo salen de la sesión y se muestran sin poder
 * cambiarlos: el mensaje lo arma el backend desde la cuenta. La persona solo
 * escribe qué necesita.
 */
export function TiendaCerrada({ usuario }: { usuario: UsuarioSesion }) {
  const [mensaje, setMensaje] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [recibo, setRecibo] = useState<string | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);

  async function enviar() {
    setEnviando(true);
    setFallo(null);
    try {
      setRecibo(await escribirALaPlataforma(mensaje.trim()));
      setMensaje("");
    } catch (error) {
      setFallo(mensajeDe(error));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="mx-auto max-w-[620px] py-10">
      <div role="status" className="rounded-[14px] border border-ambar bg-trigo p-5 text-marino">
        <p className="font-jakarta text-[20px] font-extrabold">Tu tienda está cerrada</p>
        <p className="mt-1 text-[14px] text-pizarra">
          La administración de DealCommerce cerró {usuario.tienda?.nombre}. Tu vitrina no se muestra al
          público y el panel está en pausa, pero no se borró nada: tu catálogo, tus pedidos y tus
          clientes siguen guardados.
        </p>
      </div>

      <Tarjeta className="mt-5">
        <p className="font-jakarta text-[17px] font-bold text-marino">Escribir a DealCommerce</p>
        <dl className="mt-3 grid gap-1 rounded-[12px] bg-hueso p-3 text-[13px] sm:grid-cols-[90px_1fr]">
          <dt className="text-pizarra">Tienda</dt>
          <dd className="font-semibold text-marino">{usuario.tienda?.nombre}</dd>
          <dt className="text-pizarra">De</dt>
          <dd className="text-marino">{usuario.nombre}</dd>
          <dt className="text-pizarra">Correo</dt>
          <dd className="text-marino">{usuario.email}</dd>
        </dl>

        {recibo ? (
          <Aviso tipo="ok">{recibo}</Aviso>
        ) : (
          <>
            <label htmlFor="mensaje-a-dealcommerce" className="mt-4 block text-[13px] font-semibold text-marino">
              ¿Qué necesitas?
            </label>
            <textarea
              id="mensaje-a-dealcommerce"
              rows={5}
              maxLength={2000}
              value={mensaje}
              onChange={(e) => setMensaje(e.target.value)}
              placeholder="Por ejemplo: quiero reabrir mi tienda, ¿qué tengo que hacer?"
              className="mt-2 w-full rounded-[12px] border border-niebla bg-white p-3 text-[14px] text-marino outline-none focus-visible:border-acero"
            />
            <p className="mt-1 text-[12px] text-pizarra">Te respondemos a tu correo.</p>
            <Boton className="mt-3" disabled={enviando || mensaje.trim().length < 5} onClick={enviar}>
              {enviando ? "Enviando…" : "Enviar mensaje"}
            </Boton>
            {fallo && <Aviso tipo="error">{fallo}</Aviso>}
          </>
        )}
      </Tarjeta>

      <div className="mt-6 text-center">
        <Boton variante="secundario" onClick={cerrarSesion}>
          Cerrar sesión
        </Boton>
      </div>
    </div>
  );
}
