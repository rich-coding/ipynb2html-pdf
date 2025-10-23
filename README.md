# ipynb2html - Simple Notebook Converter

Esta pequeña utilidad proporciona una interfaz gráfica (Tkinter) para convertir archivos Jupyter Notebook (`.ipynb`) a HTML o PDF usando `jupyter nbconvert`.

Características
- Interfaz gráfica sencilla para seleccionar el notebook y elegir HTML o PDF.
- Opción para instalar automáticamente dependencias Python faltantes (usa `pip` con el mismo intérprete que ejecuta la app).
- En Linux (Debian/Ubuntu) puede intentar instalar `pandoc` y `texlive-xetex` con `sudo apt-get` si falta.
- Limpia metadatos problemáticos del notebook antes de la conversión.

Detalles de la limpieza
- El conversor crea una copia "limpia" del notebook usando `nbformat` y reconstuye las salidas (outputs) conservando sólo los campos permitidos por el esquema oficial.
- Se omiten explícitamente las salidas de widgets (MIME types como `application/vnd.jupyter.widget-view+json`) porque suelen incluir estado complejo que rompe la validación de `nbformat` y `nbconvert`.

Uso desde la GUI
1. Ejecuta la app:

```bash
python3 ipynb2html.py
```

2. En la ventana: selecciona un archivo `.ipynb`, marca la casilla "Instalar dependencias si faltan" si quieres que la app intente instalar paquetes automáticamente, elige HTML o PDF y pulsa "Convertir".

Línea de comandos (modo rápido)
Si prefieres no abrir la GUI puedes usar directamente `jupyter nbconvert` sobre el archivo creado por la función de limpieza; por ejemplo:

```bash
# Primero, desde Python, genera el archivo limpio (ejemplo de uso):
python3 - <<'PY'
import importlib.util
spec = importlib.util.spec_from_file_location('ipnbmod', 'ipynb2html.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
conv = mod.NotebookConverter(master=None)
clean = conv.clean_notebook('MiNotebook.ipynb')
print(clean)
PY

# Luego convierte con nbconvert:
jupyter nbconvert MiNotebook.ipynb.clean --to html --template classic
```

Dependencias y notas
- Recomendado instalar en un entorno virtual (venv/virtualenv/conda).
- `requirements.txt` contiene las recomendaciones mínimas: `nbconvert`, `pyppeteer`, `nbformat`.
- Para conversión a PDF pueden ser necesarias dependencias adicionales:
	- Chromium (pyppeteer o playwright lo descargan/instalan),
	- `pandoc` y `texlive-xetex` para ciertos flujos de nbconvert (en Debian/Ubuntu se puede instalar con `sudo apt-get install pandoc texlive-xetex`).

Solución de problemas
- Si nbconvert falla con errores de JSON o validación: asegúrate de ejecutar la limpieza (`clean_notebook`) antes de convertir. La GUI lo hace automáticamente.
- Si la instalación automática falla en Linux con `sudo` pídete ejecutar manualmente:
	```bash
	sudo apt-get update && sudo apt-get install -y pandoc texlive-xetex
	```
- Para problemas con la descarga de Chromium por `pyppeteer`, prueba a ejecutar `pyppeteer-install` o instalar `playwright` y ejecutar `playwright install`.

Contacto
Si quieres que añada soporte de línea de comandos directo al script (por ejemplo `--convert file.ipynb --format pdf`), puedo añadirlo.

Archivos
- `ipynb2html.py` - Aplicación principal (GUI).
- `requirements.txt` - Paquetes recomendados: `nbconvert`, `pyppeteer`.

Uso
1. Ejecuta la app:

```bash
python3 ipynb2html.py
```

2. En la ventana: selecciona un archivo `.ipynb`, marca la casilla "Instalar dependencias si faltan" si quieres que la app intente instalar paquetes automáticamente, elige HTML o PDF y pulsa "Convertir".

Notas
- La app intentará instalar paquetes con `pip` usando el intérprete Python actual (por ejemplo, `python3 -m pip install ...`).
- Para PDF, nbconvert puede necesitar un motor de navegación (Chromium) y paquetes TeX para renderizar libros complejos. Si la app no puede instalar Chromium o pandoc automáticamente, deberás instalarlos manualmente.
- Si tu entorno usa `playwright` en lugar de `pyppeteer`, instala `playwright` y corre `playwright install` si es necesario.

Limitaciones
- La instalación automática de `pandoc` solo soportada para Debian/Ubuntu mediante `apt`.
- No se han incluido instaladores para gestores de paquetes distintos a `pip` y `apt`.

Contribuciones
Si quieres mejorar la app (por ejemplo, añadir soporte para `playwright`), envía un parche o solicita cambios.
