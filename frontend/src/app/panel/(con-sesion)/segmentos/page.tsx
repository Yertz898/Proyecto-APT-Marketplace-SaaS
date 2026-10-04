import { Cabecera, SinConectar } from "@/components/panel/piezas";

export const metadata = { title: "Segmentos" };

export default function PaginaSegmentos() {
  return (
    <>
      <Cabecera titulo="Segmentos" descripcion="Quiénes compran seguido y quiénes se están yendo." />
      <SinConectar seccion="La segmentación" />
    </>
  );
}
