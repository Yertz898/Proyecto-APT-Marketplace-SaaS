/*
 * El tema de la vitrina: claro u oscuro.
 *
 * Lo elige el comprador y vive en su navegador. Está acá, fuera del componente,
 * porque el layout de la tienda —que corre en el servidor— necesita el guion
 * para dejarlo puesto antes de pintar.
 */

export type Tema = "claro" | "oscuro";

export const CLAVE_DEL_TEMA = "dealcommerce:tema-vitrina";

/*
 * Corre antes que nada, desde el layout de la tienda.
 *
 * Tiene que ser suelto y síncrono: si esperara a que React hidrate, el
 * comprador que eligió claro vería un golpe de negro en cada carga. El texto es
 * una constante de este archivo, nunca algo que venga del vendedor ni de la
 * URL; el `JSON.stringify` es para que la clave quede escapada aunque mañana
 * alguien la cambie.
 */
export const GUION_DEL_TEMA = `(function(){try{var t=localStorage.getItem(${JSON.stringify(
  CLAVE_DEL_TEMA,
)});if(t==="claro"||t==="oscuro"){document.documentElement.dataset.vitrina=t}}catch(e){}})()`;
