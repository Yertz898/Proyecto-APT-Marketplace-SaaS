"use client";

import { useEffect, useState } from "react";

import { cambiarPlan, cancelarPlan, obtenerPlan, reanudarPlan } from "@/lib/api/gestion";
import { formatearFecha, formatearPesos } from "@/lib/formato";
import type { Plan } from "@/lib/tipos";
import type { EstadoDelPlan } from "@/lib/tipos-gestion";

import { Aviso, Boton, mensajeDe } from "./controles";
import { Cabecera, Cargando, Error, Tarjeta } from "./piezas";

/*
 * El plan de la tienda: verlo, cambiarlo y cancelarlo.
 *
 * No hay cobro en línea. El cambio es inmediato y la facturación se coordina
 * con DealCommerce; por eso cada botón dice qué pasa al apretarlo antes de
 * hacerlo, y cancelar pide confirmación aparte.
 */
export function PantallaPlan() {
  const [estado, setEstado] = useState<EstadoDelPlan | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);
  const [trabajando, setTrabajando] = useState<Plan | "cancelar" | "reanudar" | null>(null);
  const [aviso, setAviso] = useState<{ tipo: "ok" | "error"; texto: string } | null>(null);
  const [confirmandoCancelacion, setConfirmandoCancelacion] = useState(false);

  useEffect(() => {
    obtenerPlan().then(setEstado, (error) => setFallo(mensajeDe(error)));
  }, []);

  async function hacer(
    accion: Plan | "cancelar" | "reanudar",
    llamada: () => Promise<EstadoDelPlan>,
    exito: string,
  ) {
    setTrabajando(accion);
    setAviso(null);
    try {
      setEstado(await llamada());
      setAviso({ tipo: "ok", texto: exito });
    } catch (error) {
      setAviso({ tipo: "error", texto: mensajeDe(error) });
    } finally {
      setTrabajando(null);
      setConfirmandoCancelacion(false);
    }
  }

  if (fallo) return <Error mensaje={fallo} />;
  if (!estado) return <Cargando />;

  const cancelada = Boolean(estado.canceladaEn);

  return (
    <>
      <Cabecera
        titulo="Tu plan"
        descripcion="Precios mensuales netos por tienda. El cambio es inmediato y la facturación se coordina con DealCommerce."
      />

      {cancelada && (
        <div role="status" className="mb-5 rounded-[14px] border border-ambar bg-trigo p-5 text-marino">
          <p className="font-semibold">Tu suscripción está cancelada.</p>
          <p className="mt-1 text-[14px] text-pizarra">
            La cancelaste el {formatearFecha(estado.canceladaEn as string)}. Tu tienda no se muestra al
            público, pero tu catálogo, tus pedidos y tus cuentas siguen guardados.
          </p>
          <Boton
            className="mt-4"
            disabled={trabajando !== null}
            onClick={() => hacer("reanudar", reanudarPlan, "Reanudamos tu suscripción. Tu tienda vuelve a estar abierta.")}
          >
            {trabajando === "reanudar" ? "Reanudando…" : "Reanudar suscripción"}
          </Boton>
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        {estado.planes.map((opcion) => {
          const esActual = opcion.plan === estado.plan;
          return (
            <Tarjeta key={opcion.plan} className={esActual ? "border-acero" : undefined}>
              <div className="flex items-center justify-between gap-2">
                <p className="font-jakarta text-[18px] font-extrabold">{opcion.nombre}</p>
                {esActual && (
                  <span className="rounded-full bg-cielo px-2.5 py-1 text-[11px] font-semibold text-acero">
                    Tu plan
                  </span>
                )}
              </div>
              <p className="mt-2 font-jakarta text-[26px] font-extrabold tracking-[-0.02em]">
                {formatearPesos(opcion.precioNeto)}
                <span className="ml-1 text-[13px] font-normal text-pizarra">al mes</span>
              </p>
              <p className="mt-2 min-h-[63px] text-[14px] leading-[1.5] text-pizarra">{opcion.incluye}</p>
              {!esActual && (
                <Boton
                  variante="secundario"
                  className="mt-4 w-full"
                  disabled={cancelada || trabajando !== null}
                  onClick={() =>
                    hacer(opcion.plan, () => cambiarPlan(opcion.plan), `Tu tienda ahora está en el plan ${opcion.nombre}.`)
                  }
                >
                  {trabajando === opcion.plan ? "Cambiando…" : `Cambiar a ${opcion.nombre}`}
                </Boton>
              )}
            </Tarjeta>
          );
        })}
      </div>

      {aviso && <Aviso tipo={aviso.tipo}>{aviso.texto}</Aviso>}

      {!cancelada && (
        <section className="mt-10 border-t border-arena pt-6">
          <p className="text-[13px] font-semibold text-marino">Cancelar suscripción</p>
          <p className="mt-1 max-w-[560px] text-[14px] text-pizarra">
            Tu tienda deja de mostrarse al público en el momento. No se borra nada: puedes reanudar
            cuando quieras desde esta misma pantalla.
          </p>
          {confirmandoCancelacion ? (
            <div role="alertdialog" aria-label="Confirmar cancelación" className="mt-4 rounded-[12px] border border-[#f4c7c3] bg-[#fef3f2] p-4">
              <p className="text-[14px] font-semibold text-[#912018]">¿Seguro que quieres cancelar tu plan?</p>
              <div className="mt-3 flex flex-wrap gap-2.5">
                <Boton
                  variante="peligro"
                  disabled={trabajando !== null}
                  onClick={() => hacer("cancelar", cancelarPlan, "Cancelamos tu suscripción.")}
                >
                  {trabajando === "cancelar" ? "Cancelando…" : "Sí, cancelar mi plan"}
                </Boton>
                <Boton variante="secundario" onClick={() => setConfirmandoCancelacion(false)}>
                  No, volver
                </Boton>
              </div>
            </div>
          ) : (
            <Boton variante="peligro" className="mt-4" onClick={() => setConfirmandoCancelacion(true)}>
              Cancelar plan
            </Boton>
          )}
        </section>
      )}
    </>
  );
}
