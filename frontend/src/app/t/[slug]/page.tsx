import { notFound } from "next/navigation";

import { Portada } from "@/components/tienda/portada";
import { CategoriasDestacadas, LlamadoMayorista, MasPedidos } from "@/components/tienda/secciones-inicio";
import { obtenerCategorias, obtenerMasPedidos } from "@/lib/api/catalogo";
import { obtenerTienda } from "@/lib/api/tienda";

/** Inicio de la tienda pública (mockup 1A en escritorio, 1D en móvil). */
export default async function InicioTienda({ params }: PageProps<"/t/[slug]">) {
  const { slug } = await params;
  const [tienda, categorias, masPedidos] = await Promise.all([
    obtenerTienda(slug),
    obtenerCategorias(slug),
    obtenerMasPedidos(slug),
  ]);

  if (!tienda) {
    notFound();
  }

  return (
    <main className="flex-1">
      <Portada tienda={tienda} />
      <CategoriasDestacadas slugTienda={slug} categorias={categorias} />
      <MasPedidos slugTienda={slug} productos={masPedidos} />
      <LlamadoMayorista tienda={tienda} />
    </main>
  );
}
