/*
 * Íconos dibujados en el mockup, copiados trazo por trazo.
 *
 * Los colores de trazo van literales porque los atributos de presentación de
 * SVG no leen variables CSS de forma confiable. Los íconos que cambian de color
 * con el hover (redes sociales) reciben su color por clase.
 */

const ORO = "#C9A227";
const LILA = "#A78BFA";
const TEXTO = "#F5F3F7";
const TEXTO_SUAVE = "#A09CAB";

type PropsIcono = {
  tamano?: number;
  className?: string;
};

export function IconoMarca({ tamano = 22, className }: PropsIcono) {
  return (
    <svg width={tamano} height={tamano} viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <path d="M12 3l4 4-4 4-4-4 4-4z" fill={ORO} />
      <circle cx="12" cy="16" r="4.5" stroke={LILA} strokeWidth="1.6" />
    </svg>
  );
}

export function IconoLupa({ tamano = 15, claro = false, className }: PropsIcono & { claro?: boolean }) {
  const color = claro ? TEXTO : TEXTO_SUAVE;
  return (
    <svg width={tamano} height={tamano} viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <circle cx="11" cy="11" r="7" stroke={color} strokeWidth="1.8" />
      <path d="M16.5 16.5L21 21" stroke={color} strokeWidth="1.8" />
    </svg>
  );
}

export function IconoBolsa({ tamano = 21, className }: PropsIcono) {
  return (
    <svg width={tamano} height={tamano} viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <path d="M6 8h12l-1.2 11H7.2L6 8z" stroke={TEXTO} strokeWidth="1.5" />
      <path d="M9 8V6.5a3 3 0 016 0V8" stroke={TEXTO} strokeWidth="1.5" />
    </svg>
  );
}

export function IconoFlechaAbajo({ className }: { className?: string }) {
  return (
    <svg width="10" height="10" viewBox="0 0 10 10" aria-hidden="true" className={className}>
      <path d="M1 3l4 4 4-4" stroke={LILA} strokeWidth="1.4" fill="none" />
    </svg>
  );
}

export function IconoInfo({ className }: { className?: string }) {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <circle cx="12" cy="12" r="9" stroke={ORO} strokeWidth="1.6" />
      <path d="M12 8v.5M12 11v5" stroke={ORO} strokeWidth="1.6" />
    </svg>
  );
}

const TRAZO_INSTAGRAM =
  "M7.5 2h9A5.5 5.5 0 0122 7.5v9A5.5 5.5 0 0116.5 22h-9A5.5 5.5 0 012 16.5v-9A5.5 5.5 0 017.5 2zm0 2A3.5 3.5 0 004 7.5v9A3.5 3.5 0 007.5 20h9a3.5 3.5 0 003.5-3.5v-9A3.5 3.5 0 0016.5 4h-9zM12 7a5 5 0 110 10 5 5 0 010-10zm0 2a3 3 0 100 6 3 3 0 000-6zm5.6-2.9a1.1 1.1 0 110 2.2 1.1 1.1 0 010-2.2z";

const TRAZO_WHATSAPP_CONTORNO =
  "M12 2a10 10 0 00-8.6 15.1L2 22l5-1.3A10 10 0 1012 2zm0 2a8 8 0 016.7 12.4l-.3.5.7 2.5-2.6-.7-.5.3A8 8 0 1112 4zm-3.3 4c-.3 0-.7.1-1 .5-.3.4-.8 1-.8 2 0 1.1.7 2.2 1 2.6.4.5 1.9 2.9 4.7 3.9 2.3.8 2.8.7 3.3.6.5-.1 1.6-.7 1.9-1.3.2-.7.2-1.2.2-1.3-.1-.2-.3-.2-.5-.3l-2-1c-.3-.1-.5-.1-.7.1l-.8 1c-.1.2-.3.2-.6.1-.3-.1-1.2-.5-2.2-1.4-.8-.7-1.3-1.5-1.5-1.8-.1-.3 0-.4.1-.6l.6-.7c.2-.2.2-.4.1-.6l-.8-2c-.1-.3-.3-.3-.5-.3h-.2z";

const TRAZO_WHATSAPP_SOLIDO =
  "M12 2a10 10 0 00-8.6 15.1L2 22l5-1.3A10 10 0 1012 2zm-3.3 6c-.3 0-.7.1-1 .5-.3.4-.8 1-.8 2 0 1.1.7 2.2 1 2.6.4.5 1.9 2.9 4.7 3.9 2.3.8 2.8.7 3.3.6.5-.1 1.6-.7 1.9-1.3.2-.7.2-1.2.2-1.3-.1-.2-.3-.2-.5-.3l-2-1c-.3-.1-.5-.1-.7.1l-.8 1c-.1.2-.3.2-.6.1-.3-.1-1.2-.5-2.2-1.4-.8-.7-1.3-1.5-1.5-1.8-.1-.3 0-.4.1-.6l.6-.7c.2-.2.2-.4.1-.6l-.8-2c-.1-.3-.3-.3-.5-.3h-.2z";

export function IconoInstagram({ tamano = 22, className }: PropsIcono) {
  return (
    <svg width={tamano} height={tamano} viewBox="0 0 24 24" aria-hidden="true" className={className}>
      <path d={TRAZO_INSTAGRAM} />
    </svg>
  );
}

export function IconoWhatsapp({ tamano = 22, solido = false, className }: PropsIcono & { solido?: boolean }) {
  return (
    <svg width={tamano} height={tamano} viewBox="0 0 24 24" aria-hidden="true" className={className}>
      <path d={solido ? TRAZO_WHATSAPP_SOLIDO : TRAZO_WHATSAPP_CONTORNO} />
    </svg>
  );
}

/**
 * Ícono de categoría. El mockup dibuja solo las cuatro categorías de Joyas Ye;
 * una categoría nueva se muestra sin ícono hasta que tenga uno diseñado.
 */
export function IconoCategoria({ slug, tamano, grosor }: { slug: string; tamano: number; grosor: number }) {
  const svg = { width: tamano, height: tamano, viewBox: "0 0 24 24", fill: "none", "aria-hidden": true } as const;

  switch (slug) {
    case "anillos":
      return (
        <svg {...svg}>
          <circle cx="12" cy="14" r="6.5" stroke={LILA} strokeWidth={grosor} />
          <path d="M12 3l3 3-3 3-3-3 3-3z" fill={ORO} />
        </svg>
      );
    case "collares":
      return (
        <svg {...svg}>
          <path d="M5 5c0 7 3 11 7 11s7-4 7-11" stroke={LILA} strokeWidth={grosor} />
          <circle cx="12" cy="18.5" r="2.6" fill={ORO} />
        </svg>
      );
    case "aros":
      return (
        <svg {...svg}>
          <circle cx="8" cy="5" r="1.6" fill={ORO} />
          <circle cx="16" cy="5" r="1.6" fill={ORO} />
          <path
            d="M8 8c3 3 3 8 0 11-3-3-3-8 0-11zM16 8c3 3 3 8 0 11-3-3-3-8 0-11z"
            stroke={LILA}
            strokeWidth={grosor - 0.2}
            fill="none"
          />
        </svg>
      );
    case "pulseras":
      return (
        <svg {...svg}>
          <ellipse cx="12" cy="12" rx="8.5" ry="6" stroke={LILA} strokeWidth={grosor} />
          <circle cx="12" cy="6" r="1.8" fill={ORO} />
        </svg>
      );
    default:
      return null;
  }
}
