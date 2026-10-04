import { Cabecera, SinConectar } from "@/components/panel/piezas";

export const metadata = { title: "Asistente" };

export default function PaginaAsistente() {
  return (
    <>
      <Cabecera titulo="Asistente" descripcion="Pregúntale por las ventas de tu tienda." />
      <SinConectar seccion="El asistente" />
    </>
  );
}
