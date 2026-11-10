import { Cabecera, SinConectar } from "@/components/panel/piezas";

export const metadata = { title: "Pedidos" };

export default function PaginaPedidos() {
  return (
    <>
      <Cabecera titulo="Pedidos" descripcion="Qué te pidieron y en qué va cada uno." />
      <SinConectar seccion="El listado de pedidos" />
    </>
  );
}
