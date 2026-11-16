"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";

import { ErrorDeApi } from "@/lib/api/errores";
import { cambiarMiembro, crearVendedor, obtenerEquipo, reiniciarClave } from "@/lib/api/gestion";
import { formatearFecha } from "@/lib/formato";
import type { Miembro } from "@/lib/tipos-gestion";

import { Aviso, Boton, Campo, mensajeDe } from "./controles";
import { Cabecera, Cargando, Error, Tarjeta } from "./piezas";

/*
 * Quién atiende la tienda.
 *
 * El dueño crea a sus vendedores con una contraseña inicial, que les entrega
 * por su cuenta. Un vendedor que se va se desactiva, no se borra: sus pedidos
 * y cargas siguen apuntando a él, y una cuenta desactivada no puede entrar.
 */
export function PantallaEquipo() {
  const [equipo, setEquipo] = useState<Miembro[] | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);

  const cargar = useCallback(() => {
    obtenerEquipo().then(setEquipo, (error) => setFallo(mensajeDe(error)));
  }, []);

  useEffect(cargar, [cargar]);

  function reemplazar(miembro: Miembro) {
    setEquipo((actual) => actual?.map((m) => (m.id === miembro.id ? miembro : m)) ?? null);
  }

  return (
    <>
      <Cabecera titulo="Equipo" descripcion="Las personas que atienden tu tienda contigo." />

      {fallo && <Error mensaje={fallo} onReintentar={() => {
            setFallo(null);
            cargar();
          }} />}
      {!fallo && !equipo && <Cargando />}

      {equipo && (
        <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_360px] lg:items-start">
          <Tarjeta className="p-0">
            <ul className="divide-y divide-arena">
              {equipo.map((miembro) => (
                <FilaDeMiembro key={miembro.id} miembro={miembro} onCambio={reemplazar} />
              ))}
            </ul>
          </Tarjeta>
          <NuevoVendedor onCreado={(m) => setEquipo((actual) => [...(actual ?? []), m])} />
        </div>
      )}
    </>
  );
}

function FilaDeMiembro({ miembro, onCambio }: { miembro: Miembro; onCambio: (m: Miembro) => void }) {
  const [trabajando, setTrabajando] = useState(false);
  const [reiniciando, setReiniciando] = useState(false);
  const [clave, setClave] = useState("");
  const [aviso, setAviso] = useState<{ tipo: "ok" | "error"; texto: string } | null>(null);
  const esDueno = miembro.rol === "dueno_tienda";

  async function alternarActivo() {
    setTrabajando(true);
    setAviso(null);
    try {
      onCambio(await cambiarMiembro(miembro.id, { activo: !miembro.activo }));
    } catch (error) {
      setAviso({ tipo: "error", texto: mensajeDe(error) });
    } finally {
      setTrabajando(false);
    }
  }

  async function guardarClave(evento: FormEvent) {
    evento.preventDefault();
    setTrabajando(true);
    setAviso(null);
    try {
      await reiniciarClave(miembro.id, clave);
      setClave("");
      setReiniciando(false);
      setAviso({ tipo: "ok", texto: "Contraseña cambiada. Entrégasela a esta persona por un medio seguro." });
    } catch (error) {
      setAviso({ tipo: "error", texto: error instanceof ErrorDeApi ? (error.de("nueva") ?? error.message) : mensajeDe(error) });
    } finally {
      setTrabajando(false);
    }
  }

  return (
    <li className="p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-[15px] font-semibold text-marino">
            {miembro.nombre}
            {!miembro.activo && (
              <span className="ml-2 rounded-full bg-hueso px-2 py-0.5 text-[11px] font-semibold text-pizarra">
                Desactivado
              </span>
            )}
          </p>
          <p className="text-[13px] text-pizarra">
            {miembro.email} · {miembro.rolNombre} · desde el {formatearFecha(miembro.fechaRegistro)}
          </p>
        </div>
        {!esDueno && (
          <div className="flex flex-wrap gap-2">
            <Boton variante="secundario" className="h-9 px-3 text-[13px]" disabled={trabajando} onClick={() => setReiniciando((v) => !v)}>
              Cambiar contraseña
            </Boton>
            <Boton
              variante={miembro.activo ? "secundario" : "principal"}
              className="h-9 px-3 text-[13px]"
              disabled={trabajando}
              onClick={alternarActivo}
            >
              {miembro.activo ? "Desactivar" : "Reactivar"}
            </Boton>
          </div>
        )}
      </div>
      {reiniciando && (
        <form onSubmit={guardarClave} className="mt-3 flex flex-wrap items-end gap-2">
          <div className="min-w-[220px] flex-1">
            <Campo
              id={`clave-${miembro.id}`}
              etiqueta="Contraseña nueva"
              type="text"
              autoComplete="off"
              value={clave}
              onChange={(e) => setClave(e.target.value)}
            />
          </div>
          <Boton type="submit" disabled={trabajando || clave.length < 8}>
            Guardar
          </Boton>
        </form>
      )}
      {aviso && <Aviso tipo={aviso.tipo}>{aviso.texto}</Aviso>}
    </li>
  );
}

function NuevoVendedor({ onCreado }: { onCreado: (m: Miembro) => void }) {
  const [nombre, setNombre] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [errores, setErrores] = useState<Record<string, string | null>>({});
  const [aviso, setAviso] = useState<{ tipo: "ok" | "error"; texto: string } | null>(null);

  async function crear(evento: FormEvent) {
    evento.preventDefault();
    setGuardando(true);
    setErrores({});
    setAviso(null);
    try {
      onCreado(await crearVendedor({ nombre, email, password }));
      setNombre("");
      setEmail("");
      setPassword("");
      setAviso({ tipo: "ok", texto: "Listo. Ya puede iniciar sesión en el panel con ese correo y contraseña." });
    } catch (error) {
      if (error instanceof ErrorDeApi && Object.keys(error.detalles).length) {
        setErrores({ nombre: error.de("nombre"), email: error.de("email"), password: error.de("password") });
      } else {
        setAviso({ tipo: "error", texto: mensajeDe(error) });
      }
    } finally {
      setGuardando(false);
    }
  }

  return (
    <Tarjeta>
      <form onSubmit={crear} noValidate className="flex flex-col gap-4">
        <div>
          <p className="text-[13px] font-semibold text-marino">Agregar vendedor</p>
          <p className="mt-1 text-[13px] text-pizarra">
            Un vendedor hace lo mismo que tú, salvo el plan y el equipo.
          </p>
        </div>
        <Campo id="nv-nombre" etiqueta="Nombre" value={nombre} onChange={(e) => setNombre(e.target.value)} error={errores.nombre} />
        <Campo id="nv-email" etiqueta="Correo" type="email" value={email} onChange={(e) => setEmail(e.target.value)} error={errores.email} />
        <Campo
          id="nv-password"
          etiqueta="Contraseña inicial"
          type="text"
          autoComplete="off"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={errores.password}
          ayuda="Entrégasela tú; podrá cambiarla desde su cuenta."
        />
        <div>
          <Boton type="submit" disabled={guardando || !nombre || !email || !password}>
            {guardando ? "Creando…" : "Crear vendedor"}
          </Boton>
        </div>
        {aviso && <Aviso tipo={aviso.tipo}>{aviso.texto}</Aviso>}
      </form>
    </Tarjeta>
  );
}
