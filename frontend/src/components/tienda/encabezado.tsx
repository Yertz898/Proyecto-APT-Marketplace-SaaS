"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import type { Categoria, ContenidoTienda } from "@/lib/tipos";
import { cn } from "@/lib/utils";

import { ContadorCarrito } from "./carrito";
import { EncabezadoMovil } from "./encabezado-movil";
import { IconoCategoria, IconoFlechaAbajo, IconoLupa } from "./iconos";
import { Marca } from "./marca";

type Props = {
  tienda: ContenidoTienda;
  categorias: Categoria[];
};

/*
 * Encabezado de la tienda pública (mockup 1A, 1B y 1C; el móvil está en 1D).
 *
 * Los elementos marcados con `data-pendiente` llevan a pantallas que todavía no
 * están diseñadas: se ven y reaccionan igual que en el mockup, pero no navegan.
 *
 * El menú de Productos se abre con el mouse, como en el mockup, y también al
 * llegar con el teclado, para que se pueda usar sin mouse.
 */
export function Encabezado({ tienda, categorias }: Props) {
  const ruta = usePathname();
  const base = `/t/${tienda.slug}`;
  const enInicio = ruta === base;
  const enFicha = ruta.startsWith(`${base}/productos/`);
  const enProductos = enFicha || ruta.startsWith(`${base}/catalogo`);

  return (
    <>
      <header className="relative z-40 hidden border-b border-lila/14 bg-tinta/74 backdrop-blur-[16px] lg:block">
        <div className="mx-auto flex h-[78px] max-w-[1280px] items-center gap-10 px-6">
          <Marca tienda={tienda} lugar="encabezado" />

          <nav aria-label="Principal" className="flex items-center gap-[30px] text-sm text-texto-suave">
            <Link href={base} className={cn("transition-colors hover:text-texto", enInicio && "text-texto")}>
              Inicio
            </Link>

            <div className="group/productos relative py-[26px]">
              <button
                type="button"
                className={cn(
                  "flex cursor-default items-center gap-1.5 bg-transparent transition-colors",
                  enProductos
                    ? "text-lila"
                    : "group-hover/productos:text-texto group-focus-within/productos:text-texto",
                )}
              >
                Productos
                <IconoFlechaAbajo />
              </button>

              <div className="invisible absolute top-[70px] -left-[18px] w-[300px] -translate-y-1.5 rounded-[14px] border border-lila/24 bg-superficie p-2.5 opacity-0 shadow-[0_26px_60px_-18px_rgba(0,0,0,.85),0_0_0_1px_rgba(124,58,237,.12)] transition-[opacity,translate,visibility] duration-180 ease-[ease] group-hover/productos:visible group-hover/productos:translate-y-0 group-hover/productos:opacity-100 group-focus-within/productos:visible group-focus-within/productos:translate-y-0 group-focus-within/productos:opacity-100">
                {categorias.map((categoria) => (
                  <Link
                    key={categoria.slug}
                    href={`${base}/catalogo?categoria=${categoria.slug}`}
                    className="flex items-center gap-3 rounded-[10px] px-3 py-[11px] transition-colors hover:bg-violeta/14"
                  >
                    <IconoCategoria slug={categoria.slug} tamano={20} grosor={1.5} />
                    <span className="flex-1 text-sm text-texto">{categoria.nombre}</span>
                    <span className="text-xs text-texto-suave">{categoria.cantidadProductos}</span>
                  </Link>
                ))}
                <Link
                  href={`${base}/catalogo`}
                  className={cn(
                    "block px-3 py-[11px] text-xs text-lila",
                    categorias.length > 0 && "mt-1.5 border-t border-lila/14",
                  )}
                >
                  Ver todo el catálogo →
                </Link>
              </div>
            </div>

            <span data-pendiente="envios" aria-disabled="true" className="cursor-default transition-colors hover:text-texto">
              Envíos
            </span>
            <span data-pendiente="ayuda" aria-disabled="true" className="cursor-default transition-colors hover:text-texto">
              Ayuda
            </span>
          </nav>

          <div className="ml-auto flex items-center gap-4">
            {enFicha ? (
              <button type="button" aria-label="Buscar" aria-disabled="true" data-pendiente="busqueda" className="block cursor-pointer">
                <IconoLupa tamano={17} />
              </button>
            ) : (
              <div
                data-pendiente="busqueda"
                className="flex h-10 w-[230px] items-center gap-[9px] rounded-[20px] border border-lila/16 bg-texto/5 px-3.5"
              >
                <IconoLupa tamano={15} />
                <span className="text-[13px] text-texto-suave">{tienda.buscador.placeholder}</span>
              </div>
            )}

            <ContadorCarrito variante="escritorio" />

            <button
              type="button"
              aria-disabled="true"
              data-pendiente="iniciar-sesion"
              className="h-10 cursor-pointer rounded-[20px] border border-lila/40 bg-transparent px-[18px] text-[13px] font-medium text-texto transition-colors hover:bg-violeta/18"
            >
              Iniciar sesión
            </button>
          </div>
        </div>
      </header>

      <EncabezadoMovil tienda={tienda} categorias={categorias} />
    </>
  );
}
