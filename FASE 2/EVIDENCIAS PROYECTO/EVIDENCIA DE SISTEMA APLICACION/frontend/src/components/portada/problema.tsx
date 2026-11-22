import { FranjaClara, TituloDeSeccion } from "./secciones";

/*
 * El problema, contado con las palabras del vendedor.
 *
 * A la izquierda, las tres quejas: son citas y por eso van entre comillas. A la
 * derecha, cómo se ve eso en el teléfono: una cotización por WhatsApp que se
 * demora, contra el mismo pedido resuelto en DealCommerce. El chat es de
 * ejemplo y decorativo (aria-hidden): lo que dice ya está en el texto de la
 * izquierda.
 */

const QUEJAS = [
  {
    cita: "“Cotizo a mano cada mensaje”",
    detalle: "Me escriben “¿precio por 20?” y tengo que sacar la cuenta, responder y esperar. Todo el día.",
  },
  {
    cita: "“Mis precios mayoristas están en mi cabeza”",
    detalle: "Cada cliente tiene su tramo y nadie más lo sabe. Si no estoy yo, no se vende.",
  },
  {
    cita: "“No sé qué se vende y qué no”",
    detalle: "Los pedidos quedan perdidos entre chats y capturas de pantalla. Compro stock a ojo.",
  },
];

export function Problema() {
  return (
    <FranjaClara>
      <TituloDeSeccion antetitulo="El problema">¿Te suena conocido?</TituloDeSeccion>

      <div className="grid grid-cols-[repeat(auto-fit,minmax(min(100%,420px),1fr))] items-center gap-[clamp(32px,5cqi,72px)]">
        <ol className="flex list-none flex-col p-0">
          {QUEJAS.map((queja, posicion) => (
            <li key={queja.cita} className="grid grid-cols-[auto_1fr] gap-x-5 border-t border-arena py-6 last:border-b">
              <span aria-hidden="true" className="pt-1 font-jakarta text-sm font-extrabold text-ambar-hondo tabular-nums">
                {String(posicion + 1).padStart(2, "0")}
              </span>
              <div className="flex flex-col gap-1.5">
                <h3 className="font-jakarta text-[clamp(19px,1.6cqi,22px)] leading-[1.25] font-bold tracking-[-0.01em]">
                  {queja.cita}
                </h3>
                <p className="text-base leading-[1.55] text-pizarra text-pretty">{queja.detalle}</p>
              </div>
            </li>
          ))}
        </ol>

        <ChatDeEjemplo />
      </div>
    </FranjaClara>
  );
}

function Burbuja({
  lado,
  hora,
  children,
  visto = false,
}: {
  lado: "cliente" | "tienda";
  hora: string;
  children: string;
  visto?: boolean;
}) {
  const cliente = lado === "cliente";
  return (
    <div className={`flex ${cliente ? "justify-start" : "justify-end"}`}>
      <div
        className={`max-w-[82%] rounded-xl px-3 py-2 text-[13.5px] leading-[1.4] text-marino shadow-[0_1px_0_rgba(20,33,61,.08)] ${
          cliente ? "rounded-tl-sm bg-white" : "rounded-tr-sm bg-[#DCF3D9]"
        }`}
      >
        {children}
        <span className="ml-2 inline-block translate-y-0.5 text-[10.5px] text-pizarra tabular-nums">
          {hora}
          {visto && <span className="ml-1 text-[#3B82C4]">✓✓</span>}
        </span>
      </div>
    </div>
  );
}

function ChatDeEjemplo() {
  return (
    <div aria-hidden="true" className="flex flex-col gap-4">
      <div className="overflow-hidden rounded-xl border border-arena bg-[#EFEAE2]">
        <div className="flex items-center gap-3 bg-marino px-4 py-3 text-white">
          <span className="flex size-8 items-center justify-center rounded-full bg-white/15 text-sm font-bold">C</span>
          <div className="leading-tight">
            <p className="text-sm font-semibold">Clienta mayorista</p>
            <p className="text-[11px] text-white/70">WhatsApp</p>
          </div>
        </div>

        <div className="flex flex-col gap-2 px-3.5 py-4">
          <Burbuja lado="cliente" hora="10:02">
            Hola! ¿A cuánto me dejas 20 cadenas y 3 lotes de pulseras?
          </Burbuja>
          <Burbuja lado="cliente" hora="10:03">
            ¿Y si llevo 30 cadenas?
          </Burbuja>
          <Burbuja lado="tienda" hora="10:41" visto>
            Hola! Déjame calcular y te digo
          </Burbuja>
          <Burbuja lado="cliente" hora="12:15">
            ¿Pudiste ver? Necesito cerrar hoy
          </Burbuja>
          <p className="mt-1 self-center rounded-md bg-white/70 px-2.5 py-1 text-[11px] text-pizarra">
            2 horas sin respuesta
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3 rounded-xl border border-jade/30 bg-jade-claro px-4 py-3.5">
        <span className="flex size-9 flex-none items-center justify-center rounded-full bg-jade text-white">
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.4"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M5 12.5l4.5 4.5L19 7.5" />
          </svg>
        </span>
        <p className="text-sm leading-[1.45] text-marino">
          <span className="font-bold">En DealCommerce, el mismo pedido sale en 10 segundos:</span> la clienta elige
          las cantidades, ve su tramo y el total, y te llega listo.
        </p>
      </div>
    </div>
  );
}
