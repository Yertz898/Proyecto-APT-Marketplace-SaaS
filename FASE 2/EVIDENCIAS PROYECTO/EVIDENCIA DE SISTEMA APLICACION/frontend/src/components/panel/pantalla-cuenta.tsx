"use client";

import { useState, type FormEvent } from "react";

import { useSesion } from "@/components/sesion/usar-sesion";
import { ErrorDeApi } from "@/lib/api/errores";
import { cambiarContrasena, cambiarNombre } from "@/lib/api/gestion";
import { cerrarSesion } from "@/lib/api/sesion";

import { Aviso, Boton, Campo, mensajeDe } from "./controles";
import { Cabecera, Cargando, Tarjeta } from "./piezas";

/*
 * La cuenta de quien usa el panel: su nombre, su contraseña y su sesión.
 *
 * El correo no se edita desde acá: es con lo que se inicia sesión, y cambiarlo
 * sin verificar el nuevo dejaría la cuenta en manos de un error de tipeo.
 */
export function PantallaCuenta() {
  const { sesion, hidratado } = useSesion();

  if (!hidratado || !sesion) return <Cargando />;

  return (
    <>
      <Cabecera titulo="Tu cuenta" descripcion="Tus datos, tu contraseña y tu sesión." />

      <div className="grid gap-4 lg:grid-cols-2">
        <DatosPersonales
          nombreActual={sesion.usuario.nombre}
          email={sesion.usuario.email}
          rol={sesion.usuario.rolNombre}
        />
        <CambioDeContrasena />
      </div>

      <Tarjeta className="mt-4">
        <p className="text-[13px] font-semibold text-marino">Sesión</p>
        <p className="mt-1 text-[14px] text-pizarra">Cierra la sesión en este navegador.</p>
        <Boton variante="secundario" className="mt-4" onClick={cerrarSesion}>
          Cerrar sesión
        </Boton>
      </Tarjeta>
    </>
  );
}

type Resultado = { tipo: "ok" | "error"; texto: string } | null;

function DatosPersonales({ nombreActual, email, rol }: { nombreActual: string; email: string; rol: string }) {
  const [nombre, setNombre] = useState(nombreActual);
  const [guardando, setGuardando] = useState(false);
  const [resultado, setResultado] = useState<Resultado>(null);

  async function guardar(evento: FormEvent) {
    evento.preventDefault();
    if (!nombre.trim()) return;
    setGuardando(true);
    setResultado(null);
    try {
      await cambiarNombre(nombre.trim());
      setResultado({ tipo: "ok", texto: "Guardamos tu nombre." });
    } catch (error) {
      setResultado({ tipo: "error", texto: mensajeDe(error) });
    } finally {
      setGuardando(false);
    }
  }

  return (
    <Tarjeta>
      <form onSubmit={guardar} className="flex flex-col gap-4">
        <p className="text-[13px] font-semibold text-marino">Tus datos</p>
        <Campo
          id="nombre"
          etiqueta="Nombre"
          value={nombre}
          onChange={(e) => setNombre(e.target.value)}
          maxLength={150}
        />
        <Campo
          id="correo"
          etiqueta="Correo"
          value={email}
          disabled
          ayuda="Es con lo que inicias sesión; no se cambia desde acá."
        />
        <p className="text-[13px] text-pizarra">
          Rol: <span className="font-semibold text-marino">{rol}</span>
        </p>
        <div>
          <Boton type="submit" disabled={guardando || !nombre.trim() || nombre.trim() === nombreActual}>
            {guardando ? "Guardando…" : "Guardar nombre"}
          </Boton>
        </div>
        {resultado && <Aviso tipo={resultado.tipo}>{resultado.texto}</Aviso>}
      </form>
    </Tarjeta>
  );
}

function CambioDeContrasena() {
  const [actual, setActual] = useState("");
  const [nueva, setNueva] = useState("");
  const [repetida, setRepetida] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [errores, setErrores] = useState<Record<string, string | null>>({});
  const [resultado, setResultado] = useState<Resultado>(null);

  async function guardar(evento: FormEvent) {
    evento.preventDefault();
    setResultado(null);
    if (nueva !== repetida) {
      setErrores({ repetida: "Las dos contraseñas nuevas no coinciden." });
      return;
    }
    setErrores({});
    setGuardando(true);
    try {
      await cambiarContrasena(actual, nueva);
      setActual("");
      setNueva("");
      setRepetida("");
      setResultado({ tipo: "ok", texto: "Cambiamos tu contraseña." });
    } catch (error) {
      if (error instanceof ErrorDeApi && (error.de("actual") || error.de("nueva"))) {
        setErrores({ actual: error.de("actual"), nueva: error.de("nueva") });
      } else {
        setResultado({ tipo: "error", texto: mensajeDe(error) });
      }
    } finally {
      setGuardando(false);
    }
  }

  return (
    <Tarjeta>
      <form onSubmit={guardar} noValidate className="flex flex-col gap-4">
        <p className="text-[13px] font-semibold text-marino">Cambiar contraseña</p>
        <Campo
          id="actual"
          etiqueta="Contraseña actual"
          type="password"
          autoComplete="current-password"
          value={actual}
          onChange={(e) => setActual(e.target.value)}
          error={errores.actual}
        />
        <Campo
          id="nueva"
          etiqueta="Contraseña nueva"
          type="password"
          autoComplete="new-password"
          value={nueva}
          onChange={(e) => setNueva(e.target.value)}
          error={errores.nueva}
          ayuda="Al menos 8 caracteres, que no sea solo números ni una muy común."
        />
        <Campo
          id="repetida"
          etiqueta="Repite la contraseña nueva"
          type="password"
          autoComplete="new-password"
          value={repetida}
          onChange={(e) => setRepetida(e.target.value)}
          error={errores.repetida}
        />
        <div>
          <Boton type="submit" disabled={guardando || !actual || !nueva || !repetida}>
            {guardando ? "Cambiando…" : "Cambiar contraseña"}
          </Boton>
        </div>
        {resultado && <Aviso tipo={resultado.tipo}>{resultado.texto}</Aviso>}
      </form>
    </Tarjeta>
  );
}
