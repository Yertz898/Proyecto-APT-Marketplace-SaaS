import { cn } from "@/lib/utils";

/*
 * Campo de formulario, compartido por todo el proyecto.
 *
 * Sirve a dos paletas porque el sistema tiene dos caras: DealCommerce es claro
 * y la vitrina de cada tienda se ve como esa tienda quiera, que hoy es oscura.
 * Lo que comparten es la forma —etiqueta, ayuda, error asociado por aria— y no
 * los colores. No es de shadcn, por eso no vive en components/ui.
 */

export type TemaDeFormulario = "claro" | "oscuro";

const PALETA = {
  claro: {
    etiqueta: "text-marino",
    opcional: "text-pizarra",
    campo: "bg-white text-marino",
    normal: "border-niebla focus-visible:border-acero",
    conError: "border-ambar",
    ayuda: "text-pizarra",
    error: "text-ambar-hondo",
  },
  oscuro: {
    etiqueta: "text-texto",
    opcional: "text-texto-suave",
    campo: "bg-superficie text-texto",
    normal: "border-lila/20 focus-visible:border-lila",
    // El oro es el color que la vitrina ya usa para lo que hay que revisar.
    conError: "border-oro/70",
    ayuda: "text-texto-suave",
    error: "text-oro",
  },
} as const;

/** Un campo con su etiqueta y el error que le corresponde. */
export function Campo({
  id,
  etiqueta,
  tipo = "text",
  valor,
  onCambio,
  error,
  ayuda,
  requerido = true,
  autoComplete,
  multilinea = false,
  placeholder,
  tema = "oscuro",
}: {
  id: string;
  etiqueta: string;
  tipo?: string;
  valor: string;
  onCambio: (valor: string) => void;
  error?: string | null;
  ayuda?: string;
  requerido?: boolean;
  autoComplete?: string;
  multilinea?: boolean;
  placeholder?: string;
  tema?: TemaDeFormulario;
}) {
  const color = PALETA[tema];
  const idAyuda = ayuda ? `${id}-ayuda` : undefined;
  const idError = error ? `${id}-error` : undefined;

  const comunes = {
    id,
    value: valor,
    required: requerido,
    autoComplete,
    placeholder,
    "aria-invalid": Boolean(error),
    "aria-describedby": [idError, idAyuda].filter(Boolean).join(" ") || undefined,
    className: cn(
      "mt-2 w-full rounded-[12px] border px-4 text-base outline-none",
      color.campo,
      multilinea ? "resize-none py-3" : "h-12",
      error ? color.conError : color.normal,
    ),
  };

  return (
    <div>
      <label htmlFor={id} className={cn("text-[13px] font-semibold", color.etiqueta)}>
        {etiqueta}
        {!requerido && <span className={cn("ml-1.5 font-normal", color.opcional)}>(opcional)</span>}
      </label>

      {multilinea ? (
        <textarea {...comunes} rows={4} onChange={(evento) => onCambio(evento.target.value)} />
      ) : (
        <input {...comunes} type={tipo} onChange={(evento) => onCambio(evento.target.value)} />
      )}

      {ayuda && !error && (
        <p id={idAyuda} className={cn("mt-1.5 text-xs", color.ayuda)}>
          {ayuda}
        </p>
      )}

      {error && (
        <p id={idError} className={cn("mt-1.5 text-xs font-medium", color.error)}>
          {error}
        </p>
      )}
    </div>
  );
}
