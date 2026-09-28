import { FranjaClara, TituloDeSeccion } from "./secciones";

/*
 * El problema, contado con las palabras del vendedor.
 *
 * Las tres tarjetas son citas y por eso van entre comillas: describen el día a
 * día de quien hoy cotiza a mano por WhatsApp.
 */

const QUEJAS = [
  {
    cita: "“Cotizo a mano cada mensaje”",
    detalle: "Me escriben “¿precio por 20?” y tengo que sacar la cuenta, responder y esperar. Todo el día.",
    icono: (
      <>
        <path d="M4 18.5V6a2 2 0 012-2h12a2 2 0 012 2v8a2 2 0 01-2 2H8l-4 2.5z" />
        <path d="M9 9h6M9 12h3" />
      </>
    ),
  },
  {
    cita: "“Mis precios mayoristas están en mi cabeza”",
    detalle: "Cada cliente tiene su tramo y nadie más lo sabe. Si no estoy yo, no se vende.",
    icono: (
      <>
        <circle cx="12" cy="10" r="6.5" />
        <path d="M9.5 20h5M10.5 16.5v3.5M13.5 16.5v3.5" />
        <path d="M12 7v3l2 1.5" />
      </>
    ),
  },
  {
    cita: "“No sé qué se vende y qué no”",
    detalle: "Los pedidos quedan perdidos entre chats y capturas de pantalla. Compro stock a ojo.",
    icono: (
      <>
        <path d="M4 20V10M10 20V4M16 20v-7M22 20H2" />
        <path d="M18.5 4.5l3 3M21.5 4.5l-3 3" />
      </>
    ),
  },
];

export function Problema() {
  return (
    <FranjaClara>
      <TituloDeSeccion antetitulo="El problema">¿Te suena conocido?</TituloDeSeccion>

      <div className="grid grid-cols-[repeat(auto-fit,minmax(min(100%,300px),1fr))] gap-5">
        {QUEJAS.map((queja) => (
          <div
            key={queja.cita}
            className="flex flex-col gap-3.5 rounded-[16px] border border-arena bg-hueso p-7"
          >
            <svg
              width="28"
              height="28"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#1F4E79"
              strokeWidth="1.7"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              {queja.icono}
            </svg>
            <h3 className="font-jakarta text-[21px] leading-[1.25] font-bold tracking-[-0.01em]">{queja.cita}</h3>
            <p className="text-base leading-[1.55] text-pizarra text-pretty">{queja.detalle}</p>
          </div>
        ))}
      </div>
    </FranjaClara>
  );
}
