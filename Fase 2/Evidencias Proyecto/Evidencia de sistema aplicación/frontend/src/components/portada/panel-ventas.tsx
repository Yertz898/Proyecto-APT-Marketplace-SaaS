import { Franja, TituloDeSeccion } from "./secciones";

/*
 * El panel del vendedor, con las ventas del año y el pronóstico.
 *
 * Los números son inventados y la sección lo dice con una etiqueta a la vista.
 * No es un detalle de diseño: el proyecto trabaja con datos sintéticos y todo
 * gráfico hecho con ellos se rotula como tal (CLAUDE.md > Ingesta de planillas).
 *
 * Las alturas van en porcentaje del alto del gráfico. La línea del pronóstico
 * se deriva de esas mismas alturas en vez de repetirlas: si un mes cambia, la
 * línea lo sigue sola.
 */

type Mes = {
  letra: string;
  alto: number;
  tipo: "real" | "actual" | "pronostico";
};

const MESES: Mes[] = [
  { letra: "E", alto: 41.4, tipo: "real" },
  { letra: "F", alto: 37.1, tipo: "real" },
  { letra: "M", alto: 48.6, tipo: "real" },
  { letra: "A", alto: 45.7, tipo: "real" },
  { letra: "M", alto: 54.3, tipo: "real" },
  { letra: "J", alto: 51.4, tipo: "real" },
  { letra: "J", alto: 58.6, tipo: "real" },
  { letra: "A", alto: 62.9, tipo: "real" },
  { letra: "S", alto: 68.6, tipo: "actual" },
  { letra: "O", alto: 72.9, tipo: "pronostico" },
  { letra: "N", alto: 80, tipo: "pronostico" },
  { letra: "D", alto: 91.4, tipo: "pronostico" },
];

/** Centro horizontal de la barra de un mes, en porcentaje del ancho. */
function centroDe(posicion: number): number {
  return ((posicion + 0.5) / MESES.length) * 100;
}

// La línea arranca en el último mes con venta real y recorre los pronosticados.
const DESDE = MESES.findIndex((mes) => mes.tipo === "actual");
const RECORRIDO = MESES.slice(DESDE).map((mes, indice) => ({
  x: centroDe(DESDE + indice),
  y: 100 - mes.alto,
}));

const CIFRAS = [
  { etiqueta: "Ventas de septiembre", valor: "$4.812.300", color: "text-jade" },
  { etiqueta: "Pedidos del mes", valor: "128", color: "" },
  { etiqueta: "Pronóstico para diciembre", valor: "$6.400.000", color: "text-acero" },
];

export function PanelDeVentas() {
  return (
    <Franja className="pb-[clamp(64px,7cqi,112px)]">
      <TituloDeSeccion antetitulo="Tu panel">Mira cómo va tu negocio, y hacia dónde va</TituloDeSeccion>

      <div className="flex flex-col gap-7 rounded-[20px] border border-arena bg-white p-[clamp(20px,3cqi,36px)] shadow-[0_1px_2px_rgba(20,33,61,.04)]">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <span className="font-jakarta text-lg font-bold">Ventas mensuales 2026</span>
          <span className="inline-flex items-center gap-1.5 rounded-full border border-ambar bg-trigo px-3 py-[5px] text-[13px] font-semibold text-marino">
            <span className="size-[7px] rounded-full bg-ambar" />
            Datos de ejemplo
          </span>
        </div>

        <div className="grid grid-cols-[repeat(auto-fit,minmax(min(100%,220px),1fr))] gap-4">
          {CIFRAS.map((cifra) => (
            <div key={cifra.etiqueta} className="flex flex-col gap-1.5 rounded-[12px] bg-hueso px-5 py-[18px]">
              <span className="text-sm text-pizarra">{cifra.etiqueta}</span>
              <span className={`font-jakarta text-[28px] font-extrabold tracking-[-0.02em] ${cifra.color}`}>
                {cifra.valor}
              </span>
            </div>
          ))}
        </div>

        <Grafico />
      </div>
    </Franja>
  );
}

function Grafico() {
  return (
    <div className="flex flex-col gap-2.5">
      <div
        className="relative h-[clamp(180px,20cqi,280px)] border-b border-niebla"
        style={{
          backgroundImage:
            "repeating-linear-gradient(to top,#EEEBE3 0,#EEEBE3 1px,transparent 1px,transparent 25%)",
        }}
      >
        <div className="absolute inset-0 flex items-end">
          {MESES.map((mes, posicion) => (
            <div key={posicion} className="flex h-full flex-1 items-end justify-center">
              <div
                className={
                  mes.tipo === "pronostico"
                    ? "box-border w-[56%] rounded-t-[4px] border-[1.5px] border-b-0 border-dashed border-niebla"
                    : `w-[56%] rounded-t-[4px] ${mes.tipo === "actual" ? "bg-marino" : "bg-acero"}`
                }
                style={{ height: `${mes.alto}%` }}
              />
            </div>
          ))}
        </div>

        <svg
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          className="absolute inset-0 size-full overflow-visible"
          aria-hidden="true"
        >
          <polyline
            points={RECORRIDO.map((punto) => `${punto.x},${punto.y}`).join(" ")}
            fill="none"
            stroke="#1E7F53"
            strokeWidth="2.5"
            strokeDasharray="6 5"
            strokeLinecap="round"
            vectorEffect="non-scaling-stroke"
          />
        </svg>

        {/* El punto hueco es el mes en curso; el lleno, el final del pronóstico. */}
        <Punto x={RECORRIDO[0].x} alto={100 - RECORRIDO[0].y} hueco />
        <Punto x={RECORRIDO.at(-1)!.x} alto={100 - RECORRIDO.at(-1)!.y} />
      </div>

      <div className="flex text-center text-xs text-pizarra">
        {MESES.map((mes, posicion) => (
          <span key={posicion} className={`flex-1 ${mes.tipo === "actual" ? "font-bold text-marino" : ""}`}>
            {mes.letra}
          </span>
        ))}
      </div>

      <div className="mt-1.5 flex flex-wrap gap-5 text-[13px] text-pizarra">
        <span className="inline-flex items-center gap-2">
          <span className="size-3 rounded-[3px] bg-acero" />
          Ventas reales
        </span>
        <span className="inline-flex items-center gap-2">
          <svg width="22" height="4" aria-hidden="true">
            <path d="M1 2h20" stroke="#1E7F53" strokeWidth="2.5" strokeDasharray="5 4" strokeLinecap="round" />
          </svg>
          Pronóstico
        </span>
      </div>
    </div>
  );
}

function Punto({ x, alto, hueco = false }: { x: number; alto: number; hueco?: boolean }) {
  return (
    <span
      className={`absolute -mb-[5px] -ml-[5px] size-2.5 rounded-full ${
        hueco ? "box-border border-[2.5px] border-jade bg-white" : "bg-jade"
      }`}
      style={{ left: `${x}%`, bottom: `${alto}%` }}
    />
  );
}
