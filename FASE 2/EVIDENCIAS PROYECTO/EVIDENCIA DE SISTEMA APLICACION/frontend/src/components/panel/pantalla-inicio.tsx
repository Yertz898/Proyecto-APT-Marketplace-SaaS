"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { useSesion } from "@/components/sesion/usar-sesion";
import { obtenerPedidos, obtenerPronostico, obtenerResumenDeVentas } from "@/lib/api/pedidos";
import { formatearFecha, formatearPesos } from "@/lib/formato";
import type { PedidoDelPanel, PronosticoDeDemanda, ResumenDeVentas } from "@/lib/tipos-panel";

import { InsigniaDeEstado } from "./estado-pedido";
import { LineaDeTiempo, SERIE } from "./graficos";
import { Cabecera, Cargando, Kpi, Tarjeta, TituloDeTarjeta } from "./piezas";
import { NOMBRE_DEL_PLAN, planAlcanza, rolAlcanza, seccionDe } from "./secciones";

/*
 * Inicio del panel: cómo va la tienda hoy, de un vistazo.
 *
 * Junta lo que ya existe en otras pantallas —ventas, pedidos y quiebres— sin
 * pedirle nada nuevo al backend: cada bloque llama al mismo endpoint que su
 * sección. Un bloque que el plan o el rol no incluye no se pide ni se dibuja;
 * uno que falla se queda callado, porque el inicio no puede romperse porque
 * un indicador no cargó.
 */

type Estado<T> = T | null | "sin-acceso";

function puede(href: string, rol: Parameters<typeof rolAlcanza>[0], plan: Parameters<typeof planAlcanza>[0]) {
  const seccion = seccionDe(href);
  return Boolean(seccion && rolAlcanza(rol, seccion) && planAlcanza(plan, seccion.plan));
}

export function PantallaInicio() {
  const { sesion, hidratado } = useSesion();
  const tienda = sesion?.usuario.tienda;
  const rol = sesion?.usuario.rol;
  const plan = tienda?.plan;

  const [pedidos, setPedidos] = useState<Estado<PedidoDelPanel[]>>(null);
  const [resumen, setResumen] = useState<Estado<ResumenDeVentas>>(null);
  const [pronostico, setPronostico] = useState<Estado<PronosticoDeDemanda>>(null);

  useEffect(() => {
    if (!tienda) return;
    const pedir = <T,>(href: string, carga: () => Promise<T>, guardar: (v: Estado<T>) => void) => {
      if (!puede(href, rol, plan)) {
        guardar("sin-acceso");
        return;
      }
      carga()
        .then(guardar)
        .catch(() => guardar("sin-acceso"));
    };
    pedir("/panel/pedidos", obtenerPedidos, setPedidos);
    pedir("/panel/ventas", obtenerResumenDeVentas, setResumen);
    pedir("/panel/pronostico", obtenerPronostico, setPronostico);
  }, [tienda, rol, plan]);

  if (!hidratado || !tienda) return <Cargando />;

  const hoy = new Intl.DateTimeFormat("es-CL", { weekday: "long", day: "numeric", month: "long" }).format(new Date());
  const primerNombre = sesion?.usuario.nombre.split(" ")[0] ?? "";

  return (
    <>
      <Cabecera
        antetitulo={hoy}
        titulo={`Hola${primerNombre ? `, ${primerNombre}` : ""}`}
        descripcion={`Así va ${tienda.nombre}. Plan ${NOMBRE_DEL_PLAN[tienda.plan]}.`}
        acciones={<EnlaceDeTienda slug={tienda.slug} />}
      />

      <Indicadores resumen={resumen} pedidos={pedidos} />

      <div className="mt-5 grid gap-5 @4xl:grid-cols-[minmax(0,1.6fr)_minmax(0,1fr)]">
        <div className="flex min-w-0 flex-col gap-5">
          {resumen && resumen !== "sin-acceso" && <VentasDelAno resumen={resumen} />}
          <PedidosRecientes pedidos={pedidos} />
        </div>
        <div className="flex min-w-0 flex-col gap-5">
          {pronostico && pronostico !== "sin-acceso" && <Quiebres pronostico={pronostico} />}
          <Accesos rol={rol} plan={plan} />
        </div>
      </div>
    </>
  );
}

function EnlaceDeTienda({ slug }: { slug: string }) {
  const [copiado, setCopiado] = useState(false);

  async function copiar() {
    try {
      await navigator.clipboard.writeText(`${window.location.origin}/t/${slug}`);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 1800);
    } catch {
      setCopiado(false);
    }
  }

  return (
    <div className="flex items-center gap-2 rounded-xl border border-arena bg-white py-1.5 pr-1.5 pl-3.5">
      <a href={`/t/${slug}`} target="_blank" rel="noreferrer" className="text-[13.5px] font-semibold text-acero">
        /t/{slug}
      </a>
      <button
        type="button"
        onClick={copiar}
        className="h-8 cursor-pointer rounded-lg bg-acero px-3 text-[12.5px] font-semibold text-white hover:bg-acero-hondo"
      >
        {copiado ? "¡Copiado!" : "Copiar enlace"}
      </button>
    </div>
  );
}

function Indicadores({
  resumen,
  pedidos,
}: {
  resumen: Estado<ResumenDeVentas>;
  pedidos: Estado<PedidoDelPanel[]>;
}) {
  if (resumen && resumen !== "sin-acceso") {
    const variacion = resumen.mesAnterior.variacion;
    const ticket = resumen.ventas.pedidos ? Math.round(resumen.ventas.total / resumen.ventas.pedidos) : 0;
    return (
      <div className="grid grid-cols-[repeat(auto-fit,minmax(min(100%,160px),1fr))] gap-3">
        <Kpi
          etiqueta={`Ventas de ${resumen.mes.etiqueta}`}
          valor={formatearPesos(resumen.ventas.total)}
          nota={
            variacion === null
              ? `${resumen.ventas.pedidos} pedidos`
              : `${variacion >= 0 ? "▲" : "▼"} ${Math.abs(Math.round(variacion * 100))} % contra el mes anterior`
          }
          tono={variacion === null ? "neutro" : variacion >= 0 ? "sube" : "baja"}
          href="/panel/ventas"
        />
        <Kpi
          etiqueta="Por coordinar"
          valor={formatearPesos(resumen.porCoordinar.total)}
          nota={`${resumen.porCoordinar.pedidos} ${resumen.porCoordinar.pedidos === 1 ? "pedido pendiente" : "pedidos pendientes"}`}
          tono={resumen.porCoordinar.pedidos > 0 ? "alerta" : "neutro"}
          href="/panel/pedidos"
        />
        <Kpi
          etiqueta="Ticket promedio del mes"
          valor={ticket ? formatearPesos(ticket) : "—"}
          nota={`${resumen.ventas.pedidos} pedidos confirmados`}
        />
        <Kpi
          etiqueta="Mes anterior"
          valor={formatearPesos(resumen.mesAnterior.total)}
          nota={`${resumen.mesAnterior.pedidos} pedidos`}
        />
      </div>
    );
  }

  if (pedidos && pedidos !== "sin-acceso") {
    const pendientes = pedidos.filter((p) => p.estado === "PENDIENTE");
    return (
      <div className="grid grid-cols-[repeat(auto-fit,minmax(min(100%,160px),1fr))] gap-3">
        <Kpi
          etiqueta="Por coordinar"
          valor={String(pendientes.length)}
          nota={formatearPesos(pendientes.reduce((s, p) => s + p.total, 0))}
          tono={pendientes.length ? "alerta" : "neutro"}
          href="/panel/pedidos"
        />
        <Kpi etiqueta="Pedidos en total" valor={String(pedidos.length)} />
      </div>
    );
  }

  if (resumen === null || pedidos === null) {
    return <div className="h-[104px] animate-pulse rounded-xl bg-white/60 motion-reduce:animate-none" />;
  }
  return null;
}

function VentasDelAno({ resumen }: { resumen: ResumenDeVentas }) {
  const puntos = resumen.serieMensual.map((m) => ({ etiqueta: m.etiqueta, valor: m.total, atenuado: m.enCurso }));
  return (
    <Tarjeta>
      <TituloDeTarjeta
        detalle="Ventas confirmadas y entregadas de los últimos doce meses."
        accion={
          <Link href="/panel/ventas" className="text-[13px] font-semibold text-acero">
            Ver ventas
          </Link>
        }
      >
        Cómo viene el año
      </TituloDeTarjeta>
      <LineaDeTiempo series={[{ nombre: "Ventas", color: SERIE[0], puntos }]} formatear={formatearPesos} compacta />
    </Tarjeta>
  );
}

function PedidosRecientes({ pedidos }: { pedidos: Estado<PedidoDelPanel[]> }) {
  if (pedidos === "sin-acceso") return null;

  return (
    <Tarjeta className="p-0">
      <div className="px-6 pt-5">
        <TituloDeTarjeta
          accion={
            <Link href="/panel/pedidos" className="text-[13px] font-semibold text-acero">
              Ver todos
            </Link>
          }
        >
          Pedidos recientes
        </TituloDeTarjeta>
      </div>

      {pedidos === null ? (
        <Cargando texto="Cargando pedidos…" />
      ) : pedidos.length === 0 ? (
        <p className="px-6 pb-6 text-[14px] text-pizarra">
          Todavía no llegan pedidos. Comparte el enlace de tu tienda para recibir el primero.
        </p>
      ) : (
        <ul className="flex list-none flex-col divide-y divide-arena border-t border-arena p-0">
          {pedidos.slice(0, 6).map((pedido) => (
            <li key={pedido.id} className="flex items-center justify-between gap-3 px-6 py-3">
              <div className="min-w-0">
                <p className="truncate text-[14px] font-semibold text-marino">{pedido.nombreContacto}</p>
                <p className="text-[12px] text-pizarra tabular-nums">
                  {pedido.folio} · {formatearFecha(pedido.creadoEn)}
                </p>
              </div>
              <div className="flex flex-none items-center gap-3">
                <span className="hidden text-[14px] font-semibold text-marino tabular-nums @xl:inline">
                  {formatearPesos(pedido.total)}
                </span>
                <InsigniaDeEstado estado={pedido.estado}>{pedido.estadoVisible}</InsigniaDeEstado>
              </div>
            </li>
          ))}
        </ul>
      )}
    </Tarjeta>
  );
}

function Quiebres({ pronostico }: { pronostico: PronosticoDeDemanda }) {
  const enRiesgo = pronostico.productos
    .filter((p) => p.diasHastaQuiebre !== null)
    .sort((a, b) => (a.diasHastaQuiebre ?? 0) - (b.diasHastaQuiebre ?? 0))
    .slice(0, 5);

  return (
    <Tarjeta>
      <TituloDeTarjeta
        detalle="Al ritmo que proyecta el pronóstico."
        accion={
          <Link href="/panel/pronostico" className="text-[13px] font-semibold text-acero">
            Ver pronóstico
          </Link>
        }
      >
        Se te puede acabar
      </TituloDeTarjeta>
      {enRiesgo.length === 0 ? (
        <p className="text-[14px] text-pizarra">Ningún producto con stock controlado está por acabarse.</p>
      ) : (
        <ul className="flex list-none flex-col gap-2 p-0">
          {enRiesgo.map((producto) => (
            <li
              key={producto.codigo}
              className="flex items-center justify-between gap-3 rounded-lg border border-ambar/40 bg-trigo/50 px-3 py-2"
            >
              <span className="min-w-0 truncate text-[13.5px] text-marino">{producto.nombre}</span>
              <span className="flex-none text-[12px] font-semibold text-ambar-hondo tabular-nums">
                {producto.diasHastaQuiebre === 0 ? "Sin stock" : `~${producto.diasHastaQuiebre} días`}
              </span>
            </li>
          ))}
        </ul>
      )}
    </Tarjeta>
  );
}

const ACCESOS = [
  { href: "/panel/catalogo", texto: "Agregar o editar productos" },
  { href: "/panel/cargas", texto: "Subir una planilla" },
  { href: "/panel/agenda", texto: "Revisar la agenda" },
  { href: "/panel/asistente", texto: "Preguntarle al asistente" },
];

function Accesos({
  rol,
  plan,
}: {
  rol: Parameters<typeof rolAlcanza>[0];
  plan: Parameters<typeof planAlcanza>[0];
}) {
  const visibles = ACCESOS.filter((a) => puede(a.href, rol, plan));
  if (visibles.length === 0) return null;

  return (
    <Tarjeta>
      <TituloDeTarjeta>Accesos rápidos</TituloDeTarjeta>
      <ul className="flex list-none flex-col gap-1 p-0">
        {visibles.map((acceso) => (
          <li key={acceso.href}>
            <Link
              href={acceso.href}
              className="flex items-center justify-between rounded-lg px-3 py-2.5 text-[14px] text-marino no-underline hover:bg-hueso hover:no-underline"
            >
              {acceso.texto}
              <span aria-hidden="true" className="text-acero">
                →
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </Tarjeta>
  );
}
