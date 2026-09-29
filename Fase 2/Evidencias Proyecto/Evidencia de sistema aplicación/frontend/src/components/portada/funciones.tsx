import { FranjaClara, TituloDeSeccion } from "./secciones";

/*
 * Las ocho funciones del producto.
 *
 * Las tarjetas se levantan al pasar el mouse. El movimiento se apaga solo
 * cuando el sistema pide menos animación.
 */

const FUNCIONES = [
  {
    titulo: "Precios por volumen automáticos",
    detalle: "Defines los tramos una vez y el total se calcula solo.",
    icono: <path d="M3 20h4v-5h5v-5h5V5h4" />,
  },
  {
    titulo: "Lotes con cupos",
    detalle: "Abre una compra conjunta y ciérrala cuando se llenen los cupos.",
    icono: (
      <>
        <path d="M3 7.5L12 3l9 4.5-9 4.5-9-4.5z" />
        <path d="M3 7.5v9L12 21l9-4.5v-9M12 12v9" />
      </>
    ),
  },
  {
    titulo: "Venta por gramo",
    detalle: "Tu cliente pide 250 g o 3 kg y el precio se ajusta.",
    icono: (
      <>
        <path d="M12 4v16M7 20h10M5 7h14" />
        <path d="M5 7l-3 6h6l-3-6zM19 7l-3 6h6l-3-6z" />
      </>
    ),
  },
  {
    titulo: "Carga desde Excel",
    detalle: "Sube tu planilla de siempre y tu catálogo queda listo.",
    icono: (
      <>
        <rect x="3" y="3" width="18" height="18" rx="2" />
        <path d="M3 9h18M3 15h18M9 3v18" />
      </>
    ),
  },
  {
    titulo: "Panel de ventas",
    detalle: "Qué se vende, a quién y cuándo, en una sola pantalla.",
    icono: (
      <>
        <path d="M3 21h18" />
        <rect x="5" y="11" width="3" height="7" />
        <rect x="10.5" y="6" width="3" height="12" />
        <rect x="16" y="9" width="3" height="9" />
      </>
    ),
  },
  {
    titulo: "Pronóstico de demanda",
    detalle: "Anticipa cuánto vas a vender para comprar mejor.",
    icono: (
      <>
        <path d="M3 18l5-5 4 3 3-4" />
        <path d="M15 12l6-7" strokeDasharray="2 2.5" />
      </>
    ),
  },
  {
    titulo: "Sugerencias de descuento",
    detalle: "Te avisa qué productos conviene rebajar para que roten.",
    icono: (
      <>
        <path d="M18 6L6 18" />
        <circle cx="7.5" cy="7.5" r="2.5" />
        <circle cx="16.5" cy="16.5" r="2.5" />
      </>
    ),
  },
  {
    titulo: "Asistente de ventas",
    detalle: "Pregúntale “¿qué vendí más en agosto?” y te responde al tiro.",
    icono: (
      <>
        <path d="M4 19V6a2 2 0 012-2h12a2 2 0 012 2v8a2 2 0 01-2 2H8l-4 3z" />
        <path d="M9 10h.01M12 10h.01M15 10h.01" />
      </>
    ),
  },
];

export function Funciones() {
  return (
    <FranjaClara id="funciones">
      <TituloDeSeccion antetitulo="Funciones">Todo lo que hoy haces a mano, resuelto</TituloDeSeccion>

      <div className="grid grid-cols-[repeat(auto-fit,minmax(min(100%,260px),1fr))] gap-4">
        {FUNCIONES.map((funcion) => (
          <div
            key={funcion.titulo}
            className="flex flex-col gap-3 rounded-[14px] border border-arena bg-hueso p-6 transition-[transform,box-shadow,border-color] duration-200 ease-out hover:-translate-y-1 hover:border-niebla hover:shadow-[0_10px_24px_rgba(20,33,61,.10)] motion-reduce:transition-none motion-reduce:hover:translate-y-0"
          >
            <span className="flex size-11 items-center justify-center rounded-[10px] bg-cielo">
              <svg
                width="22"
                height="22"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#1F4E79"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                {funcion.icono}
              </svg>
            </span>
            <h3 className="font-jakarta text-[17px] font-bold">{funcion.titulo}</h3>
            <p className="text-[15px] leading-[1.5] text-pizarra">{funcion.detalle}</p>
          </div>
        ))}
      </div>
    </FranjaClara>
  );
}
