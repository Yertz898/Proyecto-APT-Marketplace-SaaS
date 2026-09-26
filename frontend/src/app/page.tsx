import { notFound, redirect } from "next/navigation";

/*
 * Raíz del sitio.
 *
 * La plataforma todavía no tiene portada propia. Para trabajar cómodo se puede
 * definir NEXT_PUBLIC_TIENDA_POR_DEFECTO en el .env local y la raíz redirige a
 * esa tienda. Sin esa variable no hay nada que mostrar: ninguna tienda está
 * escrita en el código.
 */
export default function Raiz() {
  const porDefecto = process.env.NEXT_PUBLIC_TIENDA_POR_DEFECTO;

  if (!porDefecto) {
    notFound();
  }

  redirect(`/t/${porDefecto}`);
}
