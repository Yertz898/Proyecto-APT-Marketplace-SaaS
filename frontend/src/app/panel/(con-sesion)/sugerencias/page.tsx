import { Cabecera, SinConectar } from "@/components/panel/piezas";

export const metadata = { title: "Sugerencias" };

export default function PaginaSugerencias() {
  return (
    <>
      <Cabecera titulo="Sugerencias" descripcion="Qué conviene rebajar. Tú apruebas cada una." />
      <SinConectar seccion="Las sugerencias" />
    </>
  );
}
