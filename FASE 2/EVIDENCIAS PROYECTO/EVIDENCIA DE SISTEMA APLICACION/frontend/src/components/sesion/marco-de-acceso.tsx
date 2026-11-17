import Link from "next/link";

import { Marca } from "@/components/portada/marca";

/** El marco claro de DealCommerce que comparten las páginas de acceso. */
export function MarcoDeAcceso({ children }: { children: React.ReactNode }) {
  return (
    <div data-tema="claro" className="@container flex min-h-dvh w-full flex-col bg-hueso font-inter text-marino">
      <header className="border-b border-arena">
        <div className="mx-auto flex max-w-[1280px] items-center px-[clamp(20px,5.5cqi,80px)] py-[14px]">
          <Link href="/" className="flex items-center gap-2.5 text-marino no-underline hover:no-underline">
            <Marca />
          </Link>
        </div>
      </header>
      <main className="mx-auto w-full max-w-[420px] flex-1 px-5 py-14">{children}</main>
    </div>
  );
}
