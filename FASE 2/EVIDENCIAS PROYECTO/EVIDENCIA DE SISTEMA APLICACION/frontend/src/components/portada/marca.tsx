/*
 * Marca de DealCommerce.
 *
 * El isotipo es una escalera ascendente con un punto: crecimiento y un pedido.
 * Se dibuja en línea y no como archivo porque son dos trazos y así hereda el
 * tamaño sin una petición más.
 */

export function Isotipo({ tamano = 30 }: { tamano?: number }) {
  return (
    <svg width={tamano} height={tamano} viewBox="0 0 30 30" aria-hidden="true">
      <path d="M3 27V20H9V14H15V6H25Q28 6 28 9V24Q28 27 25 27Z" fill="#1F4E79" />
      <circle cx="22.5" cy="11.5" r="2.4" fill="#F7F6F2" />
    </svg>
  );
}

export function Marca({ tamano = 30, tamanoTexto = 20 }: { tamano?: number; tamanoTexto?: number }) {
  return (
    <>
      <Isotipo tamano={tamano} />
      <span
        className="font-jakarta font-extrabold tracking-[-0.02em]"
        style={{ fontSize: `${tamanoTexto}px` }}
      >
        DealCommerce
      </span>
    </>
  );
}
