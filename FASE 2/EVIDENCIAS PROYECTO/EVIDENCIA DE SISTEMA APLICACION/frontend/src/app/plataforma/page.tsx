/**
 * Portada de la administración de la plataforma.
 *
 * Por ahora solo confirma que la sesión de administrador funciona y entra
 * donde corresponde. El panel con las tiendas suscritas es lo siguiente.
 */
export default function PaginaDePlataforma() {
  return (
    <div className="max-w-[560px]">
      <h1 className="font-jakarta text-[32px] leading-[1.1] font-extrabold tracking-[-0.03em]">
        Administración de DealCommerce
      </h1>
      <p className="mt-4 text-[17px] leading-[1.55] text-pizarra">
        Desde acá se administran las tiendas suscritas a la plataforma.
      </p>
      <p className="mt-3 text-[15px] leading-[1.55] text-pizarra">
        La pantalla con el listado de tiendas, su estado de suscripción y sus cuentas todavía no
        está construida.
      </p>
    </div>
  );
}
