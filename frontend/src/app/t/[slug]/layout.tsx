import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { ProveedorCarrito } from "@/components/tienda/carrito";
import { Encabezado } from "@/components/tienda/encabezado";
import { Pie } from "@/components/tienda/pie";
import { obtenerCategorias } from "@/lib/api/catalogo";
import { obtenerTienda } from "@/lib/api/tienda";

export async function generateMetadata({ params }: LayoutProps<"/t/[slug]">): Promise<Metadata> {
  const { slug } = await params;
  const tienda = await obtenerTienda(slug);

  if (!tienda) {
    return {};
  }

  return { title: { default: tienda.nombre, template: `%s · ${tienda.nombre}` } };
}

/** Marco de la tienda pública: encabezado y pie, comunes a las tres pantallas. */
export default async function LayoutTienda({ children, params }: LayoutProps<"/t/[slug]">) {
  const { slug } = await params;
  const [tienda, categorias] = await Promise.all([obtenerTienda(slug), obtenerCategorias(slug)]);

  if (!tienda) {
    notFound();
  }

  return (
    <ProveedorCarrito>
      <Encabezado tienda={tienda} categorias={categorias} />
      {children}
      <Pie tienda={tienda} />
    </ProveedorCarrito>
  );
}
