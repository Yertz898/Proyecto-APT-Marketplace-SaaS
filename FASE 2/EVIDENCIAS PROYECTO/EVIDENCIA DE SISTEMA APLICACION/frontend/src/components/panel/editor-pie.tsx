"use client";

import { useState } from "react";

import { Campo } from "@/components/campo";
import { IconoRed } from "@/components/tienda/icono-red";
import type { ErrorDeApi } from "@/lib/api/errores";
import { esEnlaceValido, nombreDeRed, perfilDe, redDe } from "@/lib/redes";
import type { PerfilDeTienda } from "@/lib/tipos-panel";

import { Tarjeta } from "./piezas";

/*
 * El editor del pie de página de la vitrina.
 *
 * Tiene lo que trae el pie de cualquier marketplace: una frase sobre la tienda,
 * cómo contactarla y sus redes. Las redes son una lista libre: el dueño pega
 * el enlace a su perfil y el ícono se elige solo por el dominio, así que no
 * hace falta una casilla por red ni saber cuál es cuál.
 */

const MAXIMO = 8;

type Cambiar = <C extends keyof PerfilDeTienda>(campo: C, valor: PerfilDeTienda[C]) => void;

export function EditorDelPie({
  borrador,
  cambiar,
  deshabilitado,
  error,
}: {
  borrador: PerfilDeTienda;
  cambiar: Cambiar;
  deshabilitado: boolean;
  error: ErrorDeApi | null;
}) {
  const [nuevo, setNuevo] = useState("");
  const [aviso, setAviso] = useState<string | null>(null);
  const redes = borrador.redesSociales ?? [];

  function agregar() {
    let enlace = nuevo.trim();
    if (!enlace) return;
    // Quien pega «instagram.com/mi-tienda» quiere decir https.
    if (!/^[a-z]+:\/\//i.test(enlace)) enlace = `https://${enlace}`;
    if (!esEnlaceValido(enlace)) {
      setAviso("Ese enlace no se puede usar. Copia la dirección completa de tu perfil.");
      return;
    }
    if (redes.includes(enlace)) {
      setAviso("Ese enlace ya está en la lista.");
      return;
    }
    if (redes.length >= MAXIMO) {
      setAviso(`Puedes poner hasta ${MAXIMO} redes.`);
      return;
    }
    cambiar("redesSociales", [...redes, enlace]);
    setNuevo("");
    setAviso(null);
  }

  function quitar(enlace: string) {
    cambiar(
      "redesSociales",
      redes.filter((r) => r !== enlace),
    );
  }

  function mover(indice: number, sentido: -1 | 1) {
    const otro = indice + sentido;
    if (otro < 0 || otro >= redes.length) return;
    const lista = [...redes];
    const actual = lista.at(indice) as string;
    lista.splice(indice, 1);
    lista.splice(otro, 0, actual);
    cambiar("redesSociales", lista);
  }

  return (
    <Tarjeta>
      <p className="text-[13px] font-semibold text-marino">Pie de página</p>
      <p className="mt-1 text-[13px] text-pizarra">
        Lo que aparece al final de cada página de tu tienda. Lo que dejes en blanco no se muestra. Viene con todos los
        planes.
      </p>

      <div className="mt-4 flex flex-col gap-4">
        <Campo
          id="pie-descripcion"
          etiqueta="Sobre tu tienda"
          tema="claro"
          requerido={false}
          multilinea
          placeholder="Joyas de plata al por mayor y al detalle, con envío a todo Chile."
          valor={borrador.pieDescripcion ?? ""}
          onCambio={(valor) => cambiar("pieDescripcion", valor.slice(0, 300))}
          error={error?.de("pieDescripcion")}
          ayuda={`${(borrador.pieDescripcion ?? "").length} de 300 caracteres.`}
        />
        <div className="grid gap-4 sm:grid-cols-2">
          <Campo
            id="pie-correo"
            etiqueta="Correo de contacto"
            tipo="email"
            tema="claro"
            requerido={false}
            valor={borrador.pieCorreo ?? ""}
            onCambio={(valor) => cambiar("pieCorreo", valor)}
            error={error?.de("pieCorreo")}
          />
          <Campo
            id="pie-telefono"
            etiqueta="Teléfono"
            tipo="tel"
            tema="claro"
            requerido={false}
            placeholder="+56 9 1234 5678"
            valor={borrador.pieTelefono ?? ""}
            onCambio={(valor) => /^[\d+\s()-]{0,30}$/.test(valor) && cambiar("pieTelefono", valor)}
            error={error?.de("pieTelefono")}
          />
          <Campo
            id="pie-direccion"
            etiqueta="Dirección"
            tema="claro"
            requerido={false}
            placeholder="Av. Providencia 1234, Santiago"
            valor={borrador.pieDireccion ?? ""}
            onCambio={(valor) => cambiar("pieDireccion", valor.slice(0, 200))}
            error={error?.de("pieDireccion")}
          />
          <Campo
            id="pie-horario"
            etiqueta="Horario de atención"
            tema="claro"
            requerido={false}
            placeholder="Lunes a viernes, 10:00 a 18:00"
            valor={borrador.pieHorario ?? ""}
            onCambio={(valor) => cambiar("pieHorario", valor.slice(0, 120))}
            error={error?.de("pieHorario")}
          />
        </div>

        <div>
          <p className="text-[13px] font-semibold text-marino">Redes sociales</p>
          <p className="mt-1 text-[12px] text-pizarra">
            Pega el enlace a tu perfil. Reconocemos Instagram, Facebook, TikTok, X, YouTube, WhatsApp, LinkedIn,
            Pinterest y Telegram; cualquier otro enlace aparece como sitio web.
          </p>

          {redes.length > 0 && (
            <ul className="mt-3 flex list-none flex-col gap-2 p-0">
              {redes.map((enlace, indice) => {
                const red = redDe(enlace);
                return (
                  <li key={enlace} className="flex items-center gap-3 rounded-[12px] border border-arena bg-hueso px-3 py-2">
                    <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-white text-acero">
                      <IconoRed red={red} tamano={18} />
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block text-[13px] font-semibold text-marino">{nombreDeRed(red)}</span>
                      <span className="block truncate text-[12px] text-pizarra">{perfilDe(enlace)}</span>
                    </span>
                    <span className="flex shrink-0 items-center gap-1">
                      <BotonChico etiqueta="Subir" deshabilitado={deshabilitado || indice === 0} onClick={() => mover(indice, -1)}>
                        ↑
                      </BotonChico>
                      <BotonChico
                        etiqueta="Bajar"
                        deshabilitado={deshabilitado || indice === redes.length - 1}
                        onClick={() => mover(indice, 1)}
                      >
                        ↓
                      </BotonChico>
                      <BotonChico etiqueta={`Quitar ${nombreDeRed(red)}`} deshabilitado={deshabilitado} onClick={() => quitar(enlace)}>
                        ×
                      </BotonChico>
                    </span>
                  </li>
                );
              })}
            </ul>
          )}

          {!deshabilitado && redes.length < MAXIMO && (
            <div className="mt-3 flex flex-wrap items-center gap-2">
              <span className="flex size-11 shrink-0 items-center justify-center rounded-[12px] border border-niebla text-acero">
                <IconoRed red={nuevo.trim() ? redDe(/^[a-z]+:\/\//i.test(nuevo) ? nuevo : `https://${nuevo}`) : "sitio"} tamano={18} />
              </span>
              <input
                aria-label="Enlace a una red social"
                value={nuevo}
                onChange={(e) => {
                  setNuevo(e.target.value);
                  setAviso(null);
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    agregar();
                  }
                }}
                placeholder="https://instagram.com/tu-tienda"
                className="h-11 min-w-[220px] flex-1 rounded-[12px] border border-niebla bg-white px-3 text-[14px] text-marino outline-none focus-visible:border-acero"
              />
              <button
                type="button"
                onClick={agregar}
                className="h-11 cursor-pointer rounded-[12px] bg-acero px-4 text-[13px] font-semibold text-white hover:bg-acero-hondo"
              >
                Agregar
              </button>
            </div>
          )}
          {(aviso || error?.de("redesSociales")) && (
            <p className="mt-2 text-xs font-medium text-ambar-hondo">{aviso ?? error?.de("redesSociales")}</p>
          )}
        </div>
      </div>
    </Tarjeta>
  );
}

function BotonChico({
  etiqueta,
  deshabilitado,
  onClick,
  children,
}: {
  etiqueta: string;
  deshabilitado: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      aria-label={etiqueta}
      title={etiqueta}
      disabled={deshabilitado}
      onClick={onClick}
      className="flex size-8 cursor-pointer items-center justify-center rounded-full text-[15px] text-pizarra hover:bg-white hover:text-marino disabled:cursor-not-allowed disabled:opacity-30"
    >
      {children}
    </button>
  );
}
