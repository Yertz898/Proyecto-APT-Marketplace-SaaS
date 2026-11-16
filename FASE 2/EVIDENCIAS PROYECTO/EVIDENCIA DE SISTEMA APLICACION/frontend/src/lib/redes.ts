/**
 * De qué red social es un enlace, por su dominio.
 *
 * El dueño pega el enlace a su perfil y la vitrina dibuja el ícono que
 * corresponde. Lo que no se reconoce se muestra como un sitio web, con un
 * globo: nunca se esconde un enlace que la tienda decidió publicar.
 */

export type RedSocial =
  | "instagram"
  | "facebook"
  | "tiktok"
  | "x"
  | "youtube"
  | "whatsapp"
  | "linkedin"
  | "pinterest"
  | "telegram"
  | "sitio";

const NOMBRES: Record<RedSocial, string> = {
  instagram: "Instagram",
  facebook: "Facebook",
  tiktok: "TikTok",
  x: "X",
  youtube: "YouTube",
  whatsapp: "WhatsApp",
  linkedin: "LinkedIn",
  pinterest: "Pinterest",
  telegram: "Telegram",
  sitio: "Sitio web",
};

/** Dominio → red. Se compara el final del nombre, así `m.facebook.com` también vale. */
const DOMINIOS: [string, RedSocial][] = [
  ["instagram.com", "instagram"],
  ["instagr.am", "instagram"],
  ["facebook.com", "facebook"],
  ["fb.com", "facebook"],
  ["fb.me", "facebook"],
  ["tiktok.com", "tiktok"],
  ["x.com", "x"],
  ["twitter.com", "x"],
  ["youtube.com", "youtube"],
  ["youtu.be", "youtube"],
  ["wa.me", "whatsapp"],
  ["whatsapp.com", "whatsapp"],
  ["linkedin.com", "linkedin"],
  ["pinterest.com", "pinterest"],
  ["pinterest.cl", "pinterest"],
  ["pin.it", "pinterest"],
  ["t.me", "telegram"],
  ["telegram.me", "telegram"],
];

export function redDe(enlace: string): RedSocial {
  let dominio: string;
  try {
    dominio = new URL(enlace).hostname.toLowerCase();
  } catch {
    return "sitio";
  }
  const encontrada = DOMINIOS.find(([d]) => dominio === d || dominio.endsWith(`.${d}`));
  return encontrada ? encontrada[1] : "sitio";
}

export function nombreDeRed(red: RedSocial): string {
  return NOMBRES[red];
}

/** Lo que se muestra del enlace: el usuario o la ruta, sin el https://. */
export function perfilDe(enlace: string): string {
  try {
    const url = new URL(enlace);
    const ruta = url.pathname.replace(/\/+$/, "");
    return ruta && ruta !== "/" ? ruta.replace(/^\//, "") : url.hostname.replace(/^www\./, "");
  } catch {
    return enlace;
  }
}

/** Solo se publica lo que es https: el enlace termina en un href de la vitrina. */
export function esEnlaceValido(enlace: string): boolean {
  try {
    return new URL(enlace).protocol === "https:";
  } catch {
    return false;
  }
}
