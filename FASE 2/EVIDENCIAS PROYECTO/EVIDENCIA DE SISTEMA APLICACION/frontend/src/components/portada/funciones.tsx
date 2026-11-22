import type { ReactNode } from "react";

import { formatearPesos } from "@/lib/formato";

import { FranjaClara, TituloDeSeccion } from "./secciones";

/*
 * Las ocho funciones del producto, con jerarquía.
 *
 * Dos bloques grandes cuentan lo que más pesa —los precios por cantidad con la
 * carga desde Excel, y el panel con el pronóstico y el asistente— y los otros
 * cuatro van en una fila compacta. Antes eran ocho cajas iguales, y todo lo
 * que pesa lo mismo termina por no pesar nada.
 *
 * Todas sirven a cualquier tienda de la plataforma. Las vistas de los bloques
 * grandes son de ejemplo y decorativas (aria-hidden): el texto de cada bloque
 * dice lo mismo.
 */

const SECUNDARIAS = [
  {
    titulo: "Tu tienda con tu marca",
    detalle: "Tu logo, tus colores y tu tipografía. Se ve tuya, no nuestra.",
    icono: (
      <>
        <path d="M12 3a9 9 0 000 18c1.1 0 2-.9 2-2 0-.52-.2-.99-.53-1.34A1.98 1.98 0 0113 16.2c0-1.1.9-2 2-2h2.2A3.8 3.8 0 0021 10.4C21 6.3 16.97 3 12 3z" />
        <circle cx="7.5" cy="11.5" r="1" />
        <circle cx="12" cy="7.5" r="1" />
        <circle cx="16.5" cy="11.5" r="1" />
      </>
    ),
  },
  {
    titulo: "Agenda de visitas",
    detalle: "Tus clientes reservan hora para ir a verte, sin cruces.",
    icono: (
      <>
        <rect x="3" y="5" width="18" height="16" rx="2" />
        <path d="M3 10h18M8 3v4M16 3v4" />
        <path d="M8.5 14.5l2 2 4-4" />
      </>
    ),
  },
  {
    titulo: "Alerta de quiebre",
    detalle: "Te avisa qué se te va a acabar antes de que pase.",
    icono: (
      <>
        <path d="M12 4l9 16H3l9-16z" />
        <path d="M12 10v4M12 17h.01" />
      </>
    ),
  },
  {
    titulo: "Sin comisión por venta",
    detalle: "Pagas tu plan mensual y nada más. Lo que vendes es tuyo.",
    icono: (
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="M15 9.5c-.6-1-1.7-1.5-3-1.5-1.7 0-3 .9-3 2.2 0 3 6 1.6 6 4.6 0 1.3-1.3 2.2-3 2.2-1.4 0-2.6-.6-3.1-1.6M12 6.5v1.5M12 16v1.5" />
      </>
    ),
  },
];

function Icono({ children }: { children: ReactNode }) {
  return (
    <span className="flex size-10 flex-none items-center justify-center rounded-lg bg-cielo">
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#1F4E79"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        {children}
      </svg>
    </span>
  );
}

export function Funciones() {
  return (
    <FranjaClara id="funciones">
      <TituloDeSeccion antetitulo="Funciones">Todo lo que hoy haces a mano, resuelto</TituloDeSeccion>

      <div className="grid grid-cols-[repeat(auto-fit,minmax(min(100%,460px),1fr))] gap-4">
        <BloquePrecios />
        <BloqueDatos />
      </div>

      <div className="grid grid-cols-[repeat(auto-fit,minmax(min(100%,240px),1fr))] gap-4">
        {SECUNDARIAS.map((funcion) => (
          <div key={funcion.titulo} className="flex items-start gap-3.5 rounded-xl border border-arena bg-hueso p-5">
            <Icono>{funcion.icono}</Icono>
            <div className="flex flex-col gap-1">
              <h3 className="font-jakarta text-[16px] font-bold">{funcion.titulo}</h3>
              <p className="text-[14px] leading-[1.5] text-pizarra">{funcion.detalle}</p>
            </div>
          </div>
        ))}
      </div>
    </FranjaClara>
  );
}

function Bloque({ titulo, children, vista }: { titulo: ReactNode; children: ReactNode; vista: ReactNode }) {
  return (
    <div className="flex flex-col gap-5 rounded-xl border border-arena bg-hueso p-[clamp(20px,2.4cqi,32px)]">
      <div className="flex flex-col gap-3">{titulo}</div>
      <div className="flex flex-col gap-2">{children}</div>
      <div aria-hidden="true" className="mt-auto">
        {vista}
      </div>
    </div>
  );
}

function Linea({ titulo, detalle }: { titulo: string; detalle: string }) {
  return (
    <p className="text-[15px] leading-[1.5] text-pizarra">
      <span className="font-semibold text-marino">{titulo}.</span> {detalle}
    </p>
  );
}

function BloquePrecios() {
  const tramos = [
    { desde: "1 a 5 u.", precio: 12990, activo: false },
    { desde: "6 a 11 u.", precio: 10990, activo: true },
    { desde: "12 u. o más", precio: 9490, activo: false },
  ];
  return (
    <Bloque
      titulo={
        <h3 className="font-jakarta text-[clamp(21px,1.9cqi,26px)] leading-[1.2] font-extrabold tracking-[-0.02em]">
          Tus precios mayoristas, sin sacar cuentas
        </h3>
      }
      vista={
        <div className="rounded-lg border border-arena bg-white p-4">
          <div className="mb-3 flex items-center justify-between text-xs text-pizarra">
            <span>Cadena 925 · 8 unidades</span>
            <span className="rounded-full bg-jade-claro px-2 py-0.5 font-semibold text-jade">Precio por tramo</span>
          </div>
          <div className="grid grid-cols-3 gap-2">
            {tramos.map((t) => (
              <div
                key={t.desde}
                className={`rounded-md border px-2.5 py-2 ${t.activo ? "border-acero bg-cielo" : "border-arena bg-hueso"}`}
              >
                <p className="text-[11px] text-pizarra">{t.desde}</p>
                <p className={`text-sm font-bold tabular-nums ${t.activo ? "text-acero" : "text-marino"}`}>
                  {formatearPesos(t.precio)}
                </p>
              </div>
            ))}
          </div>
          <div className="mt-3 flex items-center justify-between border-t border-arena pt-3 text-sm">
            <span className="text-pizarra">Total</span>
            <span className="font-bold text-marino tabular-nums">{formatearPesos(87920)}</span>
          </div>
        </div>
      }
    >
      <Linea titulo="Precios por cantidad automáticos" detalle="Defines los tramos una vez y el total se calcula solo." />
      <Linea titulo="Carga desde Excel" detalle="Sube tu planilla de siempre y tu catálogo queda listo." />
    </Bloque>
  );
}

function BloqueDatos() {
  const barras = [38, 44, 41, 52, 49, 58, 63];
  return (
    <div className="flex flex-col gap-5 rounded-xl bg-marino p-[clamp(20px,2.4cqi,32px)] text-white">
      <h3 className="font-jakarta text-[clamp(21px,1.9cqi,26px)] leading-[1.2] font-extrabold tracking-[-0.02em]">
        Tu negocio en números, y una forma simple de preguntarle
      </h3>
      <div className="flex flex-col gap-2 text-[15px] leading-[1.5] text-[#C9D3DF]">
        <p>
          <span className="font-semibold text-white">Panel de ventas.</span> Qué se vende, a quién y cuándo, en una sola
          pantalla.
        </p>
        <p>
          <span className="font-semibold text-white">Pronóstico de demanda.</span> Anticipa cuánto vas a vender para
          comprar mejor.
        </p>
        <p>
          <span className="font-semibold text-white">Asistente de ventas.</span> Pregúntale “¿qué vendí más en agosto?”
          y te responde al tiro.
        </p>
      </div>

      <div aria-hidden="true" className="mt-auto grid grid-cols-[repeat(auto-fit,minmax(min(100%,200px),1fr))] gap-3">
        <div className="flex flex-col justify-between gap-3 rounded-lg bg-white/[0.06] p-4 ring-1 ring-white/10">
          <span className="text-xs text-[#C9D3DF]">Ventas por semana</span>
          <div className="flex h-16 items-end gap-1.5">
            {barras.map((alto, i) => (
              <span
                key={i}
                className={`flex-1 rounded-t-[3px] ${i === barras.length - 1 ? "bg-ambar" : "bg-[#5B8DB8]"}`}
                style={{ height: `${alto + 30}%` }}
              />
            ))}
          </div>
          <span className="text-xs text-[#C9D3DF]">
            Pronóstico próximo mes <span className="font-semibold text-white tabular-nums">{formatearPesos(6400000)}</span>
          </span>
        </div>

        <div className="flex flex-col gap-2 rounded-lg bg-white/[0.06] p-4 ring-1 ring-white/10">
          <span className="self-end rounded-xl rounded-tr-sm bg-acero px-3 py-1.5 text-[13px]">
            ¿Qué vendí más en agosto?
          </span>
          <span className="rounded-xl rounded-tl-sm bg-white px-3 py-2 text-[13px] leading-[1.45] text-marino">
            Tu producto estrella fue la <b>cadena 925</b>: 142 unidades y{" "}
            <b className="tabular-nums">{formatearPesos(1384500)}</b>, el 18 % de tus ventas del mes.
          </span>
        </div>
      </div>
    </div>
  );
}
