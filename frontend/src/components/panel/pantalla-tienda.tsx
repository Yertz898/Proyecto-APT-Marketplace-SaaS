"use client";

import Image from "next/image";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { Campo } from "@/components/campo";
import { esDuenoDeTienda, useSesion } from "@/components/sesion/usar-sesion";
import { ErrorDeApi } from "@/lib/api/errores";
import { guardarPerfil, obtenerPerfil } from "@/lib/api/perfil-tienda";
import type { CambiosDelPerfil, PerfilDeTienda } from "@/lib/tipos-panel";

import { Cabecera, Cargando, Error as Aviso, Tarjeta } from "./piezas";

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
  { campo: "colorPrimarioHover", etiqueta: "Primario al pasar el mouse", ayuda: "Un tono más oscuro." },
  { campo: "colorAcento", etiqueta: "Acento", ayuda: "Detalles y enlaces." },
  { campo: "colorDestacado", etiqueta: "Destacado", ayuda: "Ofertas y avisos." },
] as const;

type CampoDeColor = (typeof COLORES)[number]["campo"];

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
              En hexadecimal, como #7C3AED. Se usan los cuatro o ninguno: con la paleta a medias, tu
              vitrina usa la de DealCommerce.
            </p>

            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              {COLORES.map(({ campo, etiqueta, ayuda }) => (
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
function VistaPrevia({ perfil, logo }: { perfil: PerfilDeTienda; logo: File | null }) {
  const primario = esHexadecimal(perfil.colorPrimario) ? perfil.colorPrimario : "#1f4e79";
  const acento = esHexadecimal(perfil.colorAcento) ? perfil.colorAcento : "#4a5468";
  const destacado = esHexadecimal(perfil.colorDestacado) ? perfil.colorDestacado : "#e0a526";

  return (
    <aside className="lg:sticky lg:top-6 lg:self-start">
      <Tarjeta>
        <Titulo>Vista previa</Titulo>
        <p className="mt-1 text-[13px] text-pizarra">
          Una muestra de tu vitrina. {logo && "El logo nuevo se ve al guardar."}
        </p>

        <div className="mt-4 overflow-hidden rounded-[12px] border border-arena">
          <div className="flex items-center gap-2.5 px-4 py-3" style={{ background: primario }}>
            {perfil.logoActual && (
              <Image
                src={perfil.logoActual.url}
                alt=""
                width={24}
                height={24}
                className="size-6 rounded-full border border-white/40 object-cover"
              />
            )}
            <span className="truncate text-[14px] font-bold text-white">{perfil.nombre}</span>
          </div>

          <div className="bg-white p-4">
            <p className="text-[13px] font-semibold text-marino">Un producto</p>
            <p className="mt-0.5 text-[12px]" style={{ color: acento }}>
              Categoría de ejemplo
            </p>
            <p className="mt-2 text-[15px] font-extrabold text-marino">$19.990</p>
            <span
              className="mt-2 inline-block rounded-full px-2 py-0.5 text-[11px] font-semibold text-white"
              style={{ background: destacado }}
            >
              Oferta
            </span>
            <span
              className="mt-3 block rounded-[10px] py-2 text-center text-[13px] font-semibold text-white"
              style={{ background: primario }}
            >
              Agregar
            </span>
          </div>
        </div>
      </Tarjeta>
    </aside>
  );
}

/** El mismo formato que exige el backend: seis dígitos y nada más. */
function esHexadecimal(valor: string): boolean {
  return /^#[0-9a-fA-F]{6}$/.test(valor);
}

function tieneDetalles(error: ErrorDeApi): boolean {
  return Object.keys(error.detalles).length > 0;
}

function mensajeDe(error: unknown): string {
  return error instanceof Error ? error.message : "No pudimos cargar tu perfil.";
}
