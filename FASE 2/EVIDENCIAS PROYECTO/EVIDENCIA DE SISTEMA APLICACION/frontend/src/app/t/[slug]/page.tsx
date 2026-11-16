import { CalendarDays, Gem, Package, Scale } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import type { ReactNode } from "react";

import { Carrusel, Diapositiva } from "@/components/tienda/carrusel";
import { TarjetaProducto } from "@/components/tienda/tarjeta-producto";
import { obtenerAgenda } from "@/lib/api/agenda";
import { obtenerDestacados, obtenerFormasDeVenta } from "@/lib/api/catalogo";
import { obtenerIdentidadTienda } from "@/lib/api/tienda";
import type { FormaDeVenta, IdentidadTienda, Producto } from "@/lib/tipos";

/**
 * Portada de la tienda pública.
 *
 * Tiene una presentación, los carruseles con lo más vendido y lo nuevo, y
 * accesos por forma de venta. Cómo se ordena todo eso lo decide la plantilla
 * que eligió la tienda; el contenido es siempre el mismo.
 *
 * Nada se inventa: sin ventas no hay carrusel de más vendidos, y sin banner
 * la portada se arma con el nombre y los colores de la tienda.
 */
export default async function InicioTienda({ params }: PageProps<"/t/[slug]">) {
  const { slug } = await params;
  const [tienda, destacados, formas, agenda] = await Promise.all([
    obtenerIdentidadTienda(slug),
    obtenerDestacados(slug),
    obtenerFormasDeVenta(slug),
    obtenerAgenda(slug, { dias: 1 }),
  ]);

  if (!tienda) {
    notFound();
  }

  const base = `/t/${slug}`;
  const plantilla = tienda.plantilla ?? "clasica";
  const conAgenda = agenda !== null;

  // Lo que la portada dice de la tienda sale de sus datos, no de un texto fijo.
  const todos = [...destacados.masVendidos, ...destacados.nuevos];
  const conTramos = todos.some((p) => p.tramos.length > 0);
  const destacado = todos.find((p) => p.foto) ?? null;

  const masVendidos = destacados.masVendidos.length > 0 && (
    <FilaDeProductos titulo="Lo más vendido" productos={destacados.masVendidos} base={base} slug={slug} />
  );
  const nuevos = destacados.nuevos.length > 0 && (
    <FilaDeProductos titulo="Recién llegados" productos={destacados.nuevos} base={base} slug={slug} />
  );

  return (
    <main className="flex flex-1 flex-col gap-14 pb-16 lg:gap-20">
      {plantilla === "moderna" ? (
        <PortadaModerna tienda={tienda} base={base} />
      ) : plantilla === "minimal" ? (
        <PortadaMinimal tienda={tienda} base={base} />
      ) : (
        <PortadaClasica
          tienda={tienda}
          base={base}
          formas={formas}
          conTramos={conTramos}
          conAgenda={conAgenda}
          destacado={destacado}
        />
      )}

      {plantilla === "moderna" && destacados.masVendidos.length > 0 ? (
        <GrillaDestacada productos={destacados.masVendidos} base={base} slug={slug} />
      ) : (
        masVendidos
      )}

      {(formas.length > 1 || conAgenda) && <ComoVendemos formas={formas} base={base} conAgenda={conAgenda} />}

      {nuevos}

      <Contacto tienda={tienda} base={base} />
    </main>
  );
}

// ── Portadas ────────────────────────────────────────────────────────────────

function BotonCatalogo({ base, children = "Ver el catálogo" }: { base: string; children?: ReactNode }) {
  return (
    <Link
      href={`${base}/productos`}
      className="inline-flex h-12 items-center rounded-full bg-violeta px-7 text-sm font-semibold text-white transition-colors hover:bg-violeta-hover hover:no-underline"
    >
      {children}
    </Link>
  );
}

const FRASE_DE_FORMA: Record<string, string> = { unidad: "por unidad", lote: "por lote", peso: "por gramo" };

/** «Compra por lote o por gramo»: cómo vende la tienda, dicho desde sus formas de venta. */
function comoVende(formas: FormaDeVenta[]): string {
  const frases = formas.map((f) => FRASE_DE_FORMA[f.valor] ?? f.nombre.toLowerCase());
  if (frases.length === 0) return "Recorre el catálogo";
  if (frases.length === 1) return `Compra ${frases.at(0)}`;
  return `Compra ${frases.slice(0, -1).join(", ")} o ${frases.at(-1)}`;
}

/**
 * La portada clásica: una tarjeta con la presentación de la tienda y, al lado,
 * un producto destacado con foto.
 *
 * El texto de presentación es el «Sobre tu tienda» del pie si el dueño lo
 * escribió; si no, se arma con cómo vende. Las etiquetas también salen de los
 * datos: «Precios por tramo» solo si hay tramos, «Cierre por WhatsApp» solo si
 * la tienda cargó su WhatsApp.
 */
function PortadaClasica({
  tienda,
  base,
  formas,
  conTramos,
  conAgenda,
  destacado,
}: {
  tienda: IdentidadTienda;
  base: string;
  formas: FormaDeVenta[];
  conTramos: boolean;
  conAgenda: boolean;
  destacado: Producto | null;
}) {
  const presentacion =
    tienda.pie?.descripcion ||
    `${comoVende(formas)}${conTramos ? " con precios escalonados: mientras más llevas, menos pagas." : "."}`;

  const etiquetas = [
    conTramos && "Precios por tramo",
    formas.length > 0 && `Venta ${formas.map((f) => FRASE_DE_FORMA[f.valor] ?? f.nombre.toLowerCase()).join(" y ")}`,
    tienda.redes.whatsapp && "Cierre por WhatsApp",
    conAgenda && "Visitas con hora",
  ].filter((e): e is string => Boolean(e));

  const imagen = destacado?.foto ?? tienda.banner;

  return (
    <section className="mx-auto w-full max-w-[1280px] px-5 pt-8 lg:px-6 lg:pt-10">
      <div
        className={`grid gap-6 overflow-hidden rounded-[28px] border border-lila/15 bg-gradient-to-br from-violeta/35 via-tinta to-tinta p-6 sm:p-8 lg:p-10 ${imagen ? "lg:grid-cols-[1.05fr_1fr] lg:items-center" : ""}`}
      >
        <div>
          <p className="text-[12px] font-semibold tracking-[0.2em] text-lila uppercase">Bienvenida</p>
          <h1 className="mt-3 font-serif text-[44px] leading-[1.05] text-texto lg:text-[64px]">{tienda.nombre}</h1>
          <p className="mt-4 max-w-[520px] text-[16px] leading-[1.6] text-texto-suave">{presentacion}</p>

          <div className="mt-7 flex flex-wrap gap-3">
            <BotonCatalogo base={base} />
            {conAgenda && (
              <Link
                href={`${base}/agenda`}
                className="inline-flex h-12 items-center gap-2 rounded-full border border-lila/40 px-6 text-sm font-semibold text-texto transition-colors hover:bg-violeta/15 hover:no-underline"
              >
                <CalendarDays size={17} aria-hidden="true" />
                Agendar visita
              </Link>
            )}
          </div>

          {etiquetas.length > 0 && (
            <ul className="mt-6 flex list-none flex-wrap gap-2 p-0">
              {etiquetas.map((etiqueta) => (
                <li key={etiqueta} className="rounded-full border border-lila/25 px-3.5 py-1.5 text-[12px] text-texto-suave">
                  {etiqueta}
                </li>
              ))}
            </ul>
          )}
        </div>

        {imagen && (
          <TarjetaDestacada base={base} producto={destacado} imagen={imagen} conTramos={conTramos} nombreTienda={tienda.nombre} />
        )}
      </div>
    </section>
  );
}

/** El producto con foto que la portada clásica pone al lado de la presentación. */
function TarjetaDestacada({
  base,
  producto,
  imagen,
  conTramos,
  nombreTienda,
}: {
  base: string;
  producto: Producto | null;
  imagen: { url: string; alt: string };
  conTramos: boolean;
  nombreTienda: string;
}) {
  const contenido = (
    <div className="relative aspect-[4/3] overflow-hidden rounded-[20px] border border-lila/15">
      <Image src={imagen.url} alt={imagen.alt} fill priority sizes="(min-width: 1024px) 560px, 100vw" className="object-cover" />
      <div className="absolute inset-0 bg-gradient-to-t from-black/75 via-black/10 to-transparent" />
      {conTramos && (
        <span className="absolute top-4 right-4 rounded-full border border-oro/50 bg-black/45 px-3 py-1 text-[12px] font-medium text-oro backdrop-blur-sm">
          Descuentos por volumen
        </span>
      )}
      <div className="absolute right-5 bottom-5 left-5">
        <p className="text-[11px] font-semibold tracking-[0.2em] text-lila uppercase">{producto ? "Destacado" : nombreTienda}</p>
        {producto && <p className="mt-1 font-serif text-[24px] leading-[1.15] text-white">{producto.nombre}</p>}
      </div>
    </div>
  );

  if (!producto) return contenido;
  return (
    <Link href={`${base}/productos/${encodeURIComponent(producto.codigo)}`} className="block hover:no-underline">
      {contenido}
    </Link>
  );
}

function PortadaModerna({ tienda, base }: { tienda: IdentidadTienda; base: string }) {
  return (
    <section className="mx-auto grid w-full max-w-[1280px] items-center gap-8 px-5 pt-10 lg:grid-cols-2 lg:px-6 lg:pt-14">
      <div>
        <span className="inline-flex rounded-full bg-violeta/15 px-3 py-1 text-[12px] font-semibold text-lila">
          Compra directo a la tienda
        </span>
        <h1 className="mt-4 font-serif text-[44px] leading-[1.02] text-texto lg:text-[64px]">{tienda.nombre}</h1>
        <p className="mt-4 max-w-[460px] text-[16px] leading-[1.6] text-texto-suave">
          Precios que bajan mientras más llevas. Arma tu pedido y lo coordinamos contigo por WhatsApp.
        </p>
        <div className="mt-7 flex flex-wrap gap-3">
          <BotonCatalogo base={base}>Comprar ahora</BotonCatalogo>
        </div>
      </div>
      <div className="relative aspect-[4/3] overflow-hidden rounded-[18px] bg-gradient-to-br from-violeta/50 to-lila/20">
        {tienda.banner && (
          <Image src={tienda.banner.url} alt={tienda.banner.alt} fill priority sizes="(min-width: 1024px) 640px, 100vw" className="object-cover" />
        )}
      </div>
    </section>
  );
}

function PortadaMinimal({ tienda, base }: { tienda: IdentidadTienda; base: string }) {
  return (
    <section className="mx-auto w-full max-w-[1100px] px-5 pt-16 text-center lg:pt-24">
      <h1 className="font-serif text-[40px] leading-[1.1] text-texto lg:text-[60px]">{tienda.nombre}</h1>
      <div className="mt-7">
        <BotonCatalogo base={base} />
      </div>
      {tienda.banner && (
        <div className="relative mt-12 aspect-[21/9] overflow-hidden rounded-[18px]">
          <Image src={tienda.banner.url} alt={tienda.banner.alt} fill priority sizes="(min-width: 1100px) 1100px, 100vw" className="object-cover" />
        </div>
      )}
    </section>
  );
}

// ── Secciones ───────────────────────────────────────────────────────────────

function FilaDeProductos({
  titulo,
  productos,
  base,
  slug,
}: {
  titulo: string;
  productos: Producto[];
  base: string;
  slug: string;
}) {
  return (
    <Carrusel
      titulo={titulo}
      accion={
        <Link href={`${base}/productos`} className="mr-2 text-[14px] font-semibold text-lila">
          Ver todo
        </Link>
      }
    >
      {productos.map((producto) => (
        <Diapositiva key={producto.codigo}>
          <TarjetaProducto slugTienda={slug} producto={producto} />
        </Diapositiva>
      ))}
    </Carrusel>
  );
}

/** La plantilla moderna muestra sus más vendidos en grilla, con el primero destacado. */
function GrillaDestacada({ productos, base, slug }: { productos: Producto[]; base: string; slug: string }) {
  return (
    <section className="mx-auto w-full max-w-[1280px] px-5 lg:px-6">
      <div className="mb-5 flex items-end justify-between">
        <h2 className="font-serif text-[28px] text-texto lg:text-[34px]">Lo más vendido</h2>
        <Link href={`${base}/productos`} className="text-[14px] font-semibold text-lila">
          Ver todo
        </Link>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {productos.slice(0, 8).map((producto) => (
          <TarjetaProducto key={producto.codigo} slugTienda={slug} producto={producto} />
        ))}
      </div>
    </section>
  );
}

const DESCRIPCION_DE_FORMA: Record<string, string> = {
  unidad: "Elige pieza por pieza lo que te gusta.",
  lote: "Paquetes ya armados, listos para revender.",
  peso: "Cotiza por gramo, con precios que bajan por volumen.",
};

const LINK_DE_FORMA: Record<string, string> = {
  unidad: "Ver piezas",
  lote: "Ver lotes",
  peso: "Ver productos por gramo",
};

function IconoDeForma({ valor }: { valor: string }) {
  const props = { size: 20, strokeWidth: 1.7, "aria-hidden": true } as const;
  if (valor === "peso") return <Scale {...props} />;
  if (valor === "lote") return <Package {...props} />;
  return <Gem {...props} />;
}

function TarjetaDeCompra({ href, icono, titulo, detalle, accion }: { href: string; icono: ReactNode; titulo: string; detalle: string; accion: string }) {
  return (
    <Link
      href={href}
      className="group flex flex-col rounded-[18px] border border-lila/12 bg-superficie p-6 transition-colors hover:border-lila/45 hover:no-underline"
    >
      <span className="flex size-11 items-center justify-center rounded-xl border border-lila/30 bg-violeta/15 text-lila">{icono}</span>
      <span className="mt-5 block font-serif text-[22px] text-texto">{titulo}</span>
      <span className="mt-1 block flex-1 text-[14px] leading-[1.55] text-texto-suave">{detalle}</span>
      <span className="mt-5 inline-block text-[13px] font-semibold text-oro group-hover:underline">{accion} →</span>
    </Link>
  );
}

function ComoVendemos({ formas, base, conAgenda }: { formas: FormaDeVenta[]; base: string; conAgenda: boolean }) {
  return (
    <section className="mx-auto w-full max-w-[1280px] px-5 lg:px-6">
      <h2 className="mb-5 font-serif text-[28px] text-texto lg:text-[34px]">Cómo quieres comprar</h2>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {formas.map((forma) => (
          <TarjetaDeCompra
            key={forma.valor}
            href={`${base}/productos?forma=${forma.valor}`}
            icono={<IconoDeForma valor={forma.valor} />}
            titulo={forma.nombre}
            detalle={DESCRIPCION_DE_FORMA[forma.valor] ?? ""}
            accion={LINK_DE_FORMA[forma.valor] ?? "Ver productos"}
          />
        ))}
        {conAgenda && (
          <TarjetaDeCompra
            href={`${base}/agenda`}
            icono={<CalendarDays size={20} strokeWidth={1.7} aria-hidden="true" />}
            titulo="Agendar una visita"
            detalle="Elige día y hora para ver los productos en persona."
            accion="Agendar"
          />
        )}
      </div>
    </section>
  );
}

function Contacto({ tienda, base }: { tienda: IdentidadTienda; base: string }) {
  if (!tienda.redes.whatsapp && !tienda.redes.instagram) {
    return null;
  }
  return (
    <section className="mx-auto w-full max-w-[1280px] px-5 lg:px-6">
      <div className="flex flex-col items-start justify-between gap-5 rounded-[18px] bg-violeta/12 p-8 lg:flex-row lg:items-center lg:p-10">
        <div>
          <p className="font-serif text-[26px] text-texto">¿Tienes dudas antes de comprar?</p>
          <p className="mt-1 text-[15px] text-texto-suave">Escríbenos y te ayudamos a armar tu pedido.</p>
        </div>
        <div className="flex flex-wrap gap-3">
          {tienda.redes.whatsapp && (
            <a
              href={tienda.redes.whatsapp}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex h-12 items-center rounded-full bg-violeta px-6 text-sm font-semibold text-white hover:bg-violeta-hover hover:no-underline"
            >
              Escribir por WhatsApp
            </a>
          )}
          {tienda.redes.instagram && (
            <a
              href={tienda.redes.instagram}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex h-12 items-center rounded-full border border-lila/40 px-6 text-sm font-semibold text-texto hover:bg-violeta/15 hover:no-underline"
            >
              Ver Instagram
            </a>
          )}
          <Link
            href={`${base}/productos`}
            className="inline-flex h-12 items-center rounded-full border border-lila/40 px-6 text-sm font-semibold text-texto hover:bg-violeta/15 hover:no-underline"
          >
            Ir al catálogo
          </Link>
        </div>
      </div>
    </section>
  );
}
