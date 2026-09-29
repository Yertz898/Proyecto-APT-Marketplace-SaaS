/*
 * Campo de formulario de la portada.
 *
 * Es aparte del campo compartido del proyecto porque aquel está vestido con la
 * paleta oscura de la vitrina y este va sobre fondo claro. Comparten la forma
 * —etiqueta, ayuda, error asociado por aria— y no los colores.
 */

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
}) {
  const idAyuda = ayuda ? `${id}-ayuda` : undefined;
  const idError = error ? `${id}-error` : undefined;

  const clases = [
    "mt-2 w-full rounded-[12px] border bg-white px-4 text-base text-marino outline-none",
    multilinea ? "resize-none py-3" : "h-12",
    error ? "border-ambar" : "border-niebla focus-visible:border-acero",
  ].join(" ");

  const comunes = {
    id,
    value: valor,
    required: requerido,
    autoComplete,
    placeholder,
    "aria-invalid": Boolean(error),
    "aria-describedby": [idError, idAyuda].filter(Boolean).join(" ") || undefined,
    className: clases,
  };

  return (
    <div>
      <label htmlFor={id} className="text-[13px] font-semibold text-marino">
        {etiqueta}
        {!requerido && <span className="ml-1.5 font-normal text-pizarra">(opcional)</span>}
      </label>

      {multilinea ? (
        <textarea {...comunes} rows={4} onChange={(evento) => onCambio(evento.target.value)} />
      ) : (
        <input {...comunes} type={tipo} onChange={(evento) => onCambio(evento.target.value)} />
      )}

      {ayuda && !error && (
        <p id={idAyuda} className="mt-1.5 text-xs text-pizarra">
          {ayuda}
        </p>
      )}

      {error && (
        <p id={idError} className="mt-1.5 text-xs font-medium text-ambar-hondo">
          {error}
        </p>
      )}
    </div>
  );
}
