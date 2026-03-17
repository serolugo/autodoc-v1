# AutoDoc V1 — Métodos y técnicas principales

## Python stdlib

**`pathlib.Path`** — manejo de rutas de forma orientada a objetos. Se usa en absolutamente todo el sistema para construir, verificar y manipular rutas de archivos y carpetas sin preocuparse por separadores de Windows vs Linux.

**`csv`** — lectura y escritura de los archivos `tile_index.csv` y `records.csv`. Se usa `csv.writer` para escribir filas y `csv.DictReader` para leer rows como diccionarios.

**`argparse`** — parseo de argumentos de línea de comandos en `cli.py`. Define los subcomandos `init`, `create-tile` y `create-run` con sus flags y rutas.

**`dataclasses`** — los modelos `TileConfig` y `RunConfig` son dataclasses, lo que da tipado claro y construcción limpia sin escribir `__init__` manualmente.

**`shutil`** — copia de archivos (`shutil.copy2`) y limpieza de directorios en `works/`. `copy2` preserva metadatos del archivo original.

**`re`** — expresiones regulares para detectar folders válidos con el patrón `run-\d{3}` en `run_id.py`.

**`datetime`** — obtención de la fecha actual para generar el componente `YYMMDD` del `tile_id`.

**`tempfile`** — creación de directorios temporales aislados en los tests, para que cada test corra en su propio entorno limpio.

---

## PyYAML

**`yaml.safe_load`** — lectura de `tile_config.yaml` y `run_config.yaml`. Se usa `safe_load` en lugar de `load` por seguridad, evita ejecución de código arbitrario en el YAML.

**`yaml.dump`** — solo se usa en los tests para escribir los archivos YAML de prueba. El manifest de producción usa un serializador propio.

---

## Patrones de diseño

**Dataclass + `from_dict`** — los modelos se construyen desde un diccionario raw de YAML. Todos los campos faltantes defaultean a `""` o `False` sin lanzar errores.

**Serialización manual** — `manifest.yaml` no usa PyYAML para escribirse. Tiene su propio serializador `_render_manifest` que produce líneas en blanco entre secciones para legibilidad visual — algo que PyYAML no soporta nativamente.

**Separación de validación** — `validate_create_tile_structure` y `validate_create_run_structure` son funciones separadas porque cada comando requiere un subconjunto distinto de paths obligatorios.

**Detección automática de layout** — `_resolve_vivado_project_root` en `copier.py` detecta si el proyecto Vivado está en Layout A (directo) o Layout B (con wrapper) sin configuración del usuario.

**Copia flat con resolución de colisiones** — `_copy_flat` busca recursivamente en el origen pero copia todo al mismo nivel en el destino. Si dos archivos tienen el mismo nombre aplica sufijos `_1`, `_2` automáticamente.

**Fail soft en categorías vacías** — si una categoría de copia no existe en el proyecto Vivado, retorna `[]` y el run continúa. Solo las rutas que sí existen se registran en `manifest.yaml`.

**Header-on-first-write en CSV** — los archivos CSV se crean vacíos y el header se escribe automáticamente la primera vez que se agrega una fila, siguiendo la spec sección 16.4.

**`.gitkeep` automático** — cada carpeta creada por el sistema recibe un `.gitkeep` para que git la rastree aunque esté vacía.
