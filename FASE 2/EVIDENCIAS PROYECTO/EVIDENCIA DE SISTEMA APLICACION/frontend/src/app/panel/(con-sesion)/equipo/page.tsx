import { Cabecera, SinConectar } from "@/components/panel/piezas";

export const metadata = { title: "Equipo" };

export default function PaginaEquipo() {
  return (
    <>
      <Cabecera titulo="Equipo" descripcion="Quién más atiende tu tienda." />
      <SinConectar seccion="La gestión del equipo" />
    </>
  );
}
