# data

Los datos crudos del cliente. **Nada de esta carpeta se versiona**, salvo este
archivo: el repositorio es público y lo que hay acá son ventas reales de una
tienda real, con nombres y teléfonos de personas que no dieron permiso para
publicarlos.

## Qué va acá

    data/
      historial-ventas/     el historial de pedidos que entregó el cliente
      modelos/              lo que entrenan el pronóstico y la segmentación

El historial entra al sistema con un comando, no a mano:

    docker compose exec api python manage.py importar_historial data/historial-ventas/<archivo>

El comando normaliza, valida y deja los pedidos en la base. Lo que llega acá
no se edita: si una fila está mala, se corrige en el importador y se anota por
qué, porque el archivo original es la única copia de esas ventas.

## Por qué existe

Joyas_ye no lleva registro digital de sus ventas. El único historial es el que
reconstruyó el equipo, y sin él no hay con qué entrenar el pronóstico de
demanda ni la segmentación de compradores del Sprint 4.
