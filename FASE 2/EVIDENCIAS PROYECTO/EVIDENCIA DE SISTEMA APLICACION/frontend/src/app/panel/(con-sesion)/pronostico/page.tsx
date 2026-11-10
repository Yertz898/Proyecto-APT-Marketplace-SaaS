import { Cabecera, SinConectar } from "@/components/panel/piezas";

export const metadata = { title: "Pronóstico" };

export default function PaginaPronostico() {
  return (
    <>
      <Cabecera titulo="Pronóstico" descripcion="Qué categorías van a pedirte el próximo mes." />
      <SinConectar seccion="El pronóstico" />
    </>
  );
}
