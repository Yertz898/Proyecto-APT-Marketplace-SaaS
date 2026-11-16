import { Clock, Mail, MapPin, Phone } from "lucide-react";
import Link from "next/link";

import { nombreDeRed, redDe } from "@/lib/redes";
import type { IdentidadTienda } from "@/lib/tipos";

import { EnlaceExterno } from "./enlace-externo";
import { IconoRed } from "./icono-red";
import { Marca } from "./marca";

/**
 * Pie de página de la tienda.
 *
 * Es el mismo para todas las tiendas y lo llena cada dueño desde «Tienda y
 * marca»: una frase sobre la tienda, cómo contactarla, sus redes y los enlaces
 * de siempre de un marketplace. Lo que la tienda no cargó no se dibuja, ni
 * siquiera su título: una columna «Contacto» vacía se ve como un error.
 *
 * Las redes se reconocen por el dominio del enlace, y cada una lleva su ícono.
 */
export function Pie({ tienda }: { tienda: IdentidadTienda }) {
  const pie = tienda.pie;
  const anio = new Date().getFullYear();
  const base = `/t/${tienda.slug}`;

  const contacto = pie && (pie.correo || pie.telefono || pie.direccion || pie.horario);
  // Las tiendas anteriores al pie editable solo tienen su Instagram suelto.
  const redes = pie?.redes.length ? pie.redes : [tienda.redes.instagram].filter((r): r is string => Boolean(r));

  return (
    <footer className="border-t border-violeta bg-tinta-honda">
      <div className="mx-auto grid max-w-[1280px] gap-10 px-5 py-12 sm:grid-cols-2 lg:grid-cols-[1.4fr_1fr_1fr] lg:px-6">
        <div>
          <Marca tienda={tienda} lugar="pie" />
          {pie?.descripcion && (
            <p className="mt-4 max-w-[360px] text-sm leading-[1.6] text-texto-suave">{pie.descripcion}</p>
          )}
          {redes.length > 0 && (
            <ul className="mt-5 flex list-none flex-wrap gap-2.5 p-0">
              {redes.map((enlace) => {
                const red = redDe(enlace);
                return (
                  <li key={enlace}>
                    <EnlaceExterno
                      enlace={enlace}
                      etiqueta={nombreDeRed(red)}
                      className="flex size-10 items-center justify-center rounded-full border border-lila/25 text-texto-suave transition-colors hover:border-lila hover:text-texto"
                    >
                      <IconoRed red={red} tamano={18} />
                    </EnlaceExterno>
                  </li>
                );
              })}
            </ul>
          )}
        </div>

        <nav aria-label="Enlaces de la tienda">
          <p className="text-[13px] font-semibold tracking-[0.08em] text-texto uppercase">Tienda</p>
          <ul className="mt-4 flex list-none flex-col gap-2.5 p-0 text-sm">
            <li>
              <Link href={base} className="text-texto-suave hover:text-texto">
                Inicio
              </Link>
            </li>
            <li>
              <Link href={`${base}/productos`} className="text-texto-suave hover:text-texto">
                Catálogo
              </Link>
            </li>
            <li>
              <Link href={`${base}/carrito`} className="text-texto-suave hover:text-texto">
                Mi carrito
              </Link>
            </li>
            <li>
              <Link href={`${base}/agenda`} className="text-texto-suave hover:text-texto">
                Agendar una visita
              </Link>
            </li>
            <li>
              <Link href={`${base}/entrar`} className="text-texto-suave hover:text-texto">
                Mi cuenta
              </Link>
            </li>
          </ul>
        </nav>

        {contacto && (
          <div>
            <p className="text-[13px] font-semibold tracking-[0.08em] text-texto uppercase">Contacto</p>
            <ul className="mt-4 flex list-none flex-col gap-3 p-0 text-sm text-texto-suave">
              {pie.correo && (
                <li className="flex items-start gap-2.5">
                  <Mail size={16} className="mt-0.5 shrink-0" aria-hidden="true" />
                  <a href={`mailto:${pie.correo}`} className="break-all text-texto-suave hover:text-texto">
                    {pie.correo}
                  </a>
                </li>
              )}
              {pie.telefono && (
                <li className="flex items-start gap-2.5">
                  <Phone size={16} className="mt-0.5 shrink-0" aria-hidden="true" />
                  <a href={`tel:${pie.telefono.replace(/[^\d+]/g, "")}`} className="text-texto-suave hover:text-texto">
                    {pie.telefono}
                  </a>
                </li>
              )}
              {pie.direccion && (
                <li className="flex items-start gap-2.5">
                  <MapPin size={16} className="mt-0.5 shrink-0" aria-hidden="true" />
                  <span>{pie.direccion}</span>
                </li>
              )}
              {pie.horario && (
                <li className="flex items-start gap-2.5">
                  <Clock size={16} className="mt-0.5 shrink-0" aria-hidden="true" />
                  <span>{pie.horario}</span>
                </li>
              )}
            </ul>
          </div>
        )}
      </div>

      <div className="mx-auto flex max-w-[1280px] flex-col gap-2 border-t border-texto/8 px-5 py-6 text-xs text-texto-suave lg:flex-row lg:justify-between lg:px-6">
        <span>
          © {anio} {tienda.nombre}
        </span>
        <span>Tienda operada sobre DealCommerce</span>
      </div>
    </footer>
  );
}
