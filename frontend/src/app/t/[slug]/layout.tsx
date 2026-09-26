import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { ProveedorCarrito } from "@/components/tienda/carrito";
import { Encabezado } from "@/components/tienda/encabezado";
import { Pie } from "@/components/tienda/pie";
import { obtenerIdentidadTienda } from "@/lib/api/tienda";
import { variablesDeIdentidad } from "@/lib/identidad";

export async function generateMetadata({ params }: LayoutProps<"/t/[slug]">): Promise<Metadata> {
  const { slug } = await params;
  const tienda = await obtenerIdentidadTienda(slug);

  return tienda ? { title: { default: tienda.nombre, template: `%s · ${tienda.nombre}` } } : {};
}

/**
 * Marco de la tienda pública.
 *
 * Los colores de la tienda entran como variables CSS validadas. Nunca se
 * inserta CSS ni HTML escrito por el vendedor.
 */
export default async function LayoutTienda({ children, params }: LayoutProps<"/t/[slug]">) {
  const { slug } = await params;
  const tienda = await obtenerIdentidadTienda(slug);

  if (!tienda) {
    notFound();
  }

  return (
    <ProveedorCarrito slugTienda={slug}>
      <div style={variablesDeIdentidad(tienda.colores)} className="flex min-h-full flex-1 flex-col">
        <Encabezado tienda={tienda} />
        {children}
        <Pie tienda={tienda} />
      </div>
    </ProveedorCarrito>
  );
}
