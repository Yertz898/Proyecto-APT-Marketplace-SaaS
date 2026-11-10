"use client";

import { Popover } from "@base-ui/react/popover";

import { aHsv, contraste, derivarPaleta, esHexadecimal } from "@/lib/color";
import type { Paleta } from "@/lib/color";
import { cn } from "@/lib/utils";

/*
 * El color de la tienda.
 *
 * Antes eran cuatro campos de texto y había que escribir cuatro hexadecimales
 * que combinaran entre sí, o la vitrina se caía entera a la paleta de
 * DealCommerce. Nadie sabe de memoria el código de su marca.
 *
 * Ahora se elige una plantilla y los otros tres colores salen de
 * `derivarPaleta`, así que el backend sigue recibiendo los mismos cuatro
 * campos de siempre. El campo de texto se queda para quien sí trae el
 * hexadecimal de su marca.
 *
 * Lo que se elige acá es borrador, igual que el resto de la pantalla: nada se
 * publica hasta que el dueño aprieta Guardar.
 */

/*
 * Las quince plantillas.
 *
 * Son colores corrientes del comercio —el rojo de las ofertas, el azul de la
 * confianza, el verde de lo natural, el café del cuero— y van ordenadas como
 * la rueda, de los cálidos a los fríos, para que la grilla se lea de corrido.
 * Existen para que dos tiendas del mismo SaaS no terminen idénticas.
 *
 * Ninguna deja el botón con el texto blanco ilegible: están elegidas con ese
 * mínimo cumplido, así que un dueño que toma una plantilla nunca ve el aviso.
 */
const PLANTILLAS = [
  { nombre: "Carmesí", base: "#C62828" },
  { nombre: "Terracota", base: "#B4471F" },
  { nombre: "Naranjo", base: "#CC4A04" },
  { nombre: "Mostaza", base: "#9B6A0B" },
  { nombre: "Oliva", base: "#697C2D" },
  { nombre: "Bosque", base: "#1E7F53" },
  { nombre: "Turquesa", base: "#0E7490" },
  { nombre: "Celeste", base: "#0277BD" },
  { nombre: "Marino", base: "#1F4E79" },
  { nombre: "Índigo", base: "#3949AB" },
  { nombre: "Violeta", base: "#7C3AED" },
  { nombre: "Rosa", base: "#D81B60" },
  { nombre: "Borgoña", base: "#8E1F3D" },
  { nombre: "Cacao", base: "#6D4C32" },
  { nombre: "Carbón", base: "#2B2B33" },
] as const;

const POR_DEFECTO = "#7C3AED";

export function SelectorDeColor({
  id,
  valor,
  onPaleta,
  onTexto,
  deshabilitado,
  error,
}: {
  id: string;
  /** El color primario del borrador. Puede estar a medio escribir. */
  valor: string;
  /** Una elección completa: los cuatro colores de una vez. */
  onPaleta: (paleta: Paleta) => void;
  /** Lo que el dueño escribe a mano en el campo, válido o no. */
  onTexto: (texto: string) => void;
  deshabilitado: boolean;
  error?: string | null;
}) {
  // No hay estado propio: el color vive en el borrador del formulario y acá
  // solo se lee. Una copia local se desincronizaba al escribir a mano.
  const base = esHexadecimal(valor) ? valor : POR_DEFECTO;
  const paleta = derivarPaleta(aHsv(base));
  const ilegible = contraste(paleta.primario, "#FFFFFF") < 4.5;

  function escribir(texto: string) {
    onTexto(texto);
    if (esHexadecimal(texto)) {
      onPaleta(derivarPaleta(aHsv(texto)));
    }
  }

  return (
    <Popover.Root>
      <div className="flex items-center gap-2.5">
        <Popover.Trigger
          disabled={deshabilitado}
          aria-label="Elegir el color de tu tienda"
          style={esHexadecimal(valor) ? { background: valor } : undefined}
          className="size-11 shrink-0 cursor-pointer rounded-[10px] border border-niebla bg-hueso disabled:cursor-not-allowed disabled:opacity-60"
        />

        <input
          id={id}
          type="text"
          value={valor}
          disabled={deshabilitado}
          maxLength={7}
          spellCheck={false}
          placeholder={POR_DEFECTO}
          aria-invalid={Boolean(error)}
          onChange={(evento) => escribir(evento.target.value)}
          className={cn(
            "h-11 w-full rounded-[12px] border bg-white px-3 font-mono text-[14px] text-marino uppercase outline-none disabled:cursor-not-allowed disabled:opacity-60",
            error ? "border-ambar" : "border-niebla focus-visible:border-acero",
          )}
        />
      </div>

      <Popover.Portal>
        <Popover.Positioner side="bottom" align="start" sideOffset={10}>
          <Popover.Popup className="w-[360px] rounded-[14px] border border-arena bg-white p-[18px] shadow-[0_14px_34px_rgba(20,33,61,0.14)] outline-none">
            <Popover.Title className="text-xs font-semibold text-pizarra">
              Plantillas
            </Popover.Title>

            <div className="mt-3 max-h-[296px] overflow-y-auto pr-1">
              <div className="grid grid-cols-2 gap-2.5">
                {PLANTILLAS.map(({ nombre, base: suBase }) => {
                  const suya = derivarPaleta(aHsv(suBase));
                  const elegida = suBase.toUpperCase() === base.toUpperCase();

                  return (
                    <button
                      key={nombre}
                      type="button"
                      aria-pressed={elegida}
                      onClick={() => onPaleta(suya)}
                      className={cn(
                        "block w-full cursor-pointer rounded-[12px] bg-white p-2.5 text-left hover:border-acero focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-acero",
                        elegida ? "border-2 border-acero" : "border border-arena",
                      )}
                    >
                      <span aria-hidden="true" className="flex gap-1">
                        {[suya.primario, suya.hover, suya.acento, suya.destacado].map((color) => (
                          <span
                            key={color}
                            style={{ background: color }}
                            className="block h-[26px] flex-1 rounded-[5px]"
                          />
                        ))}
                      </span>
                      <span className="mt-[7px] block text-xs font-semibold text-marino">
                        {nombre}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            {ilegible && (
              <p className="mt-3.5 rounded-[10px] border border-arena bg-trigo px-2.5 py-2 text-[11px] leading-[1.45] text-marino">
                El texto blanco de tus botones casi no se lee sobre este color. Prueba uno más
                oscuro o elige una plantilla.
              </p>
            )}

            <div className="mt-3.5 flex items-center gap-2.5 border-t border-arena pt-3.5">
              <span aria-hidden="true" className="flex shrink-0 gap-[3px]">
                {[paleta.primario, paleta.hover, paleta.acento, paleta.destacado].map((color) => (
                  <span
                    key={color}
                    style={{ background: color }}
                    className="block h-[34px] w-[22px] rounded-[5px] border border-marino/15"
                  />
                ))}
              </span>

              <p className="min-w-0 flex-1 font-mono text-[13px] text-marino">{paleta.primario}</p>

              <Popover.Close className="h-11 cursor-pointer rounded-[12px] bg-acero px-[18px] text-sm font-semibold text-white hover:bg-acero-hondo">
                Usar
              </Popover.Close>
            </div>
          </Popover.Popup>
        </Popover.Positioner>
      </Popover.Portal>
    </Popover.Root>
  );
}
