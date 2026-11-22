"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";

import { SelectorDeHora } from "@/components/agenda/selector-de-hora";
import { useSesion } from "@/components/sesion/usar-sesion";
import { ErrorDeApi } from "@/lib/api/errores";
import {
  abrirDia,
  borrarBloque,
  cambiarEstadoDeVisita,
  cerrarDia,
  crearBloque,
  guardarConfiguracionAgenda,
  obtenerBloques,
  obtenerConfiguracionAgenda,
  obtenerDiasCerrados,
  obtenerVisitas,
  proponerCambioDeVisita,
  responderCambioDeVisita,
} from "@/lib/api/gestion";
import { formatearDiaLargo, formatearFechaLarga, formatearHora } from "@/lib/formato";
import type {
  BloqueDeAtencion,
  ConfiguracionDeAgenda,
  DiaCerrado,
  EstadoDeVisita,
  VisitaDelPanel,
} from "@/lib/tipos-gestion";
import { cn } from "@/lib/utils";

import { Aviso, Boton, CLASE_ENTRADA, Campo, mensajeDe } from "./controles";
import { Cabecera, Cargando, Error, Tarjeta, Vacio } from "./piezas";

/*
 * La agenda de visitas desde el panel.
 *
 * Tres pestañas: las visitas que llegan (lo que se mira todos los días), el
 * horario de atención y las reglas. La vitrina ofrece horas a partir de lo
 * que se define acá.
 */

const DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];

const ACCION_DE_ESTADO: Record<EstadoDeVisita, string> = {
  solicitada: "Solicitada",
  confirmada: "Confirmar",
  rechazada: "Rechazar",
  cancelada: "Cancelar",
  asistida: "Asistió",
  no_asistio: "No asistió",
};

type Pestana = "visitas" | "horario" | "reglas";

export function PantallaAgenda() {
  const [pestana, setPestana] = useState<Pestana>("visitas");

  return (
    <>
      <Cabecera titulo="Agenda de visitas" descripcion="Cuándo atiendes y quién viene a verte." />

      <div role="tablist" className="mb-5 flex flex-wrap gap-2">
        {(
          [
            ["visitas", "Visitas"],
            ["horario", "Horario de atención"],
            ["reglas", "Reglas"],
          ] as const
        ).map(([valor, etiqueta]) => (
          <button
            key={valor}
            type="button"
            role="tab"
            aria-selected={pestana === valor}
            onClick={() => setPestana(valor)}
            className={cn(
              "h-10 cursor-pointer rounded-full border px-4 text-[13px] font-semibold transition-colors",
              pestana === valor ? "border-acero bg-acero text-white" : "border-niebla bg-white text-acero hover:bg-cielo",
            )}
          >
            {etiqueta}
          </button>
        ))}
      </div>

      {pestana === "visitas" && <Visitas />}
      {pestana === "horario" && <Horario />}
      {pestana === "reglas" && <Reglas />}
    </>
  );
}

// ── Visitas ─────────────────────────────────────────────────────────────────

function Visitas() {
  const [visitas, setVisitas] = useState<VisitaDelPanel[] | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);

  const cargar = useCallback(() => {
    obtenerVisitas().then(setVisitas, (error) => setFallo(mensajeDe(error)));
  }, []);
  useEffect(cargar, [cargar]);

  if (fallo) return <Error mensaje={fallo} onReintentar={() => {
            setFallo(null);
            cargar();
          }} />;
  if (!visitas) return <Cargando />;
  if (visitas.length === 0) {
    return (
      <Vacio
        titulo="No tienes visitas por delante"
        detalle="Cuando un cliente pida hora desde tu tienda, aparece acá para que la confirmes."
      />
    );
  }

  return (
    <div className="flex flex-col gap-3">
      {visitas.map((visita) => (
        <TarjetaDeVisita
          key={visita.id}
          visita={visita}
          onCambio={(nueva) => setVisitas((actual) => actual?.map((v) => (v.id === nueva.id ? nueva : v)) ?? null)}
        />
      ))}
    </div>
  );
}

function TarjetaDeVisita({ visita, onCambio }: { visita: VisitaDelPanel; onCambio: (v: VisitaDelPanel) => void }) {
  const { sesion } = useSesion();
  const slug = sesion?.usuario.tienda?.slug;
  const [trabajando, setTrabajando] = useState(false);
  const [fallo, setFallo] = useState<string | null>(null);
  const [eligiendo, setEligiendo] = useState(false);
  const cambio = visita.cambioPendiente;
  const vigente = visita.estado === "solicitada" || visita.estado === "confirmada";

  async function hacer(accion: () => Promise<VisitaDelPanel>) {
    setTrabajando(true);
    setFallo(null);
    try {
      onCambio(await accion());
      setEligiendo(false);
    } catch (error) {
      setFallo(mensajeDe(error));
    } finally {
      setTrabajando(false);
    }
  }

  async function pasarA(estado: EstadoDeVisita) {
    let motivo = "";
    if (estado === "rechazada") {
      motivo = window.prompt("¿Por qué la rechazas? El cliente lo verá.") ?? "";
    }
    await hacer(() => cambiarEstadoDeVisita(visita.id, estado, motivo));
  }

  return (
    <Tarjeta className="p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="font-jakarta text-[16px] font-bold text-marino">
            {formatearDiaLargo(visita.inicio)} · {formatearHora(visita.inicio)}
          </p>
          <p className="mt-1 text-[14px] text-marino">{visita.nombreContacto}</p>
          <p className="text-[13px] text-pizarra">
            {visita.telefonoContacto} · {visita.correoContacto}
          </p>
          {visita.motivo && <p className="mt-2 text-[13px] text-pizarra">«{visita.motivo}»</p>}
        </div>
        <span className="rounded-full bg-hueso px-3 py-1 text-[12px] font-semibold text-acero">{visita.estadoNombre}</span>
      </div>
      {visita.horaTomada && (
        <p className="mt-3 rounded-[10px] border border-ambar bg-trigo px-3 py-2 text-[13px] text-marino">
          Esa hora ya la tomó otra visita que confirmaste. Rechaza esta solicitud o proponle otra hora.
        </p>
      )}

      {cambio && cambio.propuestoPor === "comprador" && (
        <div className="mt-3 rounded-[10px] border border-ambar bg-trigo px-3.5 py-3">
          <p className="text-[13px] text-marino">
            <b>{visita.nombreContacto}</b> pide cambiarla al{" "}
            <b>
              {formatearDiaLargo(cambio.inicio)} · {formatearHora(cambio.inicio)}
            </b>
            . Si rechazas el cambio, la visita se cancela.
          </p>
          <div className="mt-2.5 flex flex-wrap gap-2">
            <Boton
              className="h-9 px-3 text-[13px]"
              disabled={trabajando}
              onClick={() => hacer(() => responderCambioDeVisita(visita.id, true))}
            >
              Aceptar cambio
            </Boton>
            <Boton
              variante="secundario"
              className="h-9 px-3 text-[13px]"
              disabled={trabajando}
              onClick={() => {
                if (window.confirm("Si rechazas el cambio, la visita se cancela. ¿Seguir?")) {
                  hacer(() => responderCambioDeVisita(visita.id, false));
                }
              }}
            >
              Rechazar
            </Boton>
          </div>
        </div>
      )}

      {cambio && cambio.propuestoPor === "tienda" && (
        <p className="mt-3 rounded-[10px] border border-niebla bg-cielo px-3 py-2 text-[13px] text-marino">
          Le propusiste cambiarla al{" "}
          <b>
            {formatearDiaLargo(cambio.inicio)} · {formatearHora(cambio.inicio)}
          </b>
          . Esperando la respuesta del cliente.
        </p>
      )}

      {!eligiendo && (visita.siguientes.length > 0 || (vigente && !cambio && slug)) && (
        <div className="mt-4 flex flex-wrap gap-2">
          {visita.siguientes.map((estado) => (
            <Boton
              key={estado}
              variante={estado === "confirmada" || estado === "asistida" ? "principal" : "secundario"}
              className="h-9 px-3 text-[13px]"
              disabled={trabajando}
              onClick={() => pasarA(estado)}
            >
              {ACCION_DE_ESTADO[estado]}
            </Boton>
          ))}
          {vigente && !cambio && slug && (
            <Boton
              variante="secundario"
              className="h-9 px-3 text-[13px]"
              disabled={trabajando}
              onClick={() => setEligiendo(true)}
            >
              Proponer otra hora
            </Boton>
          )}
        </div>
      )}

      {eligiendo && slug && (
        <div className="mt-4">
          <SelectorDeHora
            slug={slug}
            horaActual={visita.inicio}
            tema="panel"
            ocupado={trabajando}
            onElegir={(inicio) => hacer(() => proponerCambioDeVisita(visita.id, inicio))}
            onCancelar={() => setEligiendo(false)}
          />
          <p className="mt-2 text-xs text-pizarra">
            El cliente acepta o rechaza la hora nueva desde «Mis citas». Si la rechaza, la visita se cancela.
          </p>
        </div>
      )}
      {fallo && <Aviso tipo="error">{fallo}</Aviso>}
    </Tarjeta>
  );
}

// ── Horario ─────────────────────────────────────────────────────────────────

function Horario() {
  const [bloques, setBloques] = useState<BloqueDeAtencion[] | null>(null);
  const [dias, setDias] = useState<DiaCerrado[] | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);

  const cargar = useCallback(() => {
    Promise.all([obtenerBloques(), obtenerDiasCerrados()]).then(
      ([b, d]) => {
        setBloques(b);
        setDias(d);
      },
      (error) => setFallo(mensajeDe(error)),
    );
  }, []);
  useEffect(cargar, [cargar]);

  if (fallo) return <Error mensaje={fallo} onReintentar={() => {
            setFallo(null);
            cargar();
          }} />;
  if (!bloques || !dias) return <Cargando />;

  const semanales = bloques.filter((b) => b.diaSemana !== null);

  return (
    <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_360px] lg:items-start">
      <Tarjeta>
        <p className="text-[13px] font-semibold text-marino">Tu semana</p>
        <p className="mt-1 text-[13px] text-pizarra">
          Un día puede tener varios tramos, por ejemplo de 10:00 a 13:00 y de 15:00 a 18:00.
        </p>
        <ul className="mt-4 divide-y divide-arena">
          {DIAS.map((dia, indice) => {
            const delDia = semanales.filter((b) => b.diaSemana === indice);
            return (
              <li key={dia} className="flex flex-wrap items-center gap-2 py-3">
                <span className="w-[96px] text-[14px] font-semibold text-marino">{dia}</span>
                {delDia.length === 0 && <span className="text-[13px] text-pizarra">Cerrado</span>}
                {delDia.map((bloque) => (
                  <span key={bloque.id} className="inline-flex items-center gap-1.5 rounded-full bg-cielo px-3 py-1 text-[13px] text-acero">
                    {bloque.horaInicio}–{bloque.horaFin}
                    <button
                      type="button"
                      aria-label={`Quitar el tramo de ${bloque.horaInicio} a ${bloque.horaFin}`}
                      className="cursor-pointer text-[15px] leading-none text-acero/70 hover:text-acero"
                      onClick={async () => {
                        await borrarBloque(bloque.id);
                        setBloques((actual) => actual?.filter((b) => b.id !== bloque.id) ?? null);
                      }}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </li>
            );
          })}
        </ul>
      </Tarjeta>

      <div className="flex flex-col gap-4">
        <NuevoTramo onCreado={(b) => setBloques((actual) => [...(actual ?? []), b])} />
        <DiasCerrados dias={dias} setDias={setDias} />
      </div>
    </div>
  );
}

function NuevoTramo({ onCreado }: { onCreado: (b: BloqueDeAtencion) => void }) {
  const [dia, setDia] = useState(0);
  const [inicio, setInicio] = useState("10:00");
  const [fin, setFin] = useState("13:00");
  const [guardando, setGuardando] = useState(false);
  const [fallo, setFallo] = useState<string | null>(null);

  async function crear(evento: FormEvent) {
    evento.preventDefault();
    setGuardando(true);
    setFallo(null);
    try {
      onCreado(
        await crearBloque({
          nombre: "",
          diaSemana: dia,
          fecha: null,
          horaInicio: inicio,
          horaFin: fin,
          duracionMinutos: null,
          visitasSimultaneas: null,
        }),
      );
    } catch (error) {
      const detalle = error instanceof ErrorDeApi ? Object.values(error.detalles)[0]?.[0] : null;
      setFallo(detalle ?? mensajeDe(error));
    } finally {
      setGuardando(false);
    }
  }

  return (
    <Tarjeta>
      <form onSubmit={crear} className="flex flex-col gap-3">
        <p className="text-[13px] font-semibold text-marino">Agregar tramo</p>
        <label className="text-[13px] font-semibold text-marino">
          Día
          <select className={CLASE_ENTRADA} value={dia} onChange={(e) => setDia(Number(e.target.value))}>
            {DIAS.map((nombre, indice) => (
              <option key={nombre} value={indice}>
                {nombre}
              </option>
            ))}
          </select>
        </label>
        <div className="grid grid-cols-2 gap-3">
          <Campo id="tramo-inicio" etiqueta="Desde" type="time" value={inicio} onChange={(e) => setInicio(e.target.value)} />
          <Campo id="tramo-fin" etiqueta="Hasta" type="time" value={fin} onChange={(e) => setFin(e.target.value)} />
        </div>
        <div>
          <Boton type="submit" disabled={guardando}>
            {guardando ? "Agregando…" : "Agregar"}
          </Boton>
        </div>
        {fallo && <Aviso tipo="error">{fallo}</Aviso>}
      </form>
    </Tarjeta>
  );
}

function DiasCerrados({
  dias,
  setDias,
}: {
  dias: DiaCerrado[];
  setDias: (actualizar: (d: DiaCerrado[] | null) => DiaCerrado[] | null) => void;
}) {
  const [fecha, setFecha] = useState("");
  const [motivo, setMotivo] = useState("");
  const [fallo, setFallo] = useState<string | null>(null);

  async function cerrar(evento: FormEvent) {
    evento.preventDefault();
    setFallo(null);
    try {
      const nuevo = await cerrarDia(fecha, motivo);
      setDias((actual) => [...(actual ?? []), nuevo].sort((a, b) => a.fecha.localeCompare(b.fecha)));
      setFecha("");
      setMotivo("");
    } catch (error) {
      setFallo(error instanceof ErrorDeApi ? (error.de("fecha") ?? error.message) : mensajeDe(error));
    }
  }

  return (
    <Tarjeta>
      <form onSubmit={cerrar} className="flex flex-col gap-3">
        <p className="text-[13px] font-semibold text-marino">Días cerrados</p>
        <p className="text-[13px] text-pizarra">Feriados o días en que no atiendes, aunque toque.</p>
        {dias.length > 0 && (
          <ul className="flex flex-col gap-1.5">
            {dias.map((d) => (
              <li key={d.id} className="flex items-center justify-between rounded-[10px] bg-hueso px-3 py-2 text-[13px]">
                <span className="text-marino">
                  {formatearFechaLarga(d.fecha)}
                  {d.motivo && <span className="text-pizarra"> · {d.motivo}</span>}
                </span>
                <button
                  type="button"
                  className="cursor-pointer text-[12px] font-semibold text-acero"
                  onClick={async () => {
                    await abrirDia(d.id);
                    setDias((actual) => actual?.filter((x) => x.id !== d.id) ?? null);
                  }}
                >
                  Abrir
                </button>
              </li>
            ))}
          </ul>
        )}
        <Campo id="dia-fecha" etiqueta="Fecha" type="date" value={fecha} onChange={(e) => setFecha(e.target.value)} />
        <Campo id="dia-motivo" etiqueta="Motivo (opcional)" value={motivo} onChange={(e) => setMotivo(e.target.value)} maxLength={150} />
        <div>
          <Boton type="submit" variante="secundario" disabled={!fecha}>
            Cerrar ese día
          </Boton>
        </div>
        {fallo && <Aviso tipo="error">{fallo}</Aviso>}
      </form>
    </Tarjeta>
  );
}

// ── Reglas ──────────────────────────────────────────────────────────────────

function Reglas() {
  const [config, setConfig] = useState<ConfiguracionDeAgenda | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);
  const [guardando, setGuardando] = useState(false);
  const [aviso, setAviso] = useState<{ tipo: "ok" | "error"; texto: string } | null>(null);

  useEffect(() => {
    obtenerConfiguracionAgenda().then(setConfig, (error) => setFallo(mensajeDe(error)));
  }, []);

  if (fallo) return <Error mensaje={fallo} />;
  if (!config) return <Cargando />;

  const cambiar = <K extends keyof ConfiguracionDeAgenda>(campo: K, valor: ConfiguracionDeAgenda[K]) =>
    setConfig({ ...config, [campo]: valor });

  async function guardar(evento: FormEvent) {
    evento.preventDefault();
    if (!config) return;
    setGuardando(true);
    setAviso(null);
    try {
      setConfig(await guardarConfiguracionAgenda(config));
      setAviso({ tipo: "ok", texto: "Guardamos las reglas de tu agenda." });
    } catch (error) {
      setAviso({ tipo: "error", texto: mensajeDe(error) });
    } finally {
      setGuardando(false);
    }
  }

  const numero = (texto: string) => Number(texto.replace(/\D/g, "") || "0");

  return (
    <Tarjeta>
      <form onSubmit={guardar} className="grid gap-4 md:grid-cols-2">
        <Campo
          id="duracion"
          etiqueta="Duración de cada visita (minutos)"
          inputMode="numeric"
          value={config.duracionMinutos}
          onChange={(e) => cambiar("duracionMinutos", numero(e.target.value))}
        />
        <Campo
          id="simultaneas"
          etiqueta="Visitas a la vez"
          inputMode="numeric"
          value={config.visitasPorBloque}
          onChange={(e) => cambiar("visitasPorBloque", numero(e.target.value))}
        />
        <Campo
          id="anticipacion"
          etiqueta="Anticipación mínima (horas)"
          inputMode="numeric"
          value={config.anticipacionMinimaHoras}
          onChange={(e) => cambiar("anticipacionMinimaHoras", numero(e.target.value))}
        />
        <Campo
          id="ventana"
          etiqueta="Hasta cuántos días adelante se puede reservar"
          inputMode="numeric"
          value={config.ventanaMaximaDias}
          onChange={(e) => cambiar("ventanaMaximaDias", numero(e.target.value))}
        />
        <Campo id="direccion" etiqueta="Dirección" value={config.direccion} onChange={(e) => cambiar("direccion", e.target.value)} />
        <Campo
          id="correo-agenda"
          etiqueta="Correo para avisos"
          type="email"
          value={config.correoNotificaciones}
          onChange={(e) => cambiar("correoNotificaciones", e.target.value)}
        />
        <label className="md:col-span-2 text-[13px] font-semibold text-marino">
          Cómo llegar
          <textarea
            className={cn(CLASE_ENTRADA, "h-24 py-2")}
            value={config.indicaciones}
            onChange={(e) => cambiar("indicaciones", e.target.value)}
          />
        </label>
        <label className="flex cursor-pointer items-start gap-3 rounded-[12px] border border-arena bg-hueso p-4 md:col-span-2">
          <input
            type="checkbox"
            className="mt-1 size-4 cursor-pointer accent-[#1f4e79]"
            checked={config.confirmacionAutomatica}
            onChange={(e) => cambiar("confirmacionAutomatica", e.target.checked)}
          />
          <span className="text-[13px] text-pizarra">
            <span className="block font-semibold text-marino">Confirmar solas las solicitudes</span>
            Apagado, cada visita espera a que la aceptes.
          </span>
        </label>
        <div className="md:col-span-2">
          <Boton type="submit" disabled={guardando}>
            {guardando ? "Guardando…" : "Guardar reglas"}
          </Boton>
          {aviso && <Aviso tipo={aviso.tipo}>{aviso.texto}</Aviso>}
        </div>
      </form>
    </Tarjeta>
  );
}
