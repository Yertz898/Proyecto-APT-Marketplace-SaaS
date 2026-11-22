"use client";

import Link from "next/link";
import { Fragment, useCallback, useEffect, useState, type FormEvent } from "react";

import { Aviso, Boton, CLASE_ENTRADA, Campo, mensajeDe } from "@/components/panel/controles";
import { Cargando, Error, Tarjeta, Vacio } from "@/components/panel/piezas";
import { ErrorDeApi } from "@/lib/api/errores";
import {
  cambiarSolicitud,
  cambiarTienda,
  crearTienda,
  marcarMensaje,
  obtenerMensajes,
  obtenerRegistros,
  obtenerSolicitudes,
  obtenerTiendas,
  type MensajeDeTienda,
} from "@/lib/api/gestion";
import { formatearFecha } from "@/lib/formato";
import type { Plan } from "@/lib/tipos";
import type {
  NuevaTienda,
  PaginaDeRegistros,
  Plantilla,
  SolicitudDeAcceso,
  TiendaDePlataforma,
} from "@/lib/tipos-gestion";
import { cn } from "@/lib/utils";

/*
 * La administración de DealCommerce.
 *
 * Tres pestañas: las tiendas (alta, plan, plantilla, si están abiertas), las
 * solicitudes de negocios que pidieron entrar, y el registro con todo lo que
 * se hizo en cada tienda. El backend cierra todo esto a quien no sea
 * administrador; la guardia de la página solo evita dibujarlo.
 */

const PLANES: { valor: Plan; nombre: string }[] = [
  { valor: "basico", nombre: "Básico" },
  { valor: "premium", nombre: "Premium" },
  { valor: "ultimate", nombre: "Ultimate" },
];

const PLANTILLAS: { valor: Plantilla; nombre: string }[] = [
  { valor: "clasica", nombre: "Clásica" },
  { valor: "moderna", nombre: "Moderna" },
  { valor: "minimal", nombre: "Minimal" },
];

type Pestana = "tiendas" | "mensajes" | "solicitudes" | "registro";

export function PantallaPlataforma() {
  const [pestana, setPestana] = useState<Pestana>("tiendas");
  const [tiendaDelRegistro, setTiendaDelRegistro] = useState("");
  // La solicitud que se está convirtiendo en tienda: llena el formulario.
  const [desdeSolicitud, setDesdeSolicitud] = useState<SolicitudDeAcceso | null>(null);
  // Cuántos mensajes de tiendas cerradas falta leer, para el número de la pestaña.
  const [sinLeer, setSinLeer] = useState(0);

  useEffect(() => {
    obtenerMensajes().then(
      (mensajes) => setSinLeer(mensajes.filter((m) => !m.leido).length),
      () => setSinLeer(0),
    );
  }, []);

  return (
    <>
      <div className="border-b border-arena pb-6">
        <p className="mb-1.5 text-[12px] font-semibold tracking-[0.06em] text-acero uppercase">Plataforma</p>
        <h1 className="font-jakarta text-[clamp(26px,2.6cqi,32px)] leading-[1.1] font-extrabold tracking-[-0.03em]">
          Administración de DealCommerce
        </h1>
        <p className="mt-2 text-[15px] text-pizarra">Las tiendas suscritas, quién pidió entrar y qué pasó en cada una.</p>
      </div>

      <div role="tablist" className="mt-6 mb-6 flex flex-wrap gap-2">
        {(
          [
            ["tiendas", "Tiendas"],
            ["mensajes", sinLeer > 0 ? `Mensajes (${sinLeer})` : "Mensajes"],
            ["solicitudes", "Solicitudes"],
            ["registro", "Registro de actividad"],
          ] as const
        ).map(([valor, etiqueta]) => (
          <button
            key={valor}
            type="button"
            role="tab"
            aria-selected={pestana === valor}
            onClick={() => setPestana(valor)}
            className={cn(
              "h-9 cursor-pointer rounded-lg border px-3.5 text-[13px] font-semibold transition-colors motion-reduce:transition-none",
              pestana === valor ? "border-marino bg-marino text-white" : "border-arena bg-white text-marino hover:border-niebla",
            )}
          >
            {etiqueta}
          </button>
        ))}
      </div>

      {pestana === "tiendas" && (
        <Tiendas
          desdeSolicitud={desdeSolicitud}
          onCreada={() => setDesdeSolicitud(null)}
          onVerRegistro={(slug) => {
            setTiendaDelRegistro(slug);
            setPestana("registro");
          }}
        />
      )}
      {pestana === "mensajes" && <Mensajes onSinLeer={setSinLeer} />}
      {pestana === "solicitudes" && (
        <Solicitudes
          onCrearTienda={(solicitud) => {
            setDesdeSolicitud(solicitud);
            setPestana("tiendas");
          }}
        />
      )}
      {pestana === "registro" && <Registro tiendaInicial={tiendaDelRegistro} />}
    </>
  );
}

// ── Tiendas ─────────────────────────────────────────────────────────────────

function Tiendas({
  desdeSolicitud,
  onCreada,
  onVerRegistro,
}: {
  desdeSolicitud: SolicitudDeAcceso | null;
  onCreada: () => void;
  onVerRegistro: (slug: string) => void;
}) {
  const [tiendas, setTiendas] = useState<TiendaDePlataforma[] | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);

  useEffect(() => {
    obtenerTiendas().then(setTiendas, (error) => setFallo(mensajeDe(error)));
  }, []);

  function reemplazar(tienda: TiendaDePlataforma) {
    setTiendas((actual) => actual?.map((t) => (t.id === tienda.id ? tienda : t)) ?? null);
  }

  if (fallo) return <Error mensaje={fallo} />;
  if (!tiendas) return <Cargando />;

  return (
    <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_380px] xl:items-start">
      <div className="flex flex-col gap-3">
        {tiendas.length === 0 && <Vacio titulo="Todavía no hay tiendas" />}
        {tiendas.map((tienda) => (
          <FilaDeTienda key={tienda.id} tienda={tienda} onCambio={reemplazar} onVerRegistro={onVerRegistro} />
        ))}
      </div>
      <NuevaTiendaFormulario
        key={desdeSolicitud?.id ?? "nueva"}
        desdeSolicitud={desdeSolicitud}
        onCreada={(t) => {
          setTiendas((actual) => [...(actual ?? []), t]);
          onCreada();
        }}
      />
    </div>
  );
}

function FilaDeTienda({
  tienda,
  onCambio,
  onVerRegistro,
}: {
  tienda: TiendaDePlataforma;
  onCambio: (t: TiendaDePlataforma) => void;
  onVerRegistro: (slug: string) => void;
}) {
  const [fallo, setFallo] = useState<string | null>(null);
  const [trabajando, setTrabajando] = useState(false);

  async function cambiar(cambios: Parameters<typeof cambiarTienda>[1]) {
    setTrabajando(true);
    setFallo(null);
    try {
      onCambio(await cambiarTienda(tienda.slug, cambios));
    } catch (error) {
      setFallo(mensajeDe(error));
    } finally {
      setTrabajando(false);
    }
  }

  return (
    <Tarjeta className="p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="font-jakarta text-[17px] font-bold">
            {tienda.nombre}
            {!tienda.activa && (
              <span className="ml-2 rounded-full bg-trigo px-2 py-0.5 text-[11px] font-semibold text-ambar-hondo">
                {tienda.canceladaEn ? "Canceló su plan" : "Cerrada"}
              </span>
            )}
          </p>
          <p className="text-[13px] text-pizarra">
            /t/{tienda.slug} · desde el {formatearFecha(tienda.fechaCreacion)}
            {tienda.dueno && ` · ${tienda.dueno.nombre} (${tienda.dueno.email})`}
          </p>
          <p className="mt-1 text-[13px] text-pizarra">
            {tienda.productos} productos · {tienda.pedidos} pedidos · {tienda.usuarios} cuentas
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link
            href={`/t/${tienda.slug}`}
            target="_blank"
            className="flex h-9 items-center rounded-[10px] border border-niebla px-3 text-[13px] font-semibold text-acero no-underline hover:bg-cielo hover:no-underline"
          >
            Ver vitrina
          </Link>
          <Boton variante="secundario" className="h-9 px-3 text-[13px]" onClick={() => onVerRegistro(tienda.slug)}>
            Ver registro
          </Boton>
        </div>
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <label className="text-[12px] font-semibold text-marino">
          Plan
          <select
            className={cn(CLASE_ENTRADA, "h-10")}
            value={tienda.plan}
            disabled={trabajando}
            onChange={(e) => cambiar({ plan: e.target.value as Plan })}
          >
            {PLANES.map((p) => (
              <option key={p.valor} value={p.valor}>
                {p.nombre}
              </option>
            ))}
          </select>
        </label>
        <label className="text-[12px] font-semibold text-marino">
          Plantilla
          <select
            className={cn(CLASE_ENTRADA, "h-10")}
            value={tienda.plantilla}
            disabled={trabajando}
            onChange={(e) => cambiar({ plantilla: e.target.value as Plantilla })}
          >
            {PLANTILLAS.map((p) => (
              <option key={p.valor} value={p.valor}>
                {p.nombre}
              </option>
            ))}
          </select>
        </label>
        <div className="flex items-end">
          <Boton
            variante={tienda.activa ? "secundario" : "principal"}
            className="h-10 w-full"
            disabled={trabajando}
            onClick={() => cambiar({ activa: !tienda.activa })}
          >
            {tienda.activa ? "Cerrar tienda" : "Abrir tienda"}
          </Boton>
        </div>
      </div>
      {fallo && <Aviso tipo="error">{fallo}</Aviso>}
    </Tarjeta>
  );
}

const TIENDA_VACIA: NuevaTienda = {
  nombre: "",
  slug: "",
  plan: "basico",
  plantilla: "clasica",
  duenoNombre: "",
  duenoEmail: "",
  duenoPassword: "",
};

/** De «Joyas Ye» a «joyas-ye»: la dirección pública que se sugiere. */
function sugerirSlug(nombre: string): string {
  return nombre
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 60);
}

/** Lo que se sabe de una solicitud, puesto en el formulario de tienda nueva. */
function desde(solicitud: SolicitudDeAcceso): NuevaTienda {
  return {
    ...TIENDA_VACIA,
    nombre: solicitud.negocio,
    slug: sugerirSlug(solicitud.negocio),
    duenoNombre: solicitud.nombre,
    duenoEmail: solicitud.email,
    solicitud: solicitud.id,
  };
}

function NuevaTiendaFormulario({
  desdeSolicitud,
  onCreada,
}: {
  desdeSolicitud: SolicitudDeAcceso | null;
  onCreada: (t: TiendaDePlataforma) => void;
}) {
  const [datos, setDatos] = useState<NuevaTienda>(desdeSolicitud ? desde(desdeSolicitud) : TIENDA_VACIA);
  const [slugTocado, setSlugTocado] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [errores, setErrores] = useState<Record<string, string | null>>({});
  const [aviso, setAviso] = useState<{ tipo: "ok" | "error"; texto: string } | null>(null);

  const cambiar = <K extends keyof NuevaTienda>(campo: K, valor: NuevaTienda[K]) =>
    setDatos((actual) => ({
      ...actual,
      [campo]: valor,
      ...(campo === "nombre" && !slugTocado ? { slug: sugerirSlug(String(valor)) } : {}),
    }));

  async function crear(evento: FormEvent) {
    evento.preventDefault();
    setGuardando(true);
    setErrores({});
    setAviso(null);
    try {
      const tienda = await crearTienda(datos);
      onCreada(tienda);
      setDatos(TIENDA_VACIA);
      setSlugTocado(false);
      setAviso({
        tipo: "ok",
        texto: `Creamos ${tienda.nombre}. El dueño ya puede entrar al panel con su correo y la contraseña que definiste.`,
      });
    } catch (error) {
      if (error instanceof ErrorDeApi && Object.keys(error.detalles).length) {
        setErrores(Object.fromEntries(Object.keys(error.detalles).map((c) => [c, error.de(c)])));
      } else {
        setAviso({ tipo: "error", texto: mensajeDe(error) });
      }
    } finally {
      setGuardando(false);
    }
  }

  return (
    <Tarjeta>
      <form onSubmit={crear} noValidate className="flex flex-col gap-3">
        <div>
          <p className="font-jakarta text-[17px] font-bold">Nueva tienda</p>
          <p className="mt-1 text-[13px] text-pizarra">La tienda y la cuenta de su dueño, en un paso.</p>
        </div>
        {datos.solicitud && (
          <p className="rounded-[10px] bg-cielo px-3 py-2 text-[13px] text-acero">
            Desde la solicitud de {datos.nombre}. Al crearla, la solicitud queda como activada.
            Solo falta la contraseña inicial.
          </p>
        )}
        <Campo id="nt-nombre" etiqueta="Nombre de la tienda" value={datos.nombre} onChange={(e) => cambiar("nombre", e.target.value)} error={errores.nombre} />
        <Campo
          id="nt-slug"
          etiqueta="Dirección pública"
          value={datos.slug}
          onChange={(e) => {
            setSlugTocado(true);
            cambiar("slug", sugerirSlug(e.target.value));
          }}
          error={errores.slug}
          ayuda={datos.slug ? `La vitrina quedará en /t/${datos.slug}` : "Solo minúsculas, números y guiones."}
        />
        <div className="grid grid-cols-2 gap-3">
          <label className="text-[13px] font-semibold text-marino">
            Plan
            <select className={CLASE_ENTRADA} value={datos.plan} onChange={(e) => cambiar("plan", e.target.value as Plan)}>
              {PLANES.map((p) => (
                <option key={p.valor} value={p.valor}>
                  {p.nombre}
                </option>
              ))}
            </select>
          </label>
          <label className="text-[13px] font-semibold text-marino">
            Plantilla
            <select
              className={CLASE_ENTRADA}
              value={datos.plantilla}
              onChange={(e) => cambiar("plantilla", e.target.value as Plantilla)}
            >
              {PLANTILLAS.map((p) => (
                <option key={p.valor} value={p.valor}>
                  {p.nombre}
                </option>
              ))}
            </select>
          </label>
        </div>
        <p className="mt-2 text-[13px] font-semibold text-marino">Dueño</p>
        <Campo id="nt-dnombre" etiqueta="Nombre" value={datos.duenoNombre} onChange={(e) => cambiar("duenoNombre", e.target.value)} error={errores.duenoNombre} />
        <Campo
          id="nt-demail"
          etiqueta="Correo"
          type="email"
          value={datos.duenoEmail}
          onChange={(e) => cambiar("duenoEmail", e.target.value)}
          error={errores.duenoEmail}
        />
        <Campo
          id="nt-dclave"
          etiqueta="Contraseña inicial"
          type="text"
          autoComplete="off"
          value={datos.duenoPassword}
          onChange={(e) => cambiar("duenoPassword", e.target.value)}
          error={errores.duenoPassword}
          ayuda="Entrégasela al dueño; podrá cambiarla desde su cuenta."
        />
        <div>
          <Boton type="submit" disabled={guardando || !datos.nombre || !datos.slug || !datos.duenoEmail || !datos.duenoPassword}>
            {guardando ? "Creando…" : "Crear tienda"}
          </Boton>
        </div>
        {aviso && <Aviso tipo={aviso.tipo}>{aviso.texto}</Aviso>}
      </form>
    </Tarjeta>
  );
}

// ── Mensajes ────────────────────────────────────────────────────────────────

/** Lo que escribe el equipo de una tienda cerrada desde la pantalla de inicio de sesión. */
function Mensajes({ onSinLeer }: { onSinLeer: (n: number) => void }) {
  const [mensajes, setMensajes] = useState<MensajeDeTienda[] | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);

  useEffect(() => {
    obtenerMensajes().then(setMensajes, (error) => setFallo(mensajeDe(error)));
  }, []);

  async function alternar(mensaje: MensajeDeTienda) {
    try {
      const actualizado = await marcarMensaje(mensaje.id, !mensaje.leido);
      const lista = (mensajes ?? []).map((m) => (m.id === actualizado.id ? actualizado : m));
      setMensajes(lista);
      onSinLeer(lista.filter((m) => !m.leido).length);
    } catch (error) {
      setFallo(mensajeDe(error));
    }
  }

  if (fallo) return <Error mensaje={fallo} />;
  if (!mensajes) return <Cargando />;
  if (mensajes.length === 0) {
    return (
      <Vacio
        titulo="No hay mensajes"
        detalle="Cuando el equipo de una tienda cerrada te escriba desde el inicio de sesión, aparece acá."
      />
    );
  }

  return (
    <div className="flex flex-col gap-3">
      {mensajes.map((mensaje) => (
        <Tarjeta key={mensaje.id} className={cn("p-5", !mensaje.leido && "border-acero")}>
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="min-w-0 flex-1">
              <p className="font-jakarta text-[16px] font-bold">
                {mensaje.tienda}
                {!mensaje.leido && (
                  <span className="ml-2 rounded-full bg-acero px-2 py-0.5 text-[11px] font-semibold text-white">Nuevo</span>
                )}
              </p>
              <p className="text-[13px] text-pizarra">
                {mensaje.nombre} · {mensaje.email} ·{" "}
                {new Date(mensaje.fecha).toLocaleString("es-CL", { dateStyle: "short", timeStyle: "short" })}
              </p>
              <p className="mt-3 text-[14px] leading-[1.55] whitespace-pre-line text-marino">{mensaje.mensaje}</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <a
                href={`mailto:${mensaje.email}?subject=${encodeURIComponent(`Tu tienda ${mensaje.tienda} en DealCommerce`)}`}
                className="flex h-9 items-center rounded-[10px] bg-acero px-3 text-[13px] font-semibold text-white no-underline hover:bg-acero-hondo hover:no-underline"
              >
                Responder por correo
              </a>
              <Boton variante="secundario" className="h-9 px-3 text-[13px]" onClick={() => alternar(mensaje)}>
                {mensaje.leido ? "Marcar no leído" : "Marcar leído"}
              </Boton>
            </div>
          </div>
        </Tarjeta>
      ))}
    </div>
  );
}

// ── Solicitudes ─────────────────────────────────────────────────────────────

const ESTADOS: { valor: SolicitudDeAcceso["estado"]; nombre: string }[] = [
  { valor: "nueva", nombre: "Nueva" },
  { valor: "contactada", nombre: "Contactada" },
  { valor: "activada", nombre: "Activada" },
  { valor: "descartada", nombre: "Descartada" },
];

function Solicitudes({ onCrearTienda }: { onCrearTienda: (s: SolicitudDeAcceso) => void }) {
  const [solicitudes, setSolicitudes] = useState<SolicitudDeAcceso[] | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);

  useEffect(() => {
    obtenerSolicitudes().then(setSolicitudes, (error) => setFallo(mensajeDe(error)));
  }, []);

  if (fallo) return <Error mensaje={fallo} />;
  if (!solicitudes) return <Cargando />;
  if (solicitudes.length === 0) {
    return <Vacio titulo="No hay solicitudes" detalle="Los negocios que pidan entrar desde la portada aparecen acá." />;
  }

  return (
    <div className="flex flex-col gap-3">
      {solicitudes.map((solicitud) => (
        <Tarjeta key={solicitud.id} className="p-5">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="font-jakarta text-[16px] font-bold">{solicitud.negocio}</p>
              <p className="text-[13px] text-pizarra">
                {solicitud.nombre} · {solicitud.email} · {solicitud.telefono} · {formatearFecha(solicitud.fecha)}
              </p>
              {solicitud.mensaje && <p className="mt-2 text-[14px] text-marino">«{solicitud.mensaje}»</p>}
              {solicitud.estado !== "activada" && solicitud.estado !== "descartada" && (
                <Boton className="mt-3 h-9 px-3 text-[13px]" onClick={() => onCrearTienda(solicitud)}>
                  Crear tienda desde esta solicitud
                </Boton>
              )}
            </div>
            <select
              aria-label={`Estado de la solicitud de ${solicitud.negocio}`}
              className={cn(CLASE_ENTRADA, "mt-0 h-10 w-auto")}
              value={solicitud.estado}
              onChange={async (e) => {
                const actualizada = await cambiarSolicitud(solicitud.id, {
                  estado: e.target.value as SolicitudDeAcceso["estado"],
                });
                setSolicitudes((actual) => actual?.map((s) => (s.id === actualizada.id ? actualizada : s)) ?? null);
              }}
            >
              {ESTADOS.map((estado) => (
                <option key={estado.valor} value={estado.valor}>
                  {estado.nombre}
                </option>
              ))}
            </select>
          </div>
        </Tarjeta>
      ))}
    </div>
  );
}

// ── Registro ────────────────────────────────────────────────────────────────

const ACCIONES = [
  { valor: "", nombre: "Todas las acciones" },
  { valor: "crear", nombre: "Creó" },
  { valor: "modificar", nombre: "Modificó" },
  { valor: "eliminar", nombre: "Eliminó" },
  { valor: "sesion", nombre: "Inició sesión" },
  { valor: "plan", nombre: "Cambió el plan" },
  { valor: "cuenta", nombre: "Cambió su cuenta" },
];

function Registro({ tiendaInicial }: { tiendaInicial: string }) {
  const [tienda, setTienda] = useState(tiendaInicial);
  const [accion, setAccion] = useState("");
  const [texto, setTexto] = useState("");
  const [busqueda, setBusqueda] = useState("");
  const [pagina, setPagina] = useState(1);
  const [datos, setDatos] = useState<PaginaDeRegistros | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);
  const [tiendas, setTiendas] = useState<TiendaDePlataforma[]>([]);
  const [abierto, setAbierto] = useState<number | null>(null);

  useEffect(() => {
    obtenerTiendas().then(setTiendas, () => setTiendas([]));
  }, []);

  const cargar = useCallback(() => {
    obtenerRegistros({ tienda, accion, q: busqueda, pagina }).then(
      (respuesta) => {
        setDatos(respuesta);
        setFallo(null);
      },
      (error) => setFallo(mensajeDe(error)),
    );
  }, [tienda, accion, busqueda, pagina]);
  useEffect(cargar, [cargar]);

  const totalPaginas = datos ? Math.max(1, Math.ceil(datos.count / 50)) : 1;

  return (
    <>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          setPagina(1);
          setBusqueda(texto);
        }}
        className="mb-4 grid gap-3 md:grid-cols-[220px_220px_minmax(0,1fr)_auto] md:items-end"
      >
        <label className="text-[13px] font-semibold text-marino">
          Tienda
          <select
            className={CLASE_ENTRADA}
            value={tienda}
            onChange={(e) => {
              setPagina(1);
              setTienda(e.target.value);
            }}
          >
            <option value="">Todas las tiendas</option>
            {tiendas.map((t) => (
              <option key={t.slug} value={t.slug}>
                {t.nombre}
              </option>
            ))}
          </select>
        </label>
        <label className="text-[13px] font-semibold text-marino">
          Acción
          <select
            className={CLASE_ENTRADA}
            value={accion}
            onChange={(e) => {
              setPagina(1);
              setAccion(e.target.value);
            }}
          >
            {ACCIONES.map((a) => (
              <option key={a.valor} value={a.valor}>
                {a.nombre}
              </option>
            ))}
          </select>
        </label>
        <Campo id="registro-q" etiqueta="Buscar" placeholder="Correo, producto, folio…" value={texto} onChange={(e) => setTexto(e.target.value)} />
        <Boton type="submit">Buscar</Boton>
      </form>

      {fallo && <Error mensaje={fallo} />}
      {!fallo && !datos && <Cargando />}
      {datos && datos.results.length === 0 && <Vacio titulo="Sin actividad con esos filtros" />}

      {datos && datos.results.length > 0 && (
        <Tarjeta className="overflow-x-auto p-0">
          <table className="w-full min-w-[760px] text-left text-[13px]">
            <thead>
              <tr className="border-b border-arena bg-hueso text-[12px] text-pizarra">
                <th className="px-4 py-2.5 font-semibold">Cuándo</th>
                <th className="px-4 py-2.5 font-semibold">Tienda</th>
                <th className="px-4 py-2.5 font-semibold">Quién</th>
                <th className="px-4 py-2.5 font-semibold">Qué hizo</th>
                <th className="px-4 py-2.5" />
              </tr>
            </thead>
            <tbody>
              {datos.results.map((registro) => {
                const conDetalle = Object.keys(registro.detalle ?? {}).length > 0;
                return (
                  <Fragment key={registro.id}>
                    <tr className="border-b border-arena align-top">
                      <td className="px-4 py-2.5 whitespace-nowrap text-pizarra">
                        {new Date(registro.fecha).toLocaleString("es-CL", { dateStyle: "short", timeStyle: "short" })}
                      </td>
                      <td className="px-4 py-2.5">{registro.tienda || "—"}</td>
                      <td className="px-4 py-2.5">{registro.usuario || "—"}</td>
                      <td className="px-4 py-2.5">
                        <span className="font-semibold">{registro.accionNombre}</span> {registro.modelo}
                        {registro.objeto && <span className="text-pizarra"> · {registro.objeto}</span>}
                      </td>
                      <td className="px-4 py-2.5 text-right">
                        {conDetalle && (
                          <button
                            type="button"
                            className="cursor-pointer text-[12px] font-semibold text-acero"
                            onClick={() => setAbierto(abierto === registro.id ? null : registro.id)}
                          >
                            {abierto === registro.id ? "Ocultar" : "Ver cambios"}
                          </button>
                        )}
                      </td>
                    </tr>
                    {abierto === registro.id && conDetalle && (
                      <tr className="border-b border-arena bg-hueso">
                        <td colSpan={5} className="px-4 py-3">
                          <DetalleDeCambios detalle={registro.detalle} />
                        </td>
                      </tr>
                    )}
                  </Fragment>
                );
              })}
            </tbody>
          </table>
          <div className="flex items-center justify-between px-4 py-3 text-[13px]">
            <span className="text-pizarra">{datos.count} registros</span>
            <div className="flex items-center gap-3">
              <button type="button" className="cursor-pointer text-acero disabled:opacity-40" disabled={pagina <= 1} onClick={() => setPagina(pagina - 1)}>
                ← Anterior
              </button>
              <span className="text-pizarra">
                {pagina} de {totalPaginas}
              </span>
              <button
                type="button"
                className="cursor-pointer text-acero disabled:opacity-40"
                disabled={pagina >= totalPaginas}
                onClick={() => setPagina(pagina + 1)}
              >
                Siguiente →
              </button>
            </div>
          </div>
        </Tarjeta>
      )}
    </>
  );
}

function mostrar(valor: unknown): string {
  if (valor === null || valor === undefined || valor === "") return "(vacío)";
  if (typeof valor === "boolean") return valor ? "sí" : "no";
  return String(valor);
}

function DetalleDeCambios({ detalle }: { detalle: PaginaDeRegistros["results"][number]["detalle"] }) {
  return (
    <ul className="flex flex-col gap-1">
      {Object.entries(detalle).map(([campo, cambio]) => {
        const par = cambio as { antes?: unknown; despues?: unknown };
        const esPar = par && typeof par === "object" && "despues" in par;
        return (
          <li key={campo} className="text-[12px]">
            <span className="font-semibold text-marino">{campo}:</span>{" "}
            {esPar ? (
              <>
                <span className="text-pizarra line-through">{mostrar(par.antes)}</span> →{" "}
                <span className="text-marino">{mostrar(par.despues)}</span>
              </>
            ) : (
              <span className="text-marino">{mostrar(cambio)}</span>
            )}
          </li>
        );
      })}
    </ul>
  );
}
