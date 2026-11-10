import { BarraLateral } from "@/components/panel/barra-lateral";
import { GuardiaDelPanel } from "@/components/panel/guardia";

/*
 * Todo el panel salvo el formulario de entrada.
 *
 * El panel lleva la identidad de DealCommerce y no la de la tienda: es una
 * herramienta de la plataforma, igual para todas. La tienda se ve como quiera
 * en su vitrina, que es otra aplicación.
 *
 * El grupo (con-sesion) no cambia ninguna dirección: deja afuera a
 * /panel/entrar, que no puede estar detrás del guardia que redirige hacia él.
 */
export default function LayoutConSesion({ children }: LayoutProps<"/panel">) {
  return (
    <div
      data-tema="claro"
      className="@container flex min-h-dvh w-full flex-col bg-hueso font-inter text-marino lg:flex-row"
    >
      <BarraLateral />

      <main className="min-w-0 flex-1 px-5 py-7 lg:px-9 lg:py-9">
        <div className="mx-auto w-full max-w-[1100px]">
          <GuardiaDelPanel>{children}</GuardiaDelPanel>
        </div>
      </main>
    </div>
  );
}
