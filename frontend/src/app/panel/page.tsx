import { redirect } from "next/navigation";

// La carga masiva es, por ahora, la única sección del panel.
export default function PaginaPanel() {
  redirect("/panel/cargas");
}
