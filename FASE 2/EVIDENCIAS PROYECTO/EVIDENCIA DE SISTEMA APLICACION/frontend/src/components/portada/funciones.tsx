import { FranjaClara, TituloDeSeccion } from "./secciones";

/*
 * Las ocho funciones del producto.
 *
 * Todas sirven a cualquier tienda de la plataforma. Las formas de vender
 * propias de un rubro —los lotes cerrados o la venta por gramo de una
 * joyería— son del catálogo de esa tienda, no una función de DealCommerce, y
 * por eso no se nombran acá.
 *
 * Las tarjetas se levantan al pasar el mouse. El movimiento se apaga solo
 * cuando el sistema pide menos animación.
 */

const FUNCIONES = [
  {
    titulo: "Precios por cantidad automáticos",
    detalle: "Defines los tramos una vez y el total se calcula solo.",
    icono: <path d="M3 20h4v-5h5v-5h5V5h4" />,
  },
  {
    titulo: "Tu tienda con tu marca",
    detalle: "Tu logo, tus colores y tu tipografía. Se ve tuya, no nuestra.",
    icono: (
      <>
        <path d="M12 3a9 9 0 000 18c1.1 0 2-.9 2-2 0-.52-.2-.99-.53-1.34A1.98 1.98 0 0113 16.2c0-1.1.9-2 2-2h2.2A3.8 3.8 0 0021 10.4C21 6.3 16.97 3 12 3z" />
        <circle cx="7.5" cy="11.5" r="1" />
        <circle cx="12" cy="7.5" r="1" />
        <circle cx="16.5" cy="11.5" r="1" />
      </>
    ),
  },
  {
    titulo: "Agenda de visitas",
    detalle: "Tus clientes reservan hora para ir a verte, sin cruces.",
    icono: (
      <>
        <rect x="3" y="5" width="18" height="16" rx="2" />
        <path d="M3 10h18M8 3v4M16 3v4" />
        <path d="M8.5 14.5l2 2 4-4" />
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
    titulo: "Alerta de quiebre",
    detalle: "Te avisa qué se te va a acabar antes de que pase.",
    icono: (
      <>
        <path d="M12 4l9 16H3l9-16z" />
        <path d="M12 10v4M12 17h.01" />
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
