import Link from "next/link";

import { SOLICITAR_ACCESO } from "./enlaces";
import { FranjaClara, TituloDeSeccion } from "./secciones";

/*
 * Los tres planes.
 *
 * Ninguno tiene precio todavía y la sección lo dice de frente en vez de
 * inventar cifras: cómo se cobra la suscripción es una de las cosas que el
 * equipo aún no decide (CONVENCIONES.md > Lo que no está decidido).
 */

type Plan = {
  nombre: string;
  para: string;
  incluye: string[];
  /** Mensual, neto, en pesos chilenos. */
  precio: string;
  destacado?: boolean;
};

/*
 * Lo que entra acá sirve a cualquier tienda de la plataforma.
 *
 * DealCommerce aloja comercios de rubros distintos, así que las formas de
 * vender propias de uno —los lotes cerrados y la venta por gramo de la
 * joyería— no se nombran como si fueran de la plataforma. Un almacén, una
 * distribuidora o una tienda de cosmética tienen que verse reflejados en esta
 * misma lista.
 */
const PLANES: Plan[] = [
  {
    nombre: "Básico",
    para: "Para dejar de cotizar a mano.",
    precio: "$10.990",
    incluye: [
      "Tu catálogo en línea",
      "Precios por cantidad automáticos",
      "Carga desde Excel",
      "Pedidos por enlace",
    ],
  },
  {
    nombre: "Premium",
    para: "Para vender más y ordenar tu negocio.",
    precio: "$20.990",
    destacado: true,
    incluye: [
      "Todo lo del plan Básico",
      "Tu logo, colores y tipografía",
      "Panel de ventas",
      "Agenda de visitas",
      "Varias cuentas para tu equipo",
    ],
  },
  {
    nombre: "Ultimate",
    para: "Para decidir con tus datos.",
    precio: "$35.990",
    incluye: [
      "Todo lo del plan Premium",
      "Pronóstico de demanda",
      "Segmentos de clientes",
      "Asistente que responde sobre tus ventas",
    ],
  },
];

export function Planes() {
  return (
    <FranjaClara id="planes">
      <TituloDeSeccion
        antetitulo="Planes"
        bajada="Precios mensuales por tienda. Sin permanencia: se cancela cuando quieras."
      >
        Elige cómo quieres partir
      </TituloDeSeccion>

      <div className="grid grid-cols-[repeat(auto-fit,minmax(min(100%,300px),1fr))] items-stretch gap-5">
        {PLANES.map((plan) => (plan.destacado ? <Destacado key={plan.nombre} plan={plan} /> : <Normal key={plan.nombre} plan={plan} />))}
      </div>
    </FranjaClara>
  );
}

function Normal({ plan }: { plan: Plan }) {
  return (
    <div className="flex flex-col gap-5 rounded-[18px] border border-arena bg-hueso p-8">
      <Cabecera plan={plan} />
      <Precio valor={plan.precio} />
      <ul className="flex flex-1 list-none flex-col gap-3 border-t border-arena p-0 pt-5 text-[15px] leading-[1.4]">
        {plan.incluye.map((linea) => (
          <li key={linea} className="flex gap-2.5">
            <span aria-hidden="true" className="font-bold text-jade">
              ✓
            </span>
            {linea}
          </li>
        ))}
      </ul>
      <Link
        href={SOLICITAR_ACCESO}
        className="flex h-12 items-center justify-center rounded-[12px] border border-acero text-[15px] font-semibold text-acero no-underline hover:bg-cielo hover:no-underline"
      >
        Solicitar acceso
      </Link>
    </div>
  );
}

function Destacado({ plan }: { plan: Plan }) {
  return (
    <div className="flex flex-col gap-5 rounded-[18px] bg-acero p-8 text-white shadow-[0_20px_44px_rgba(31,78,121,.25)]">
      <div className="flex flex-col gap-1.5">
        <div className="flex items-center justify-between gap-2">
          <h3 className="font-jakarta text-2xl font-extrabold">{plan.nombre}</h3>
          <span className="rounded-full bg-ambar px-2.5 py-1 text-xs font-bold text-marino">Recomendado</span>
        </div>
        <span className="text-[15px] text-[#DCE6F0]">{plan.para}</span>
      </div>

      <Precio valor={plan.precio} claro />

      <ul className="flex flex-1 list-none flex-col gap-3 border-t border-white/22 p-0 pt-5 text-[15px] leading-[1.4]">
        {plan.incluye.map((linea) => (
          <li key={linea} className="flex gap-2.5">
            <span aria-hidden="true" className="font-bold">
              ✓
            </span>
            {linea}
          </li>
        ))}
      </ul>

      <Link
        href={SOLICITAR_ACCESO}
        className="flex h-12 items-center justify-center rounded-[12px] bg-white text-[15px] font-semibold text-acero no-underline hover:bg-cielo hover:no-underline"
      >
        Solicitar acceso
      </Link>
    </div>
  );
}

function Cabecera({ plan }: { plan: Plan }) {
  return (
    <div className="flex flex-col gap-1.5">
      <h3 className="font-jakarta text-2xl font-extrabold">{plan.nombre}</h3>
      <span className="text-[15px] text-pizarra">{plan.para}</span>
    </div>
  );
}

function Precio({ valor, claro = false }: { valor: string; claro?: boolean }) {
  return (
    <p className="flex items-baseline gap-1.5">
      <span className="font-jakarta text-[32px] font-extrabold tracking-[-0.02em]">{valor}</span>
      <span className={claro ? "text-sm text-[#DCE6F0]" : "text-sm text-pizarra"}>al mes</span>
    </p>
  );
}
