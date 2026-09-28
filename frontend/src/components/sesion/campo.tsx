import { cn } from "@/lib/utils";

/** Campo de texto con su etiqueta y el error que le corresponde. */
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
}) {
  const idAyuda = ayuda ? `${id}-ayuda` : undefined;
  const idError = error ? `${id}-error` : undefined;

  return (
    <div>
      <label htmlFor={id} className="text-[13px] font-semibold text-texto">
        {etiqueta}
        {!requerido && <span className="ml-1.5 font-normal text-texto-suave">(opcional)</span>}
      </label>

      <input
        id={id}
        type={tipo}
        value={valor}
        required={requerido}
        autoComplete={autoComplete}
        aria-invalid={Boolean(error)}
        aria-describedby={[idError, idAyuda].filter(Boolean).join(" ") || undefined}
        onChange={(evento) => onCambio(evento.target.value)}
        className={cn(
          "mt-2 h-12 w-full rounded-xl border bg-superficie px-4 text-base text-texto outline-none",
          // El oro es el color que ya usa el panel para lo que hay que revisar.
          error ? "border-oro/70" : "border-lila/20 focus-visible:border-lila",
        )}
      />

      {ayuda && !error && (
        <p id={idAyuda} className="mt-1.5 text-xs text-texto-suave">
          {ayuda}
        </p>
      )}

      {error && (
        <p id={idError} className="mt-1.5 text-xs text-oro">
          {error}
        </p>
      )}
    </div>
  );
}
