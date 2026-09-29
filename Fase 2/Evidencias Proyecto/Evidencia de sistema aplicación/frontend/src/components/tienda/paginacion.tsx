import Link from "next/link";

type Props = {
  base: string;
  paginaActual: number;
  totalPaginas: number;
};

/** Paginación del catálogo (mockup 1B). */
export function Paginacion({ base, paginaActual, totalPaginas }: Props) {
  if (totalPaginas <= 1) {
    return null;
  }

  const paginas = Array.from({ length: totalPaginas }, (_, indice) => indice + 1);

  return (
    <nav aria-label="Paginación" className="flex items-center justify-center gap-2 pb-[70px]">
      {paginas.map((numero) =>
        numero === paginaActual ? (
          <span
            key={numero}
            aria-current="page"
            className="flex size-[38px] items-center justify-center rounded-[10px] bg-violeta text-[13px] font-semibold text-white"
          >
            {numero}
          </span>
        ) : (
          <Link
            key={numero}
            href={`${base}?pagina=${numero}`}
            className="flex size-[38px] items-center justify-center rounded-[10px] border border-lila/20 text-[13px] text-texto-suave transition-colors hover:text-texto"
          >
            {numero}
          </Link>
        ),
      )}

      {paginaActual < totalPaginas && (
        <Link
          href={`${base}?pagina=${paginaActual + 1}`}
          className="ml-2 flex h-[38px] items-center rounded-[10px] border border-lila/20 px-4 text-[13px] text-texto"
        >
          Siguiente →
        </Link>
      )}
    </nav>
  );
}
