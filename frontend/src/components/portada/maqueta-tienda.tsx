/*
 * Maqueta que acompaña al titular: una tienda abierta en el navegador y, encima,
 * la esquina del panel del vendedor.
 *
 * Es decoración, no un ejemplo de datos reales: va con aria-hidden y ningún
 * lector de pantalla la anuncia. Los productos y los montos son inventados y
 * cumplen el mismo papel que un texto de relleno en una maqueta.
 */

type Producto = {
  nombre: string;
  precio: string;
  tramo: string;
  fondo: string;
  figura: React.ReactNode;
};

const PRODUCTOS: Producto[] = [
  {
    nombre: "Café en grano 1 kg",
    precio: "$12.990",
    tramo: "10+ u. $10.990",
    fondo: "bg-cielo",
    figura: <span className="h-[58%] w-[38%] rounded-t-[6px] rounded-b-[4px] bg-acero" />,
  },
  {
    nombre: "Aceite maravilla 1 L",
    precio: "$3.490",
    tramo: "24+ u. $2.890",
    fondo: "bg-trigo",
    figura: (
      <>
        <span className="h-[50%] w-[22%] rounded-[4px] bg-ambar" />
        <span className="h-[62%] w-[22%] rounded-[4px] bg-ambar-hondo" />
      </>
    ),
  },
  {
    nombre: "Arroz grado 1, saco 25 kg",
    precio: "$45.990",
    tramo: "5+ u. $41.990",
    fondo: "bg-jade-claro",
    figura: <span className="h-[44%] w-[56%] rounded-[6px] bg-jade" />,
  },
];

export function MaquetaTienda() {
  return (
    <div aria-hidden="true" className="relative pb-[clamp(120px,11cqi,150px)]">
      <div className="w-[88%] overflow-hidden rounded-[16px] border border-arena bg-white shadow-[0_20px_50px_rgba(20,33,61,.10)]">
        <BarraDelNavegador />

        <div className="flex flex-col gap-3.5 p-4">
          <div className="flex items-center justify-between gap-2">
            <div className="flex min-w-0 items-center gap-2">
              <span className="flex size-[26px] flex-none items-center justify-center rounded-[7px] bg-marino font-jakarta text-xs font-bold text-white">
                LA
              </span>
              <span className="truncate font-jakarta text-sm font-bold">Distribuidora Los Andes</span>
            </div>
            <span className="flex-none rounded-full bg-acero px-2.5 py-[5px] text-[11px] font-semibold text-white">
              Pedido · 24
            </span>
          </div>

          <div className="flex flex-wrap gap-1.5">
            <span className="rounded-full bg-marino px-2.5 py-1 text-[11px] font-semibold text-white">Abarrotes</span>
            <span className="rounded-full bg-lino px-2.5 py-1 text-[11px] text-marino">Bebidas</span>
            <span className="rounded-full bg-lino px-2.5 py-1 text-[11px] text-marino">Limpieza</span>
          </div>

          <div className="flex items-center justify-between gap-2 rounded-[10px] bg-jade-claro px-3 py-2.5">
            <span className="min-w-0 text-[11px] text-marino">24 u. · precio por volumen aplicado</span>
            <span className="flex-none text-[13px] font-bold text-jade">$263.760</span>
          </div>

          <div className="grid grid-cols-3 gap-2.5">
            {PRODUCTOS.map((producto) => (
              <div key={producto.nombre} className="flex flex-col gap-1.5">
                <div
                  className={`flex aspect-square items-end justify-center gap-[6%] rounded-[10px] pb-[14%] ${producto.fondo}`}
                >
                  {producto.figura}
                </div>
                <span className="text-[11px] leading-[1.25] font-semibold">{producto.nombre}</span>
                <span className="text-xs font-bold">{producto.precio}</span>
                <span className="text-[10px] font-semibold text-jade">{producto.tramo}</span>
              </div>
            ))}
          </div>

          {/* La fila cortada insinúa que el catálogo sigue más abajo. */}
          <div className="grid grid-cols-3 gap-2.5 opacity-90">
            <div className="aspect-[2/1] rounded-[10px] bg-lino" />
            <div className="aspect-[2/1] rounded-[10px] bg-lino" />
            <div className="aspect-[2/1] rounded-[10px] bg-lino" />
          </div>
        </div>
      </div>

      <PanelDelVendedor />
    </div>
  );
}

function BarraDelNavegador() {
  return (
    <div className="flex items-center gap-1.5 border-b border-lino-claro bg-crema px-3.5 py-2.5">
      <span className="size-[9px] rounded-full bg-arena-honda" />
      <span className="size-[9px] rounded-full bg-arena-honda" />
      <span className="size-[9px] rounded-full bg-arena-honda" />
      <span className="ml-2.5 min-w-0 flex-1 truncate rounded-[6px] bg-lino px-2.5 py-1 text-[11px] text-pizarra">
        losandes.dealcommerce.cl
      </span>
    </div>
  );
}

/** La tarjeta que se monta sobre la esquina del navegador. */
function PanelDelVendedor() {
  return (
    <div className="absolute right-0 bottom-0 flex w-[58%] flex-col gap-3 rounded-[14px] border border-arena bg-white p-3.5 shadow-[0_24px_60px_rgba(20,33,61,.16)]">
      <div className="flex items-center justify-between">
        <span className="font-jakarta text-xs font-bold">Tu panel · Hoy</span>
        <span className="size-[22px] rounded-[6px] bg-cielo" />
      </div>

      <div className="flex items-end justify-between gap-2">
        <div className="flex flex-col gap-0.5">
          <span className="text-[10px] text-pizarra">Ventas de hoy</span>
          <span className="font-jakarta text-lg font-extrabold tracking-[-0.02em] text-jade">$1.284.500</span>
        </div>
        <div className="flex h-8 items-end gap-[3px]">
          <span className="h-[40%] w-1.5 rounded-[2px] bg-niebla" />
          <span className="h-[55%] w-1.5 rounded-[2px] bg-niebla" />
          <span className="h-[45%] w-1.5 rounded-[2px] bg-niebla" />
          <span className="h-[70%] w-1.5 rounded-[2px] bg-niebla" />
          <span className="h-full w-1.5 rounded-[2px] bg-acero" />
        </div>
      </div>

      <div className="flex flex-col gap-1.5">
        <PedidoDeEjemplo numero="#1042" cliente="Minimarket Doña Rosa" etiqueta="Confirmado" confirmado />
        <PedidoDeEjemplo numero="#1041" cliente="Almacén El Roble" etiqueta="Nuevo" />
      </div>
    </div>
  );
}

function PedidoDeEjemplo({
  numero,
  cliente,
  etiqueta,
  confirmado = false,
}: {
  numero: string;
  cliente: string;
  etiqueta: string;
  confirmado?: boolean;
}) {
  return (
    <div className="flex items-center justify-between gap-1.5 rounded-[8px] bg-hueso px-2.5 py-2">
      <div className="flex min-w-0 flex-col">
        <span className="text-[10px] font-semibold">Pedido {numero}</span>
        <span className="truncate text-[9.5px] text-pizarra">{cliente}</span>
      </div>
      <span
        className={`flex-none rounded-full px-2 py-[3px] text-[9.5px] font-semibold ${
          confirmado ? "bg-jade-claro text-jade" : "bg-trigo text-marino"
        }`}
      >
        {etiqueta}
      </span>
    </div>
  );
}
