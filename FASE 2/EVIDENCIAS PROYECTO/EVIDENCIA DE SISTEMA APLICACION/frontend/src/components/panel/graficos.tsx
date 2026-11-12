"use client";

import { useId, useState, type ReactNode } from "react";

import { cn } from "@/lib/utils";

/*
 * Los gráficos del panel, dibujados a mano en SVG.
 *
 * Sin librería de gráficos, y no por ahorrar una dependencia: las reglas que
 * siguen estos dibujos —2 px de superficie separando marcas que se tocan, el
 * extremo del dato redondeado y la base cuadrada, un anillo del color del
 * fondo alrededor de cada punto— son exactamente lo que una librería genérica
 * hace difícil. Son también lo que hace que se lean.
 *
 * Tres reglas que no se negocian acá:
 *
 * - **El texto nunca usa el color de la serie.** Las marcas llevan el color;
 *   las etiquetas, los valores y los ejes usan los tonos de texto. Un amarillo
 *   que funciona como barra es ilegible como palabra.
 * - **No se etiqueta cada punto.** Se etiqueta el extremo o el máximo. Una
 *   cifra sobre cada dato deja de leerse.
 * - **Todo valor que muestra un tooltip está también sin pasar el mouse**, en
 *   la tabla que acompaña a cada gráfico. El hover agrega comodidad, nunca es
 *   la única forma de llegar a un número.
 */

/**
 * Los colores de serie, en orden fijo.
 *
 * Validados con el script de la guía de visualización sobre los dos fondos
 * del panel: banda de luminosidad, piso de croma, separación bajo daltonismo
 * (protanopia y deuteranopia) y contraste contra la superficie. El par más
 * cercano queda en ΔE 14,7 simulado y 15,9 a vista normal.
 *
 * El orden no se altera y no se recicla: una cuarta serie toma el cuarto
 * color, nunca uno repetido. Si hicieran falta más de cuatro, la respuesta es
 * agrupar el resto en «otros», no inventar un color nuevo.
 */
export const SERIE = ["#2a6ea8", "#1e7f53", "#b57f10", "#7c3aed"] as const;

/**
 * El gris de lo que está ahí pero no pide atención.
 *
 * No es un color de serie: es lo contrario. Marca lo inactivo —un cliente
 * perdido, un mes todavía sin cerrar— para que la vista se vaya a lo que sí
 * se puede hacer algo.
 */
export const ATENUADO = "#8b93a1";

/** El color del fondo de las tarjetas. Las separaciones se pintan con él. */
const SUPERFICIE = "#ffffff";

const REJILLA = "#e3e0d6";

// ── Piezas compartidas ──────────────────────────────────────────────────────

/**
 * El caparazón de un gráfico: título, el dibujo y su tabla.
 *
 * La tabla no es un extra de accesibilidad colgado al final: es la forma de
 * leer los valores sin pasar el mouse, y por eso vive al lado del gráfico y
 * no en otra pantalla.
 */
export function Grafico({
  titulo,
  detalle,
  leyenda,
  children,
  tabla,
}: {
  titulo: string;
  detalle?: string;
  leyenda?: ReactNode;
  children: ReactNode;
  tabla: { columnas: string[]; filas: (string | number)[][] };
}) {
  const [verTabla, setVerTabla] = useState(false);
  const id = useId();

  return (
    <section>
      <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
        <h2 className="text-[13px] font-semibold text-marino">{titulo}</h2>
        <button
          type="button"
          aria-expanded={verTabla}
          aria-controls={id}
          onClick={() => setVerTabla((previo) => !previo)}
          className="cursor-pointer text-xs text-pizarra underline decoration-arena-honda underline-offset-2 hover:text-acero"
        >
          {verTabla ? "Ver el gráfico" : "Ver los números"}
        </button>
      </div>

      {detalle && <p className="mt-1 text-xs leading-[1.5] text-pizarra">{detalle}</p>}
      {leyenda && <div className="mt-2.5">{leyenda}</div>}

      <div id={id} className="mt-3">
        {verTabla ? <Tabla {...tabla} /> : children}
      </div>
    </section>
  );
}

function Tabla({
  columnas,
  filas,
}: {
  columnas: string[];
  filas: (string | number)[][];
}) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-[13px]">
        <thead>
          <tr className="border-b border-arena text-left">
            {columnas.map((columna, i) => (
              <th
                key={columna}
                scope="col"
                className={cn(
                  "py-1.5 pr-3 font-semibold text-marino",
                  i > 0 && "text-right",
                )}
              >
                {columna}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {filas.map((fila) => (
            <tr key={String(fila[0])} className="border-b border-arena/60 last:border-0">
              {fila.map((celda, i) => (
                <td
                  key={`${fila[0]}-${columnas[i]}`}
                  className={cn("py-1.5 pr-3 text-pizarra", i > 0 && "text-right")}
                >
                  {celda}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/** La leyenda. Obligatoria desde dos series; con una sobra, la basta el título. */
export function Leyenda({
  entradas,
  forma = "linea",
}: {
  entradas: { nombre: string; color: string }[];
  forma?: "linea" | "caja";
}) {
  return (
    <ul className="flex flex-wrap gap-x-4 gap-y-1.5">
      {entradas.map(({ nombre, color }) => (
        <li key={nombre} className="flex items-center gap-1.5 text-xs text-pizarra">
          <span
            aria-hidden="true"
            style={{ background: color }}
            className={cn(
              "block shrink-0",
              forma === "linea" ? "h-[2px] w-4 rounded-full" : "size-2.5 rounded-[3px]",
            )}
          />
          {nombre}
        </li>
      ))}
    </ul>
  );
}

/** El globo que sigue al puntero. Se posiciona en porcentaje del ancho. */
function Globo({
  x,
  children,
}: {
  /** Posición horizontal, de 0 a 1. */
  x: number;
  children: ReactNode;
}) {
  // Pegado al borde cuando está cerca, para que no se salga de la tarjeta.
  const alineacion = x > 0.66 ? "translate(-100%, 0)" : x < 0.33 ? "none" : "translate(-50%, 0)";

  return (
    <div
      role="status"
      style={{ left: `${x * 100}%`, transform: alineacion }}
      className="pointer-events-none absolute top-0 z-10 min-w-max rounded-[10px] border border-arena bg-white px-2.5 py-2 text-[11px] leading-[1.5] shadow-[0_6px_18px_rgba(20,33,61,0.12)]"
    >
      {children}
    </div>
  );
}

// ── Línea de tiempo ─────────────────────────────────────────────────────────

export type PuntoDeSerie = { etiqueta: string; valor: number; atenuado?: boolean };

const ANCHO = 720;
const ALTO = 210;
const ALTO_COMPACTO = 140;
const MARGEN = { arriba: 14, derecha: 14, abajo: 26, izquierda: 60 };

/**
 * Una o varias series en el tiempo.
 *
 * Con una sola serie se pinta además el relleno al 10%, que ayuda a leer el
 * volumen sin agregar tinta. Con varias no: los rellenos se taparían entre sí.
 *
 * Un punto `atenuado` —el mes en curso— se dibuja hueco y con el tramo que
 * llega hasta él punteado. Va por la mitad, así que su valor siempre es menor
 * que el de un mes cerrado; unirlo con línea llena lo haría parecer un
 * desplome.
 */
export function LineaDeTiempo({
  series,
  formatear,
  compacta = false,
  tope: topeImpuesto,
}: {
  series: { nombre: string; color: string; puntos: PuntoDeSerie[] }[];
  formatear: (valor: number) => string;
  /** Más bajo, para cuando van varios apilados. */
  compacta?: boolean;
  /**
   * Fuerza el tope del eje.
   *
   * Es lo que hace comparables a varios gráficos pequeños puestos uno sobre
   * otro: con cada uno a su propia escala, el que vende la décima parte se
   * dibuja igual de alto y el lector concluye lo contrario de lo que pasa.
   */
  tope?: number;
}) {
  const [activo, setActivo] = useState<number | null>(null);
  const puntos = series[0]?.puntos ?? [];

  if (puntos.length === 0) {
    return <p className="py-6 text-center text-[13px] text-pizarra">Sin datos.</p>;
  }

  const maximo = Math.max(...series.flatMap((s) => s.puntos.map((p) => p.valor)), 1);
  const tope = topeImpuesto ?? techoRedondo(maximo);
  const altoTotal = compacta ? ALTO_COMPACTO : ALTO;
  const ancho = ANCHO - MARGEN.izquierda - MARGEN.derecha;
  const alto = altoTotal - MARGEN.arriba - MARGEN.abajo;

  const x = (i: number) =>
    MARGEN.izquierda + (puntos.length === 1 ? ancho / 2 : (i * ancho) / (puntos.length - 1));
  const y = (valor: number) => MARGEN.arriba + alto - (valor / tope) * alto;

  // Menos marcas en el compacto: cinco líneas en 140 px de alto son una
  // trama, no una rejilla.
  const marcas = (compacta ? [0, 0.5, 1] : [0, 0.25, 0.5, 0.75, 1]).map(
    (f) => f * tope,
  );

  return (
    <div
      className="relative"
      onPointerLeave={() => setActivo(null)}
      onPointerMove={(evento) => {
        const caja = evento.currentTarget.getBoundingClientRect();
        const fraccion =
          (evento.clientX - caja.left) / caja.width -
          MARGEN.izquierda / ANCHO;
        const util = ancho / ANCHO;
        const indice = Math.round((fraccion / util) * (puntos.length - 1));
        setActivo(Math.min(Math.max(indice, 0), puntos.length - 1));
      }}
    >
      <svg
        viewBox={`0 0 ${ANCHO} ${altoTotal}`}
        className="w-full"
        role="img"
        aria-label={`Gráfico de ${series.map((s) => s.nombre).join(", ")}`}
      >
        {marcas.map((marca) => (
          <g key={marca}>
            <line
              x1={MARGEN.izquierda}
              x2={ANCHO - MARGEN.derecha}
              y1={y(marca)}
              y2={y(marca)}
              stroke={REJILLA}
              strokeWidth={1}
            />
            <text
              x={MARGEN.izquierda - 8}
              y={y(marca) + 4}
              textAnchor="end"
              className="fill-pizarra text-[11px]"
            >
              {compacto(marca)}
            </text>
          </g>
        ))}

        {puntos.map((punto, i) =>
          i % Math.ceil(puntos.length / 8) === 0 || i === puntos.length - 1 ? (
            <text
              key={punto.etiqueta}
              x={x(i)}
              y={altoTotal - 8}
              // La primera y la ultima se anclan hacia adentro: centradas se
              // salen del dibujo y el navegador les corta la mitad.
              textAnchor={
                i === 0 ? "start" : i === puntos.length - 1 ? "end" : "middle"
              }
              className="fill-pizarra text-[11px]"
            >
              {punto.etiqueta}
            </text>
          ) : null,
        )}

        {activo !== null && (
          <line
            x1={x(activo)}
            x2={x(activo)}
            y1={MARGEN.arriba}
            y2={MARGEN.arriba + alto}
            stroke={ATENUADO}
            strokeWidth={1}
          />
        )}

        {series.map((serie) => {
          const cerrados = serie.puntos.filter((p) => !p.atenuado);
          const trazo = cerrados.map((p, i) => `${i === 0 ? "M" : "L"}${x(i)},${y(p.valor)}`).join(" ");

          return (
            <g key={serie.nombre}>
              {series.length === 1 && cerrados.length > 1 && (
                <path
                  d={`${trazo} L${x(cerrados.length - 1)},${y(0)} L${x(0)},${y(0)} Z`}
                  fill={serie.color}
                  opacity={0.1}
                />
              )}
              <path
                d={trazo}
                fill="none"
                stroke={serie.color}
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              {serie.puntos.map((punto, i) =>
                punto.atenuado ? (
                  <g key={punto.etiqueta}>
                    <line
                      x1={x(i - 1)}
                      y1={y(serie.puntos[i - 1]?.valor ?? 0)}
                      x2={x(i)}
                      y2={y(punto.valor)}
                      stroke={ATENUADO}
                      strokeWidth={2}
                      strokeDasharray="3 4"
                      strokeLinecap="round"
                    />
                    <circle
                      cx={x(i)}
                      cy={y(punto.valor)}
                      r={4}
                      fill={SUPERFICIE}
                      stroke={ATENUADO}
                      strokeWidth={2}
                    />
                  </g>
                ) : null,
              )}
              {activo !== null && !serie.puntos[activo]?.atenuado && (
                <circle
                  cx={x(activo)}
                  cy={y(serie.puntos[activo]?.valor ?? 0)}
                  r={4.5}
                  fill={serie.color}
                  stroke={SUPERFICIE}
                  strokeWidth={2}
                />
              )}
            </g>
          );
        })}
      </svg>

      {activo !== null && (
        <Globo x={x(activo) / ANCHO}>
          <p className="font-semibold text-marino">{puntos[activo]?.etiqueta}</p>
          {series.map((serie) => (
            <p key={serie.nombre} className="mt-1 flex items-center gap-1.5">
              <span
                aria-hidden="true"
                style={{ background: serie.color }}
                className="block h-[2px] w-3 shrink-0 rounded-full"
              />
              <span className="font-semibold text-marino">
                {formatear(serie.puntos[activo]?.valor ?? 0)}
              </span>
              {series.length > 1 && <span className="text-pizarra">{serie.nombre}</span>}
            </p>
          ))}
          {puntos[activo]?.atenuado && (
            <p className="mt-1 text-pizarra">El mes todavía va por la mitad.</p>
          )}
        </Globo>
      )}
    </div>
  );
}

// ── Barras ranqueadas ───────────────────────────────────────────────────────

/**
 * Barras horizontales, de mayor a menor, todas del mismo color.
 *
 * Del mismo color a propósito: el largo ya dice cuánto, y pintarlas distinto
 * gastaría el canal de la identidad en repetir lo que la barra muestra.
 */
export function BarrasRanqueadas({
  filas,
  formatear,
  color = SERIE[0],
}: {
  filas: { nombre: string; valor: number; detalle?: string }[];
  formatear: (valor: number) => string;
  color?: string;
}) {
  const [activa, setActiva] = useState<string | null>(null);
  const maximo = Math.max(...filas.map((f) => f.valor), 1);

  return (
    <ul className="flex flex-col gap-2.5">
      {filas.map((fila) => (
        <li
          key={fila.nombre}
          onPointerEnter={() => setActiva(fila.nombre)}
          onPointerLeave={() => setActiva(null)}
          onFocus={() => setActiva(fila.nombre)}
          onBlur={() => setActiva(null)}
          tabIndex={0}
          className="cursor-default rounded-[6px] outline-none focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-acero"
        >
          <div className="flex items-baseline justify-between gap-4">
            <span className="min-w-0 truncate text-[13px] text-marino">{fila.nombre}</span>
            <span className="shrink-0 text-[13px] font-semibold text-marino">
              {formatear(fila.valor)}
            </span>
          </div>

          <div className="mt-1 flex items-center gap-2.5">
            <span className="h-2.5 min-w-0 flex-1 overflow-hidden rounded-[2px] bg-lino">
              <span
                style={{
                  width: `${Math.max((fila.valor / maximo) * 100, 1.5)}%`,
                  background: color,
                  opacity: activa === null || activa === fila.nombre ? 1 : 0.55,
                }}
                className="block h-full rounded-l-[2px] rounded-r-[4px] transition-opacity"
              />
            </span>
            {fila.detalle && (
              <span className="shrink-0 text-xs text-pizarra">{fila.detalle}</span>
            )}
          </div>
        </li>
      ))}
    </ul>
  );
}

// ── Barra segmentada ────────────────────────────────────────────────────────

/**
 * Una sola barra dividida en sus partes, sin cifras encima.
 *
 * Va sobre una lista que ya da el nombre y el número de cada parte, así que
 * imprimirlos otra vez en la barra no agrega nada. Lo que la barra aporta es
 * la proporción, que en una lista de números no se ve.
 *
 * Los 2 px que separan los bloques son del color del fondo, no un borde: un
 * trazo alrededor de cada parte agregaría tinta que no es dato.
 */
export function BarraSegmentada({
  partes,
}: {
  partes: { nombre: string; valor: number; color: string }[];
}) {
  const [activa, setActiva] = useState<string | null>(null);
  const total = partes.reduce((suma, parte) => suma + parte.valor, 0);

  if (total === 0) {
    return null;
  }

  return (
    <div className="relative">
      <div className="flex h-3 w-full gap-[2px] overflow-hidden">
        {partes
          .filter((parte) => parte.valor > 0)
          .map((parte) => (
            <button
              key={parte.nombre}
              type="button"
              aria-label={`${parte.nombre}: ${parte.valor} de ${total}`}
              onPointerEnter={() => setActiva(parte.nombre)}
              onPointerLeave={() => setActiva(null)}
              onFocus={() => setActiva(parte.nombre)}
              onBlur={() => setActiva(null)}
              style={{
                width: `${(parte.valor / total) * 100}%`,
                background: parte.color,
                opacity: activa === null || activa === parte.nombre ? 1 : 0.55,
              }}
              className="h-full cursor-default rounded-[2px] transition-opacity first:rounded-l-[4px] last:rounded-r-[4px] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-acero"
            />
          ))}
      </div>

      {activa && (
        <p className="mt-2 text-xs text-pizarra">
          <span className="font-semibold text-marino">
            {partes.find((p) => p.nombre === activa)?.valor}
          </span>{" "}
          {activa.toLowerCase()} ·{" "}
          {Math.round(
            ((partes.find((p) => p.nombre === activa)?.valor ?? 0) / total) * 100,
          )}
          % del total
        </p>
      )}
    </div>
  );
}

// ── Auxiliares ──────────────────────────────────────────────────────────────

/** El tope del eje, redondeado hacia arriba a una cifra que se lea. */
function techoRedondo(maximo: number): number {
  const magnitud = 10 ** Math.floor(Math.log10(maximo));
  return Math.ceil(maximo / (magnitud / 2)) * (magnitud / 2);
}

/**
 * Las marcas del eje: completas bajo diez mil, compactas sobre eso.
 *
 * Con coma decimal, que es la chilena. Un «11.3M» se lee como once millones
 * trescientos mil acá, que es justo lo contrario de lo que dice.
 */
function compacto(valor: number): string {
  if (valor === 0) return "0";
  if (valor >= 1_000_000) {
    return `${(Math.round(valor / 100_000) / 10).toLocaleString("es-CL")}M`;
  }
  if (valor >= 1_000) return `${Math.round(valor / 1_000)}K`;
  return String(Math.round(valor));
}
