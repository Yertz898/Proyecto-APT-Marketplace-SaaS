import { GuardiaDelPanel } from "@/components/panel/guardia";
import { NavegacionPanel } from "@/components/panel/navegacion";

/*
 * Todo el panel salvo el formulario de entrada.
 *
 * El grupo no cambia ninguna dirección: /panel y /panel/cargas siguen siendo
 * las mismas. Lo único que hace es dejar afuera a /panel/entrar, que no puede
 * estar detrás del guardia que redirige hacia él.
 */
export default function LayoutConSesion({ children }: LayoutProps<"/panel">) {
  return (
    <>
      <NavegacionPanel />
      <main className="mx-auto w-full max-w-[1100px] flex-1 px-5 py-8 lg:px-8 lg:py-10">
        <GuardiaDelPanel>{children}</GuardiaDelPanel>
      </main>
    </>
  );
}
