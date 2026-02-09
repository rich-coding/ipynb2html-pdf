# ipynb2html-pdf

Un convertidor profesional de Jupyter Notebook a HTML y PDF con una estructura moderna de Python, interfaz de línea de comandos (CLI) y GUI.

## Características

- **Conversión Limpia**: Automatiza la limpieza de los notebooks eliminando metadatos problemáticos y estados de widgets antes de la conversión.
- **Interfaz Dual**: Usa la sencilla GUI de Tkinter o la potente Interfaz de Línea de Comandos (CLI).
- **Gestión Automática de Dependencias**: Puede instalar opcionalmente paquetes de Python faltantes (`nbconvert`, `pyppeteer`, etc.) y paquetes del sistema (`pandoc` en Linux).
- **Herramientas Profesionales**: Gestionado con `uv` y `just`.

## Inicio Rápido

### Requisitos Previos

- [uv](https://github.com/astral-sh/uv) (recomendado) o [pip](https://pip.pypa.io/)
- [just](https://github.com/casey/just) (opcional, para automatización)
- **Tkinter** (Para usuarios de Linux): `sudo apt-get install python3-tk`

### Instalación

```bash
# Usando uv
uv sync
```

### Uso

#### GUI (Interfaz Gráfica)

```bash
just gui
# O TAMBIÉN
uv run ipynb2html-gui
```

#### CLI (Línea de Comandos)

```bash
just cli ruta/al/notebook.ipynb --to pdf
# O TAMBIÉN
uv run ipynb2html ruta/al/notebook.ipynb --to html
```

## Desarrollo

Usamos `just` para gestionar tareas comunes de desarrollo:

- `just setup`: Sincronizar dependencias.
- `just lint`: Ejecutar comprobaciones de Ruff y formateo.
- `just fix`: Corregir automáticamente problemas de linting y formateo.
- `just test`: Ejecutar pruebas unitarias con Pytest.
- `just clean`: Eliminar archivos temporales.

## Estructura del Proyecto

- `src/ipynb2html/`: Código fuente principal del paquete.
  - `converter.py`: Lógica central para conversión y limpieza.
  - `cli.py`: Interfaz de línea de comandos.
  - `gui.py`: Interfaz gráfica de usuario.
- `tests/`: Pruebas unitarias.
- `pyproject.toml`: Configuración del proyecto y dependencias.
- `justfile`: Recetas de automatización.

## Licencia

MIT
