import { redirect } from "next/navigation";

// Mientras Joyas Ye sea la única tienda, la raíz lleva directo a su tienda
// pública. Se reemplaza cuando exista una portada de DealCommerce.
export default function Raiz() {
  redirect("/t/joyas-ye");
}
