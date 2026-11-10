"use client";

import Image from "next/image";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { Campo } from "@/components/campo";
import { esDuenoDeTienda, useSesion } from "@/components/sesion/usar-sesion";
import { ErrorDeApi } from "@/lib/api/errores";
import { guardarPerfil, obtenerPerfil } from "@/lib/api/perfil-tienda";
import { esHexadecimal, paletaParaFondoClaro } from "@/lib/color";
import type { Paleta } from "@/lib/color";
import type { CambiosDelPerfil, PerfilDeTienda } from "@/lib/tipos-panel";

import { Cabecera, Cargando, Error as Aviso, Tarjeta } from "./piezas";
import { SelectorDeColor } from "./selector-de-color";

/*
 * Tienda y marca.
 *
 * Lo que se ve acá es lo que el comprador va a ver en la vitrina, así que la
 * pantalla muestra una vista previa antes de guardar.
 *
 * El plan Básico solo deja cambiar el nombre y el logo. El candado del resto es
 * cortesía: quien decide es el backend, que rechaza el campo bloqueado aunque
 * llegue por otra vía.
 */

/** Los cuatro colores, con el nombre que les da el contrato. */
const COLORES = [
  { campo: "colorPrimario", etiqueta: "Primario", ayuda: "El color de los botones." },
  { campo: "colorPrimarioHover", etiqueta: "Primario al pasar el mouse", ayuda: "Un tono más claro." },
  { campo: "colorAcento", etiqueta: "Acento", ayuda: "Detalles y enlaces. Va sobre el fondo oscuro." },
  { campo: "colorDestacado", etiqueta: "Destacado", ayuda: "Precios, ofertas y avisos." },
] as const;

type CampoDeColor = (typeof COLORES)[number]["campo"];

/** Los tres que salen del primero. Se pueden corregir uno por uno, pero plegados. */
const DERIVADOS = COLORES.filter(({ campo }) => campo !== "colorPrimario");

export function PantallaTienda() {
  const { sesion, hidratado } = useSesion();
  const puedeEditar = esDuenoDeTienda(sesion);

  const [perfil, setPerfil] = useState<PerfilDeTienda | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);

  // Nada de estado se toca aquí de forma síncrona: el efecto solo dispara la
  // petición, y quien escribe es la respuesta.
  const cargar = useCallback(() => {
    obtenerPerfil()
      .then((perfil) => {
        setPerfil(perfil);
        setFallo(null);
      })
      .catch((error: unknown) => setFallo(mensajeDe(error)));
  }, []);

  useEffect(() => {
    if (hidratado) {
      cargar();
    }
  }, [hidratado, cargar]);

  if (!hidratado || (!perfil && !fallo)) {
    return <Cargando />;
  }

  if (!perfil) {
    return (
      <>
        <Cabecera titulo="Tienda y marca" descripcion="Tu logo, tus colores y tu tipografía." />
        <Aviso mensaje={fallo ?? ""} onReintentar={cargar} />
      </>
    );
  }

  return <Formulario perfil={perfil} puedeEditar={puedeEditar} onGuardado={setPerfil} />;
}

function Formulario({
  perfil,
  puedeEditar,
  onGuardado,
}: {
  perfil: PerfilDeTienda;
  puedeEditar: boolean;
  onGuardado: (perfil: PerfilDeTienda) => void;
}) {
  const [borrador, setBorrador] = useState(perfil);
  const [logo, setLogo] = useState<File | null>(null);
  const [banner, setBanner] = useState<File | null>(null);
  const [guardando, setGuardando] = useState(false);
  const [guardado, setGuardado] = useState(false);
  const [error, setError] = useState<ErrorDeApi | null>(null);

  const marcaAbierta = perfil.puedeEditarLaMarca;
  const bloqueado = (campo: string) => !puedeEditar || (!marcaAbierta && campo !== "nombre");

  function cambiar<C extends keyof PerfilDeTienda>(campo: C, valor: PerfilDeTienda[C]) {
    setBorrador((actual) => ({ ...actual, [campo]: valor }));
    setGuardado(false);
  }

  /** Una elección del selector: los cuatro colores de una sola vez. */
  function aplicarPaleta(paleta: Paleta) {
    setBorrador((actual) => ({
      ...actual,
      colorPrimario: paleta.primario,
      colorPrimarioHover: paleta.hover,
      colorAcento: paleta.acento,
      colorDestacado: paleta.destacado,
    }));
    setGuardado(false);
  }

  async function enviar(evento: React.FormEvent) {
    evento.preventDefault();
    setGuardando(true);
    setError(null);

    const cambios: CambiosDelPerfil = { nombre: borrador.nombre };
    if (logo) cambios.logo = logo;

    if (marcaAbierta) {
      if (banner) cambios.banner = banner;
      for (const { campo } of COLORES) {
        cambios[campo] = borrador[campo];
      }
      cambios.tipografia = borrador.tipografia;
      cambios.whatsapp = borrador.whatsapp;
      cambios.instagram = borrador.instagram;
    }

    try {
      const actualizado = await guardarPerfil(cambios);
      onGuardado(actualizado);
      setBorrador(actualizado);
      setLogo(null);
      setBanner(null);
      setGuardado(true);
    } catch (fallo: unknown) {
      setError(fallo instanceof ErrorDeApi ? fallo : null);
    } finally {
      setGuardando(false);
    }
  }

  return (
    <form onSubmit={enviar} noValidate>
      <Cabecera
        titulo="Tienda y marca"
        descripcion="Así te ven tus clientes. Los cambios se aplican a tu vitrina pública."
        acciones={
          <Link
            href={`/t/${perfil.slug}`}
            target="_blank"
            className="flex h-11 items-center rounded-[12px] border border-niebla px-4 text-[13px] font-semibold text-acero no-underline hover:bg-cielo hover:no-underline"
          >
            Ver mi vitrina
          </Link>
        }
      />

      {!puedeEditar && (
        <p className="mb-6 rounded-[12px] border border-arena bg-white px-4 py-3 text-[13px] text-pizarra">
          Estás viendo el perfil de tu tienda. Cambiarlo es cosa del dueño.
        </p>
      )}

      {!marcaAbierta && puedeEditar && <AvisoDelPlan />}

      <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
        <div className="flex flex-col gap-4">
          <Tarjeta>
            <Titulo>Identidad</Titulo>
            <div className="mt-4 flex flex-col gap-4">
              <Campo
                id="nombre"
                etiqueta="Nombre de la tienda"
                tema="claro"
                valor={borrador.nombre}
                onCambio={(valor) => cambiar("nombre", valor)}
                error={error?.de("nombre")}
              />

              <ArchivoDeImagen
                id="logo"
                etiqueta="Logo"
                ayuda="JPG, PNG o WEBP, hasta 3 MB. Cuadrado se ve mejor."
                actual={borrador.logoActual}
                elegido={logo}
                onElegir={setLogo}
                deshabilitado={!puedeEditar}
                error={error?.de("logo")}
              />

              <ArchivoDeImagen
                id="banner"
                etiqueta="Banner"
                ayuda="La imagen ancha del encabezado de tu vitrina."
                actual={borrador.bannerActual}
                elegido={banner}
                onElegir={setBanner}
                deshabilitado={bloqueado("banner")}
                error={error?.de("banner")}
              />
            </div>
          </Tarjeta>

          <Tarjeta>
            <Titulo>Colores</Titulo>
            <p className="mt-1 text-[13px] text-pizarra">
              Elige una plantilla y armamos los otros tres colores. Se usan los cuatro o ninguno:
              con la paleta a medias, tu vitrina usa la de DealCommerce.
            </p>

            <div className="mt-4">
              <label htmlFor="colorPrimario" className="text-[13px] font-semibold text-marino">
                Color de tu tienda
              </label>

              <div className="mt-2">
                <SelectorDeColor
                  id="colorPrimario"
                  valor={borrador.colorPrimario}
                  onPaleta={aplicarPaleta}
                  onTexto={(texto) => cambiar("colorPrimario", texto)}
                  deshabilitado={bloqueado("colorPrimario")}
                  error={error?.de("colorPrimario")}
                />
              </div>

              {error?.de("colorPrimario") ? (
                <p className="mt-1.5 text-xs font-medium text-ambar-hondo">
                  {error.de("colorPrimario")}
                </p>
              ) : (
                <p className="mt-1.5 text-xs text-pizarra">El color de los botones.</p>
              )}
            </div>

            <details className="mt-4 border-t border-arena pt-4">
              <summary className="cursor-pointer text-[13px] font-semibold text-acero">
                Ajustar los otros tres por separado
              </summary>

              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                {DERIVADOS.map(({ campo, etiqueta, ayuda }) => (
                  <ColorDeLaMarca
                    key={campo}
                    campo={campo}
                    etiqueta={etiqueta}
                    ayuda={ayuda}
                    valor={borrador[campo]}
                    onCambio={(valor) => cambiar(campo, valor)}
                    deshabilitado={bloqueado(campo)}
                    error={error?.de(campo)}
                  />
                ))}
              </div>
            </details>
          </Tarjeta>

          <Tarjeta>
            <Titulo>Tipografía</Titulo>
            <p className="mt-1 text-[13px] text-pizarra">
              De esta lista y no otra. Una fuente escrita a mano correría en la página de las demás
              tiendas.
            </p>

            <div className="mt-4 flex flex-wrap gap-2">
              {borrador.tipografiasDisponibles.map((fuente) => (
                <button
                  key={fuente.valor}
                  type="button"
                  disabled={bloqueado("tipografia")}
                  onClick={() => cambiar("tipografia", fuente.valor)}
                  aria-pressed={borrador.tipografia === fuente.valor}
                  className={
                    borrador.tipografia === fuente.valor
                      ? "h-11 cursor-pointer rounded-[12px] border border-acero bg-cielo px-4 text-[14px] font-semibold text-acero disabled:cursor-not-allowed"
                      : "h-11 cursor-pointer rounded-[12px] border border-arena px-4 text-[14px] text-marino hover:bg-hueso disabled:cursor-not-allowed disabled:opacity-60"
                  }
                >
                  {fuente.nombre}
                </button>
              ))}
            </div>
          </Tarjeta>

          <Tarjeta>
            <Titulo>Contacto</Titulo>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <Campo
                id="whatsapp"
                etiqueta="WhatsApp"
                tema="claro"
                requerido={false}
                placeholder="https://wa.me/56912345678"
                valor={borrador.whatsapp}
                onCambio={(valor) => cambiar("whatsapp", valor)}
                error={error?.de("whatsapp")}
              />
              <Campo
                id="instagram"
                etiqueta="Instagram"
                tema="claro"
                requerido={false}
                placeholder="https://instagram.com/tu-tienda"
                valor={borrador.instagram}
                onCambio={(valor) => cambiar("instagram", valor)}
                error={error?.de("instagram")}
              />
            </div>
          </Tarjeta>
        </div>

        <VistaPrevia perfil={borrador} logo={logo} />
      </div>

      {puedeEditar && (
        <div className="mt-5 flex flex-wrap items-center gap-3">
          <button
            type="submit"
            disabled={guardando}
            className="h-11 cursor-pointer rounded-[12px] bg-acero px-6 text-sm font-semibold text-white transition-colors hover:bg-acero-hondo disabled:cursor-not-allowed disabled:opacity-50"
          >
            {guardando ? "Guardando…" : "Guardar cambios"}
          </button>

          {guardado && (
            <p role="status" className="text-[13px] font-semibold text-acero">
              Listo: tu vitrina ya se ve así.
            </p>
          )}

          {error && !tieneDetalles(error) && (
            <p role="alert" className="text-[13px] text-ambar-hondo">
              {error.message}
            </p>
          )}
        </div>
      )}
    </form>
  );
}

function Titulo({ children }: { children: React.ReactNode }) {
  return <h2 className="font-jakarta text-[17px] font-bold text-marino">{children}</h2>;
}

function AvisoDelPlan() {
  return (
    <p className="mb-6 flex flex-wrap items-center gap-2 rounded-[12px] border border-niebla bg-cielo px-4 py-3 text-[13px] text-marino">
      <span className="font-semibold">Plan Básico:</span>
      <span>puedes cambiar el nombre y el logo. El resto de la marca viene con Premium.</span>
      <Link href="/panel/plan" className="font-semibold text-acero">
        Ver los planes
      </Link>
    </p>
  );
}

function ArchivoDeImagen({
  id,
  etiqueta,
  ayuda,
  actual,
  elegido,
  onElegir,
  deshabilitado,
  error,
}: {
  id: string;
  etiqueta: string;
  ayuda: string;
  actual: { url: string; alt: string } | null;
  elegido: File | null;
  onElegir: (archivo: File | null) => void;
  deshabilitado: boolean;
  error?: string | null;
}) {
  return (
    <div>
      <label htmlFor={id} className="text-[13px] font-semibold text-marino">
        {etiqueta}
      </label>

      <div className="mt-2 flex items-center gap-4">
        {actual && !elegido && (
          <Image
            src={actual.url}
            alt={actual.alt}
            width={56}
            height={56}
            className="size-14 shrink-0 rounded-[10px] border border-arena object-cover"
          />
        )}

        <input
          id={id}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          disabled={deshabilitado}
          aria-invalid={Boolean(error)}
          onChange={(evento) => onElegir(evento.target.files?.[0] ?? null)}
          className="block w-full cursor-pointer rounded-[12px] border border-dashed border-arena-honda bg-hueso p-3 text-[13px] text-pizarra file:mr-3 file:cursor-pointer file:rounded-[10px] file:border-0 file:bg-acero file:px-3 file:py-1.5 file:text-[13px] file:font-semibold file:text-white disabled:cursor-not-allowed disabled:opacity-60"
        />
      </div>

      {error ? (
        <p className="mt-1.5 text-xs font-medium text-ambar-hondo">{error}</p>
      ) : (
        <p className="mt-1.5 text-xs text-pizarra">{ayuda}</p>
      )}
    </div>
  );
}

function ColorDeLaMarca({
  campo,
  etiqueta,
  ayuda,
  valor,
  onCambio,
  deshabilitado,
  error,
}: {
  campo: CampoDeColor;
  etiqueta: string;
  ayuda: string;
  valor: string;
  onCambio: (valor: string) => void;
  deshabilitado: boolean;
  error?: string | null;
}) {
  return (
    <div>
      <label htmlFor={campo} className="text-[13px] font-semibold text-marino">
        {etiqueta}
      </label>

      <div className="mt-2 flex items-center gap-2.5">
        <span
          aria-hidden="true"
          style={esHexadecimal(valor) ? { background: valor } : undefined}
          className="size-11 shrink-0 rounded-[10px] border border-arena bg-hueso"
        />
        <input
          id={campo}
          type="text"
          value={valor}
          disabled={deshabilitado}
          maxLength={7}
          placeholder="#7C3AED"
          aria-invalid={Boolean(error)}
          onChange={(evento) => onCambio(evento.target.value)}
          className={
            "h-11 w-full rounded-[12px] border bg-white px-3 font-mono text-[14px] text-marino uppercase outline-none disabled:cursor-not-allowed disabled:opacity-60 " +
            (error ? "border-ambar" : "border-niebla focus-visible:border-acero")
          }
        />
      </div>

      {error ? (
        <p className="mt-1.5 text-xs font-medium text-ambar-hondo">{error}</p>
      ) : (
        <p className="mt-1.5 text-xs text-pizarra">{ayuda}</p>
      )}
    </div>
  );
}

/**
 * Cómo queda la vitrina con estos colores, antes de guardar.
 *
 * Es una muestra y no la vitrina de verdad: alcanza para decidir una paleta sin
 * publicarla. Los colores se aplican solo si pasan el mismo formato que exige
 * el backend; un valor a medio escribir no se inyecta en el estilo.
 */
/*
 * Los dos fondos de la vitrina, con los mismos valores que la hoja de estilos.
 * Si allá cambian, acá también: es una muestra, y una muestra que miente no
 * sirve para elegir.
 */
const TEMAS = [
  { nombre: "oscuro", etiqueta: "Oscuro", pagina: "#0b0a0f", tarjeta: "#16141d", texto: "#f5f3f7" },
  { nombre: "claro", etiqueta: "Claro", pagina: "#f7f5f0", tarjeta: "#ffffff", texto: "#1a1820" },
] as const;

function VistaPrevia({ perfil, logo }: { perfil: PerfilDeTienda; logo: File | null }) {
  // Los mismos valores de reserva que usa la vitrina cuando la tienda no eligió
  // paleta. Antes acá había otros tres y la muestra no se parecía a la vitrina.
  const oscura: Paleta = {
    primario: esHexadecimal(perfil.colorPrimario) ? perfil.colorPrimario : "#7c3aed",
    hover: esHexadecimal(perfil.colorPrimarioHover) ? perfil.colorPrimarioHover : "#8b5cf6",
    acento: esHexadecimal(perfil.colorAcento) ? perfil.colorAcento : "#a78bfa",
    destacado: esHexadecimal(perfil.colorDestacado) ? perfil.colorDestacado : "#c9a227",
  };

  const paletas = { oscuro: oscura, claro: paletaParaFondoClaro(oscura) };

  return (
    <aside className="lg:sticky lg:top-6 lg:self-start">
      <Tarjeta>
        <Titulo>Vista previa</Titulo>
        <p className="mt-1 text-[13px] text-pizarra">
          Tu vitrina en los dos temas: el comprador elige cuál ve, así que tu color tiene que
          funcionar en ambos. {logo && "El logo nuevo se ve al guardar."}
        </p>

        <div className="mt-4 flex flex-col gap-3">
          {TEMAS.map((tema) => (
            <Muestra
              key={tema.nombre}
              tema={tema}
              paleta={paletas[tema.nombre]}
              nombre={perfil.nombre}
              logo={perfil.logoActual}
            />
          ))}
        </div>
      </Tarjeta>
    </aside>
  );
}

function Muestra({
  tema,
  paleta,
  nombre,
  logo,
}: {
  tema: (typeof TEMAS)[number];
  paleta: Paleta;
  nombre: string;
  logo: PerfilDeTienda["logoActual"];
}) {
  return (
    <div className="overflow-hidden rounded-[12px] border border-arena" style={{ background: tema.pagina }}>
      <div className="flex items-center gap-2.5 px-4 py-3" style={{ background: paleta.primario }}>
        {logo && (
          <Image
            src={logo.url}
            alt=""
            width={24}
            height={24}
            className="size-6 rounded-full border border-white/40 object-cover"
          />
        )}
        <span className="truncate text-[14px] font-bold text-white">{nombre}</span>
        <span className="ml-auto shrink-0 text-[10px] font-semibold tracking-[.08em] text-white/70 uppercase">
          {tema.etiqueta}
        </span>
      </div>

      <div className="p-4" style={{ background: tema.tarjeta }}>
        <p className="text-[13px] font-semibold" style={{ color: tema.texto }}>
          Un producto
        </p>
        <p className="mt-0.5 text-[12px]" style={{ color: paleta.acento }}>
          Categoría de ejemplo
        </p>
        <p className="mt-2 font-serif text-[18px] font-semibold" style={{ color: paleta.destacado }}>
          $19.990
        </p>
        <span
          className="mt-2 inline-block rounded-full border px-2 py-0.5 text-[11px] font-semibold"
          style={{ color: paleta.destacado, borderColor: `${paleta.destacado}80` }}
        >
          Oferta
        </span>
        {/*
          Texto blanco fijo, igual que la vitrina. No se corrige solo a un tono
          legible a propósito: si el color elegido deja el botón ilegible, el
          dueño tiene que verlo acá, que es donde el selector se lo advierte.
        */}
        <span
          className="mt-3 block rounded-[10px] py-2 text-center text-[13px] font-semibold text-white"
          style={{ background: paleta.primario }}
        >
          Agregar
        </span>
      </div>
    </div>
  );
}

function tieneDetalles(error: ErrorDeApi): boolean {
  return Object.keys(error.detalles).length > 0;
}

function mensajeDe(error: unknown): string {
  return error instanceof Error ? error.message : "No pudimos cargar tu perfil.";
}
