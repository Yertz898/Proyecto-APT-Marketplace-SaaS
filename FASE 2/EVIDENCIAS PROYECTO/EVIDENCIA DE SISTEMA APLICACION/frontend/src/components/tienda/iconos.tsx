/*
 * Íconos de la interfaz.
 *
 * Son de la plataforma, no de una tienda: acá no hay nada específico de un
 * rubro ni de un catálogo. El trazo va en `currentColor` y el color lo pone
 * quien los usa, con una clase: la vitrina tiene tema claro y oscuro, y un
 * color literal acá se volvía invisible en uno de los dos. `currentColor` sí se
 * resuelve de forma confiable en un atributo de presentación; una variable CSS
 * es la que no.
 */

type PropsIcono = {
  tamano?: number;
  className?: string;
};

export function IconoLupa({ tamano = 15, className }: PropsIcono) {
  return (
    <svg width={tamano} height={tamano} viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="1.8" />
      <path d="M16.5 16.5L21 21" stroke="currentColor" strokeWidth="1.8" />
    </svg>
  );
}

export function IconoBolsa({ tamano = 21, className }: PropsIcono) {
  return (
    <svg width={tamano} height={tamano} viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <path d="M6 8h12l-1.2 11H7.2L6 8z" stroke="currentColor" strokeWidth="1.5" />
      <path d="M9 8V6.5a3 3 0 016 0V8" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

/** Sol y luna del interruptor de tema. Se dibuja el destino, no el estado. */
export function IconoSol({ tamano = 17, className }: PropsIcono) {
  return (
    <svg width={tamano} height={tamano} viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <circle cx="12" cy="12" r="4.2" stroke="currentColor" strokeWidth="1.7" />
      <path
        d="M12 2.4v2.3M12 19.3v2.3M4.4 4.4l1.7 1.7M17.9 17.9l1.7 1.7M2.4 12h2.3M19.3 12h2.3M4.4 19.6l1.7-1.7M17.9 6.1l1.7-1.7"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function IconoLuna({ tamano = 17, className }: PropsIcono) {
  return (
    <svg width={tamano} height={tamano} viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <path
        d="M20 14.2A8.4 8.4 0 019.8 4a8.6 8.6 0 102.6 16.8 8.6 8.6 0 007.6-6.6z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
    </svg>
  );
}

const TRAZO_INSTAGRAM =
  "M7.5 2h9A5.5 5.5 0 0122 7.5v9A5.5 5.5 0 0116.5 22h-9A5.5 5.5 0 012 16.5v-9A5.5 5.5 0 017.5 2zm0 2A3.5 3.5 0 004 7.5v9A3.5 3.5 0 007.5 20h9a3.5 3.5 0 003.5-3.5v-9A3.5 3.5 0 0016.5 4h-9zM12 7a5 5 0 110 10 5 5 0 010-10zm0 2a3 3 0 100 6 3 3 0 000-6zm5.6-2.9a1.1 1.1 0 110 2.2 1.1 1.1 0 010-2.2z";

const TRAZO_WHATSAPP =
  "M12 2a10 10 0 00-8.6 15.1L2 22l5-1.3A10 10 0 1012 2zm0 2a8 8 0 016.7 12.4l-.3.5.7 2.5-2.6-.7-.5.3A8 8 0 1112 4zm-3.3 4c-.3 0-.7.1-1 .5-.3.4-.8 1-.8 2 0 1.1.7 2.2 1 2.6.4.5 1.9 2.9 4.7 3.9 2.3.8 2.8.7 3.3.6.5-.1 1.6-.7 1.9-1.3.2-.7.2-1.2.2-1.3-.1-.2-.3-.2-.5-.3l-2-1c-.3-.1-.5-.1-.7.1l-.8 1c-.1.2-.3.2-.6.1-.3-.1-1.2-.5-2.2-1.4-.8-.7-1.3-1.5-1.5-1.8-.1-.3 0-.4.1-.6l.6-.7c.2-.2.2-.4.1-.6l-.8-2c-.1-.3-.3-.3-.5-.3h-.2z";

export function IconoInstagram({ tamano = 22, className }: PropsIcono) {
  return (
    <svg width={tamano} height={tamano} viewBox="0 0 24 24" aria-hidden="true" className={className}>
      <path d={TRAZO_INSTAGRAM} />
    </svg>
  );
}

export function IconoWhatsapp({ tamano = 22, className }: PropsIcono) {
  return (
    <svg width={tamano} height={tamano} viewBox="0 0 24 24" aria-hidden="true" className={className}>
      <path d={TRAZO_WHATSAPP} />
    </svg>
  );
}

/**
 * Flecha de navegación.
 *
 * Usa `currentColor` en vez de un color literal porque tiene que apagarse junto
 * con el texto cuando el paso no lleva a ninguna parte. `currentColor` sí se
 * resuelve de forma confiable en un atributo de presentación; una variable CSS
 * es la que no.
 */
export function IconoFlecha({
  tamano = 13,
  sentido,
  className,
}: PropsIcono & { sentido: "izquierda" | "derecha" }) {
  return (
    <svg
      width={tamano}
      height={tamano}
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
      className={className}
      style={sentido === "derecha" ? { transform: "rotate(180deg)" } : undefined}
    >
      <path
        d="M15 5l-7 7 7 7"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
