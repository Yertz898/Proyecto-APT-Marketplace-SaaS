import { Isotipo } from "./marca";

/*
 * Las tres piezas finales: la promesa sobre los datos, las preguntas y el pie.
 *
 * Están en un archivo porque son cortas y se leen mejor juntas que repartidas
 * en tres.
 */

export function Privacidad() {
  return (
    <section className="px-[clamp(20px,5.5cqi,80px)] py-[clamp(64px,7cqi,112px)]">
      <div className="mx-auto grid max-w-[1280px] grid-cols-[repeat(auto-fit,minmax(min(100%,420px),1fr))] items-start gap-[clamp(24px,4cqi,64px)]">
        <div className="flex items-start gap-[18px]">
          <span className="flex size-[52px] flex-none items-center justify-center rounded-[14px] bg-cielo">
            <svg
              width="26"
              height="26"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#1F4E79"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <rect x="4.5" y="10.5" width="15" height="10" rx="2" />
              <path d="M8 10.5V7.5a4 4 0 018 0v3" />
              <path d="M12 14.5v2" />
            </svg>
          </span>
          <h2 className="font-jakarta text-[clamp(30px,3.3cqi,46px)] leading-[1.08] font-extrabold tracking-[-0.03em]">
            Tus datos son tuyos
          </h2>
        </div>

        <div className="flex flex-col gap-3.5">
          <p className="text-lg leading-[1.55] text-marino text-pretty">
            Cada tienda ve solo su información. Tus clientes, tus precios y tus ventas no se mezclan con los de
            nadie más.
          </p>
          <p className="text-base leading-[1.55] text-pizarra text-pretty">
            No vendemos ni compartimos tus datos, y puedes descargarlos cuando quieras.
          </p>
        </div>
      </div>
    </section>
  );
}

const PREGUNTAS = [
  {
    pregunta: "¿Necesito saber de computación?",
    respuesta:
      "No. Si sabes usar WhatsApp e Instagram, puedes usar DealCommerce. Te acompañamos en la primera carga de tu catálogo.",
  },
  {
    pregunta: "¿Puedo cargar mi catálogo desde Excel?",
    respuesta:
      "Sí. Subes tu planilla con productos, precios y tramos por volumen, y tu catálogo queda armado. Después puedes editar lo que quieras a mano.",
  },
  {
    pregunta: "¿Cobran comisión por venta?",
    respuesta:
      "Los precios de los planes aún están por definir. Te los vamos a contar con claridad antes de que actives tu tienda, sin letra chica.",
  },
  {
    pregunta: "¿Cómo me pagan mis clientes?",
    respuesta:
      "Tú eliges: transferencia bancaria, pago al retirar o el medio que ya usas hoy. El pedido llega a tu panel con el detalle y el total calculado.",
  },
];

/*
 * Las preguntas usan <details> del navegador: abren y cierran sin JavaScript, y
 * el buscador las lee. La primera viene abierta.
 */
export function Preguntas() {
  return (
    <section className="px-[clamp(20px,5.5cqi,80px)] pb-[clamp(64px,7cqi,112px)]">
      <div className="mx-auto flex max-w-[880px] flex-col gap-7">
        <h2 className="font-jakarta text-[clamp(30px,3.3cqi,46px)] leading-[1.08] font-extrabold tracking-[-0.03em]">
          Preguntas frecuentes
        </h2>

        <div className="flex flex-col border-t border-arena-honda">
          {PREGUNTAS.map((item, posicion) => (
            <details key={item.pregunta} open={posicion === 0} className="group border-b border-arena-honda">
              <summary className="flex min-h-11 cursor-pointer list-none items-center justify-between gap-4 py-[22px] font-jakarta text-[clamp(17px,1.4cqi,20px)] font-bold [&::-webkit-details-marker]:hidden">
                {item.pregunta}
                <span
                  aria-hidden="true"
                  className="flex size-8 flex-none items-center justify-center rounded-full bg-cielo font-inter text-[22px] leading-none font-medium text-acero transition-transform duration-200 group-open:rotate-45 motion-reduce:transition-none"
                >
                  +
                </span>
              </summary>
              <p className="pr-12 pb-6 text-base leading-[1.6] text-pizarra text-pretty">{item.respuesta}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}

export function Pie() {
  return (
    <footer className="border-t border-arena px-[clamp(20px,5.5cqi,80px)] py-8">
      <div className="mx-auto flex max-w-[1280px] flex-wrap items-center justify-between gap-4 text-sm text-pizarra">
        <span className="flex items-center gap-2 text-marino">
          <Isotipo tamano={22} />
          <span className="font-jakarta text-base font-extrabold">DealCommerce</span>
        </span>

        <span>© 2026 DealCommerce · Hecho en Chile</span>
      </div>
    </footer>
  );
}
