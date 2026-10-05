import type { ReactNode } from "react";

import type { Plan, Rol } from "@/lib/tipos";

/*
 * Las secciones del panel, en un solo lugar.
 *
 * Están acá como datos y no repartidas por el menú porque tres cosas distintas
 * las leen: la barra lateral para dibujarlas, el guardia para decidir si se
 * entra, y cada pantalla para saber si sus datos son reales o de ejemplo.
 *
 * Lo que esta lista NO hace es proteger nada. El candado y el ocultamiento son
 * cortesía: quien decide es el backend en cada endpoint. Un plan o un rol
 * cambiados en el navegador no abren ninguna sección.
 */

/**
 * En qué está cada sección.
 *
 * - `real`: lee y escribe contra la API.
 * - `demostracion`: la pantalla está terminada y los datos vienen de un
 *   proveedor de ejemplo. Siempre lo dice en pantalla.
 * - `proximamente`: ni siquiera eso. Se anuncia y no se entra.
 */
export type EstadoDeSeccion = "real" | "demostracion" | "proximamente";

export type Seccion = {
  href: string;
  etiqueta: string;
  descripcion: string;
  grupo: string;
  estado: EstadoDeSeccion;
  /** Plan mínimo que la habilita. */
  plan: Plan;
  /** Qué puede hacer un vendedor. El dueño siempre puede todo. */
  vendedor: "completo" | "lectura" | "no";
  icono: ReactNode;
};

/** Orden de los planes, de menor a mayor. */
const ESCALERA: Plan[] = ["basico", "premium", "ultimate"];

export function planAlcanza(plan: Plan | undefined, minimo: Plan): boolean {
  if (!plan) return false;
  return ESCALERA.indexOf(plan) >= ESCALERA.indexOf(minimo);
}

export const NOMBRE_DEL_PLAN: Record<Plan, string> = {
  basico: "Básico",
  premium: "Premium",
  ultimate: "Ultimate",
};

/** Si el rol puede siquiera ver la sección en el menú. */
export function rolAlcanza(rol: Rol | undefined, seccion: Seccion): boolean {
  if (rol === "dueno_tienda") return true;
  if (rol === "vendedor") return seccion.vendedor !== "no";
  return false;
}

const trazo = {
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.7,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
};

function Icono({ children }: { children: ReactNode }) {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" {...trazo}>
      {children}
    </svg>
  );
}

export const SECCIONES: Seccion[] = [
  {
    href: "/panel",
    etiqueta: "Inicio",
    descripcion: "Lo que necesita tu atención hoy.",
    grupo: "",
    estado: "real",
    plan: "basico",
    vendedor: "completo",
    icono: (
      <Icono>
        <path d="M3 10.5L12 3l9 7.5" />
        <path d="M5 9.5V20h14V9.5" />
      </Icono>
    ),
  },

  // ── Catálogo ──────────────────────────────────────────────────────────────
  {
    href: "/panel/catalogo",
    etiqueta: "Catálogo",
    descripcion: "Tus productos, su precio y su inventario.",
    grupo: "Catálogo",
    estado: "real",
    plan: "basico",
    vendedor: "completo",
    icono: (
      <Icono>
        <path d="M3 7.5L12 3l9 4.5-9 4.5-9-4.5z" />
        <path d="M3 7.5v9L12 21l9-4.5v-9" />
      </Icono>
    ),
  },
  {
    href: "/panel/precios",
    etiqueta: "Precios",
    descripcion: "Los tramos de precio por volumen de cada producto.",
    grupo: "Catálogo",
    estado: "real",
    plan: "basico",
    vendedor: "completo",
    icono: (
      <Icono>
        <path d="M3 20h4v-5h5v-5h5V5h4" />
      </Icono>
    ),
  },
  {
    href: "/panel/cargas",
    etiqueta: "Carga masiva",
    descripcion: "Sube tu catálogo desde una planilla.",
    grupo: "Catálogo",
    estado: "real",
    plan: "basico",
    vendedor: "completo",
    icono: (
      <Icono>
        <path d="M12 16V4M8 8l4-4 4 4" />
        <path d="M4 16v3a1 1 0 001 1h14a1 1 0 001-1v-3" />
      </Icono>
    ),
  },

  // ── Ventas ────────────────────────────────────────────────────────────────
  {
    href: "/panel/pedidos",
    etiqueta: "Pedidos",
    descripcion: "Qué te pidieron y en qué va cada uno.",
    grupo: "Ventas",
    estado: "demostracion",
    plan: "basico",
    vendedor: "completo",
    icono: (
      <Icono>
        <path d="M6 8h12l-1.2 11H7.2L6 8z" />
        <path d="M9 8V6a3 3 0 016 0v2" />
      </Icono>
    ),
  },
  {
    href: "/panel/ventas",
    etiqueta: "Panel de ventas",
    descripcion: "Cómo va el mes comparado con el anterior.",
    grupo: "Ventas",
    estado: "demostracion",
    plan: "premium",
    vendedor: "completo",
    icono: (
      <Icono>
        <path d="M3 21h18" />
        <path d="M6 18v-6M12 18V7M18 18v-9" />
      </Icono>
    ),
  },

  // ── Inteligencia ──────────────────────────────────────────────────────────
  {
    href: "/panel/pronostico",
    etiqueta: "Pronóstico",
    descripcion: "Qué va a pedirte el próximo mes, y qué se te puede acabar.",
    grupo: "Inteligencia",
    estado: "demostracion",
    plan: "ultimate",
    vendedor: "completo",
    icono: (
      <Icono>
        <path d="M3 18l5-5 4 3 3-4" />
        <path d="M15 12l6-7" strokeDasharray="2 2.5" />
      </Icono>
    ),
  },
  {
    href: "/panel/segmentos",
    etiqueta: "Segmentos",
    descripcion: "Quiénes compran seguido y quiénes se están yendo.",
    grupo: "Inteligencia",
    estado: "demostracion",
    plan: "ultimate",
    vendedor: "completo",
    icono: (
      <Icono>
        <circle cx="9" cy="8" r="3.2" />
        <path d="M3 20c0-3.3 2.7-5 6-5s6 1.7 6 5" />
        <path d="M16 6.2a3.2 3.2 0 010 6M18 20c0-2.6-1-4.2-2.5-5" />
      </Icono>
    ),
  },
  {
    href: "/panel/asistente",
    etiqueta: "Asistente",
    descripcion: "Pregúntale por tus ventas.",
    grupo: "Inteligencia",
    estado: "demostracion",
    plan: "ultimate",
    vendedor: "completo",
    icono: (
      <Icono>
        <path d="M4 19V6a2 2 0 012-2h12a2 2 0 012 2v8a2 2 0 01-2 2H8l-4 3z" />
        <path d="M9 10h.01M12 10h.01M15 10h.01" />
      </Icono>
    ),
  },

  // ── Configuración ─────────────────────────────────────────────────────────
  {
    href: "/panel/tienda",
    etiqueta: "Tienda y marca",
    descripcion: "Tu logo, tus colores y tu tipografía.",
    grupo: "Configuración",
    estado: "real",
    plan: "basico",
    vendedor: "lectura",
    icono: (
      <Icono>
        <path d="M4 9l1.5-5h13L20 9" />
        <path d="M4 9h16v10a1 1 0 01-1 1H5a1 1 0 01-1-1z" />
        <path d="M9 20v-6h6v6" />
      </Icono>
    ),
  },
  {
    href: "/panel/equipo",
    etiqueta: "Equipo",
    descripcion: "Quién más atiende tu tienda.",
    grupo: "Configuración",
    estado: "real",
    plan: "premium",
    vendedor: "no",
    icono: (
      <Icono>
        <circle cx="12" cy="8" r="3.4" />
        <path d="M5 20c0-3.6 3-6 7-6s7 2.4 7 6" />
      </Icono>
    ),
  },
  {
    href: "/panel/plan",
    etiqueta: "Plan",
    descripcion: "Qué incluye tu suscripción.",
    grupo: "Configuración",
    estado: "real",
    plan: "basico",
    vendedor: "no",
    icono: (
      <Icono>
        <rect x="3" y="6" width="18" height="13" rx="2" />
        <path d="M3 10h18M7 15h4" />
      </Icono>
    ),
  },
  {
    href: "/panel/agenda",
    etiqueta: "Agenda",
    descripcion: "Visitas con hora a tu tienda.",
    grupo: "Configuración",
    estado: "proximamente",
    plan: "premium",
    vendedor: "completo",
    icono: (
      <Icono>
        <rect x="3" y="5" width="18" height="16" rx="2" />
        <path d="M3 10h18M8 3v4M16 3v4" />
      </Icono>
    ),
  },
  {
    href: "/panel/cuenta",
    etiqueta: "Cuenta",
    descripcion: "Tu contraseña y tu sesión.",
    grupo: "Configuración",
    estado: "real",
    plan: "basico",
    vendedor: "completo",
    icono: (
      <Icono>
        <circle cx="12" cy="12" r="9" />
        <circle cx="12" cy="10" r="3" />
        <path d="M6.5 19a6 6 0 0111 0" />
      </Icono>
    ),
  },
];

/** Las secciones agrupadas y en orden, como las dibuja la barra lateral. */
export function porGrupo(): [string, Seccion[]][] {
  const grupos = new Map<string, Seccion[]>();
  for (const seccion of SECCIONES) {
    const lista = grupos.get(seccion.grupo);
    if (lista) lista.push(seccion);
    else grupos.set(seccion.grupo, [seccion]);
  }
  return [...grupos.entries()];
}

export function seccionDe(ruta: string): Seccion | undefined {
  // La más específica primero: /panel calza con todo si se compara al revés.
  return [...SECCIONES]
    .sort((a, b) => b.href.length - a.href.length)
    .find((s) => ruta === s.href || ruta.startsWith(`${s.href}/`));
}
