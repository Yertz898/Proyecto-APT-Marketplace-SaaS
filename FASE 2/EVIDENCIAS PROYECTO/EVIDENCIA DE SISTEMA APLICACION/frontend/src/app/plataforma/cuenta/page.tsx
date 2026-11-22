import { PantallaCuenta } from "@/components/panel/pantalla-cuenta";

/*
 * La cuenta del administrador: su nombre, su contraseña, la verificación en
 * dos pasos y su sesión. Es la misma pantalla que usa el dueño de una tienda,
 * porque las tres cosas funcionan igual para cualquier cuenta de DealCommerce.
 */
export const metadata = { title: "Tu cuenta" };

export default function PaginaCuentaDePlataforma() {
  return <PantallaCuenta />;
}
