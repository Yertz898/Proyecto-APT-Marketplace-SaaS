# Tipografías

Los cuatro archivos de esta carpeta se bajaron de Google Fonts el 22-10-2026 y
están versionados a propósito: antes se pedían a Google en cada compilación, y
un cambio de formato de su parte rompió el build sin que nadie tocara el código.

Cada archivo es la versión **variable** de la familia, recortada al subconjunto
latino. Un archivo por familia cubre todo el rango de pesos que usa la interfaz.

| Archivo | Familia | Pesos | Diseño |
|---|---|---|---|
| `cormorant-garamond-variable.woff2` | Cormorant Garamond | 400–700 | Christian Thalmann |
| `manrope-variable.woff2` | Manrope | 200–800 | Mikhail Sharanda |
| `inter-variable.woff2` | Inter | 400–600 | Rasmus Andersson |
| `plus-jakarta-sans-variable.woff2` | Plus Jakarta Sans | 600–800 | Tokotype |

## Licencia

Las cuatro se distribuyen bajo la **SIL Open Font License 1.1**, que permite
usarlas, incrustarlas y redistribuirlas, incluso en un producto comercial,
siempre que se conserve este aviso. El texto completo de la licencia está en
<https://openfontlicense.org>.

```
Copyright 2015 the Cormorant Project Authors (github.com/CatharsisFonts/Cormorant)
Copyright 2018 The Manrope Project Authors (https://github.com/googlefonts/manrope)
Copyright 2020 The Inter Project Authors (https://github.com/rsms/inter)
Copyright 2020 The Plus Jakarta Sans Project Authors (https://github.com/tokotype/PlusJakartaSans)
```

## Cómo actualizarlas

Pedirle a Google el CSS de la familia con un User-Agent de Chrome —a un cliente
que no declara soporte de woff2 le responde con formatos antiguos—, tomar la URL
del bloque `/* latin */` y guardar ese `.woff2` con el mismo nombre de archivo:

```bash
curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36" \
  "https://fonts.googleapis.com/css2?family=Inter:wght@400..600&display=swap"
```

Si cambia el rango de pesos, hay que ajustarlo en los dos lados: en la consulta
a Google y en el `weight` de `src/app/layout.tsx`.
