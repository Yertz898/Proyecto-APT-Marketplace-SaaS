import { Cabecera, Proximamente } from "@/components/panel/piezas";

export const metadata = { title: "Agenda" };

/**
 * La agenda está construida y funcionando en la vitrina, pero el panel del
 * dueño queda congelado hasta que el cliente confirme que la quiere.
 */
export default function PaginaAgenda() {
  return (
    <>
      <Cabecera titulo="Agenda de visitas" descripcion="Visitas con hora a tu tienda." />
      <Proximamente
        titulo="Tus clientes podrán reservar hora"
        detalle="Defines tus horarios de atención y cuántas visitas aceptas a la vez. Cada solicitud llega acá para que la aceptes o la rechaces. Está en pausa hasta confirmarlo contigo."
      />
    </>
  );
}
