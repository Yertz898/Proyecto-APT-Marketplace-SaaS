"use client";

import Image from "next/image";
import { useState } from "react";

import { Campo } from "@/components/campo";
import { ErrorDeApi } from "@/lib/api/errores";
import {
  crearProducto,
  editarProducto,
  type CambiosDelProducto,
} from "@/lib/api/catalogo-panel";
import type { FormaVenta, UnidadMedida } from "@/lib/tipos";
import type { CategoriaDelPanel, ProductoDelPanel } from "@/lib/tipos-panel";
import { cn } from "@/lib/utils";

/*
 * Crear o editar un producto.
 *
 * Es el mismo formulario para las tres formas de venta porque son el mismo
 * producto: lo que cambia es qué campos tienen sentido. Elegir «por peso»
 * reemplaza las unidades por gramos o kilos; elegir «por lote» habilita las
 * piezas. Los campos que no aplican no se esconden a medias: no se muestran.
 *
 * Quien valida de verdad es el backend. Lo de acá es cortesía: evitar un viaje
 * para errores obvios y mostrar el error donde corresponde cuando vuelve.
 */

const FORMAS: { valor: FormaVenta; nombre: string; detalle: string }[] = [
  { valor: "unidad", nombre: "Por unidad", detalle: "Una pieza a la vez." },
  { valor: "lote", nombre: "Por lote", detalle: "Un conjunto que se compra entero." },
  { valor: "peso", nombre: "Por peso", detalle: "Se cobra por gramo o por kilo." },
];

const UNIDADES_DE_PESO: UnidadMedida[] = ["g", "kg"];

type Borrador = {
  codigo: string;
  nombre: string;
  descripcion: string;
  categoria: string;
  formaVenta: FormaVenta;
  unidadMedida: UnidadMedida;
  precioNeto: string;
  controlaStock: boolean;
  stock: string;
  cantidadMinima: string;
  cantidadPiezas: string;
  activo: boolean;
};

function borradorDe(producto?: ProductoDelPanel): Borrador {
  if (!producto) {
    return {
      codigo: "",
      nombre: "",
      descripcion: "",
      categoria: "",
      formaVenta: "unidad",
      unidadMedida: "unidad",
      precioNeto: "",
      controlaStock: true,
      stock: "0",
      cantidadMinima: "1",
      cantidadPiezas: "",
      activo: true,
    };
  }

  return {
    codigo: producto.codigo,
    nombre: producto.nombre,
    descripcion: producto.descripcion,
    categoria: producto.categoria ?? "",
    formaVenta: producto.formaVenta,
    unidadMedida: producto.unidadMedida,
    precioNeto: String(producto.precioNeto),
    controlaStock: producto.controlaStock,
    stock: producto.stock === null ? "0" : String(producto.stock),
    cantidadMinima: String(producto.cantidadMinima),
    cantidadPiezas:
      producto.cantidadPiezas === null ? "" : String(producto.cantidadPiezas),
    activo: producto.activo,
  };
}

export function FormularioDeProducto({
  producto,
  categorias,
  onGuardado,
  onCancelar,
}: {
  /** Sin producto, el formulario crea uno nuevo. */
  producto?: ProductoDelPanel;
  categorias: CategoriaDelPanel[];
  onGuardado: (producto: ProductoDelPanel) => void;
  onCancelar: () => void;
}) {
  const [borrador, setBorrador] = useState(() => borradorDe(producto));
  const [foto, setFoto] = useState<File | null>(null);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState<ErrorDeApi | null>(null);

  const esNuevo = !producto;
  const porPeso = borrador.formaVenta === "peso";
  const porLote = borrador.formaVenta === "lote";

  function cambiar<C extends keyof Borrador>(campo: C, valor: Borrador[C]) {
    setBorrador((actual) => ({ ...actual, [campo]: valor }));
  }

  /**
   * Cambiar la forma de venta arrastra la unidad y las piezas.
   *
   * Si no, queda un producto «por peso» medido en unidades, que el backend
   * rechaza con razón pero el formulario deja escribir.
   */
  function cambiarForma(forma: FormaVenta) {
    setBorrador((actual) => ({
      ...actual,
      formaVenta: forma,
      unidadMedida: forma === "peso" ? "g" : "unidad",
      cantidadPiezas: forma === "lote" ? actual.cantidadPiezas : "",
    }));
  }

  async function enviar(evento: React.FormEvent) {
    evento.preventDefault();
    setGuardando(true);
    setError(null);

    const cambios: CambiosDelProducto = {
      codigo: borrador.codigo.trim(),
      nombre: borrador.nombre.trim(),
      descripcion: borrador.descripcion.trim(),
      categoria: borrador.categoria,
      formaVenta: borrador.formaVenta,
      unidadMedida: borrador.unidadMedida,
      precioNeto: numero(borrador.precioNeto),
      controlaStock: borrador.controlaStock,
      stock: borrador.controlaStock ? numero(borrador.stock) : null,
      cantidadMinima: numero(borrador.cantidadMinima),
      cantidadPiezas: porLote ? numero(borrador.cantidadPiezas) : null,
      activo: borrador.activo,
    };
    if (foto) {
      cambios.foto = foto;
    }

    try {
      const guardado = esNuevo
        ? await crearProducto(cambios)
        : await editarProducto(producto.codigo, cambios);
      onGuardado(guardado);
    } catch (fallo: unknown) {
      setError(fallo instanceof ErrorDeApi ? fallo : null);
    } finally {
      setGuardando(false);
    }
  }

  return (
    <form onSubmit={enviar} noValidate className="flex flex-col gap-5">
      <section className="flex flex-col gap-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <Campo
            id="codigo"
            etiqueta="Código"
            tema="claro"
            valor={borrador.codigo}
            onCambio={(valor) => cambiar("codigo", valor)}
            ayuda="Como lo llamas tú. Es la clave de la carga masiva."
            error={error?.de("codigo")}
          />
          <Campo
            id="nombre"
            etiqueta="Nombre"
            tema="claro"
            valor={borrador.nombre}
            onCambio={(valor) => cambiar("nombre", valor)}
            error={error?.de("nombre")}
          />
        </div>

        <Campo
          id="descripcion"
          etiqueta="Descripción"
          tema="claro"
          requerido={false}
          multilinea
          valor={borrador.descripcion}
          onCambio={(valor) => cambiar("descripcion", valor)}
          ayuda="Lo que el comprador necesita saber antes de decidir."
          error={error?.de("descripcion")}
        />
      </section>

      <section>
        <p className="text-[13px] font-semibold text-marino">Cómo se vende</p>
        <div className="mt-2 grid gap-2 sm:grid-cols-3">
          {FORMAS.map((forma) => (
            <button
              key={forma.valor}
              type="button"
              onClick={() => cambiarForma(forma.valor)}
              aria-pressed={borrador.formaVenta === forma.valor}
              className={cn(
                "cursor-pointer rounded-[12px] border px-4 py-3 text-left transition-colors",
                borrador.formaVenta === forma.valor
                  ? "border-acero bg-cielo"
                  : "border-arena hover:bg-hueso",
              )}
            >
              <span className="block text-[14px] font-semibold text-marino">
                {forma.nombre}
              </span>
              <span className="block text-[12px] text-pizarra">{forma.detalle}</span>
            </button>
          ))}
        </div>

        {porPeso && (
          <div className="mt-3 flex items-center gap-2">
            <span className="text-[13px] text-pizarra">Se mide en</span>
            {UNIDADES_DE_PESO.map((unidad) => (
              <button
                key={unidad}
                type="button"
                onClick={() => cambiar("unidadMedida", unidad)}
                aria-pressed={borrador.unidadMedida === unidad}
                className={cn(
                  "h-9 cursor-pointer rounded-[10px] border px-3 text-[13px]",
                  borrador.unidadMedida === unidad
                    ? "border-acero bg-cielo font-semibold text-acero"
                    : "border-arena text-marino hover:bg-hueso",
                )}
              >
                {unidad}
              </button>
            ))}
          </div>
        )}
      </section>

      <section className="grid gap-4 sm:grid-cols-2">
        <Campo
          id="precioNeto"
          etiqueta="Precio neto"
          tema="claro"
          tipo="text"
          valor={borrador.precioNeto}
          onCambio={(valor) => cambiar("precioNeto", valor)}
          ayuda={
            porPeso
              ? `En pesos, por ${borrador.unidadMedida}. Sin IVA.`
              : "En pesos, sin IVA."
          }
          error={error?.de("precioNeto") ?? error?.de("precio_neto")}
        />

        <div>
          <label htmlFor="categoria" className="text-[13px] font-semibold text-marino">
            Categoría <span className="font-normal text-pizarra">(opcional)</span>
          </label>
          <select
            id="categoria"
            value={borrador.categoria}
            onChange={(evento) => cambiar("categoria", evento.target.value)}
            className="mt-2 h-12 w-full cursor-pointer rounded-[12px] border border-niebla bg-white px-3 text-base text-marino outline-none focus-visible:border-acero"
          >
            <option value="">Sin categoría</option>
            {categorias.map((categoria) => (
              <option key={categoria.id} value={categoria.nombre}>
                {categoria.nombre}
              </option>
            ))}
          </select>
          {error?.de("categoria") && (
            <p className="mt-1.5 text-xs font-medium text-ambar-hondo">
              {error.de("categoria")}
            </p>
          )}
        </div>

        {porLote && (
          <Campo
            id="cantidadPiezas"
            etiqueta="Piezas por lote"
            tema="claro"
            valor={borrador.cantidadPiezas}
            onCambio={(valor) => cambiar("cantidadPiezas", valor)}
            ayuda="Cuántas piezas trae el lote completo."
            error={error?.de("cantidad_piezas") ?? error?.de("cantidadPiezas")}
          />
        )}

        <Campo
          id="cantidadMinima"
          etiqueta="Compra mínima"
          tema="claro"
          requerido={false}
          valor={borrador.cantidadMinima}
          onCambio={(valor) => cambiar("cantidadMinima", valor)}
          ayuda={`Lo menos que se puede llevar, en ${
            porPeso ? borrador.unidadMedida : "unidades"
          }.`}
          error={error?.de("cantidad_minima") ?? error?.de("cantidadMinima")}
        />
      </section>

      <section className="rounded-[12px] border border-arena bg-hueso p-4">
        <label className="flex cursor-pointer items-start gap-3">
          <input
            type="checkbox"
            checked={borrador.controlaStock}
            onChange={(evento) => cambiar("controlaStock", evento.target.checked)}
            className="mt-1 size-4 cursor-pointer accent-[#1f4e79]"
          />
          <span className="text-[13px] text-pizarra">
            <span className="block font-semibold text-marino">Llevar inventario</span>
            Si lo desmarcas, el producto se muestra mientras esté activo y tú decides
            cuándo sacarlo. Es lo que corresponde cuando no cuentas lo que te queda.
          </span>
        </label>

        {borrador.controlaStock && (
          <div className="mt-4 max-w-[220px]">
            <Campo
              id="stock"
              etiqueta={`Cuánto tienes${porPeso ? ` (${borrador.unidadMedida})` : ""}`}
              tema="claro"
              valor={borrador.stock}
              onCambio={(valor) => cambiar("stock", valor)}
              error={error?.de("stock")}
            />
          </div>
        )}
      </section>

      <section>
        <label htmlFor="foto" className="text-[13px] font-semibold text-marino">
          Foto <span className="font-normal text-pizarra">(opcional)</span>
        </label>

        <div className="mt-2 flex items-center gap-4">
          {foto ? (
            <span className="flex size-16 shrink-0 items-center justify-center rounded-[10px] border border-acero bg-cielo px-1 text-center text-[11px] font-semibold text-acero">
              Nueva foto
            </span>
          ) : (
            producto?.foto && (
              <Image
                src={producto.foto.url}
                alt={producto.foto.alt}
                width={64}
                height={64}
                className="size-16 shrink-0 rounded-[10px] border border-arena object-cover"
              />
            )
          )}

          <input
            id="foto"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={(evento) => setFoto(evento.target.files?.[0] ?? null)}
            className="block w-full cursor-pointer rounded-[12px] border border-dashed border-arena-honda bg-hueso p-3 text-[13px] text-pizarra file:mr-3 file:cursor-pointer file:rounded-[10px] file:border-0 file:bg-acero file:px-3 file:py-1.5 file:text-[13px] file:font-semibold file:text-white"
          />
        </div>

        {error?.de("foto") ? (
          <p className="mt-1.5 text-xs font-medium text-ambar-hondo">{error.de("foto")}</p>
        ) : (
          <p className="mt-1.5 text-xs text-pizarra">
            JPG, PNG o WEBP, hasta 3 MB. Se revisa el contenido, no el nombre del archivo.
          </p>
        )}
      </section>

      <label className="flex cursor-pointer items-center gap-2.5">
        <input
          type="checkbox"
          checked={borrador.activo}
          onChange={(evento) => cambiar("activo", evento.target.checked)}
          className="size-4 cursor-pointer accent-[#1f4e79]"
        />
        <span className="text-[13px] text-marino">Mostrar en mi tienda</span>
      </label>

      <div className="flex flex-wrap items-center gap-3">
        <button
          type="submit"
          disabled={guardando}
          className="h-11 cursor-pointer rounded-[12px] bg-acero px-6 text-sm font-semibold text-white transition-colors hover:bg-acero-hondo disabled:cursor-not-allowed disabled:opacity-50"
        >
          {guardando ? "Guardando…" : esNuevo ? "Crear producto" : "Guardar cambios"}
        </button>
        <button
          type="button"
          onClick={onCancelar}
          className="h-11 cursor-pointer rounded-[12px] border border-niebla px-5 text-sm font-semibold text-acero transition-colors hover:bg-cielo"
        >
          Cancelar
        </button>

        {error && !error.de("codigo") && !error.de("foto") && (
          <p role="alert" className="text-[13px] text-ambar-hondo">
            {error.message}
          </p>
        )}
      </div>
    </form>
  );
}

/** Acepta coma decimal, que es como se escribe un decimal en Chile. */
function numero(texto: string): number {
  const valor = Number(texto.trim().replace(",", "."));
  return Number.isFinite(valor) ? valor : 0;
}
