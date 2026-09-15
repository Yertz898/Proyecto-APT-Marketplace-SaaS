import type { ContenidoTienda } from "@/lib/tipos";

import { joyasYe } from "./joyas-ye";

// Registro local de tiendas mientras no exista la API. Una tienda que no esté
// acá responde 404, igual que responderá el backend.
const tiendas: Record<string, ContenidoTienda> = {
  [joyasYe.slug]: joyasYe,
};

export function contenidoLocalDeTienda(slug: string): ContenidoTienda | null {
  return tiendas[slug] ?? null;
}
