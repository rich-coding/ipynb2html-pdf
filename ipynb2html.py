import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import sys
from threading import Thread
import platform
import nbformat


class NotebookConverter:
    """GUI to convert Jupyter notebooks to HTML or PDF.

    Uses nbformat to create a sanitized temporary copy before calling nbconvert.
    """

    def __init__(self, master=None):
        self.window = master or tk.Tk()
        self.window.title("Convertidor de Jupyter Notebook")
        self.window.geometry("480x260")
        self.file_path = None
        self.setup_ui()

    def setup_ui(self):
        main_frame = tk.Frame(self.window, padx=16, pady=12)
        main_frame.pack(expand=True, fill='both')

        self.file_label = tk.Label(main_frame, text="Ningún archivo seleccionado", wraplength=440)
        self.file_label.pack(pady=(0, 12))

        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill='x')

        tk.Button(btn_frame, text="Seleccionar Notebook", command=self.select_file).pack(side='left')
        tk.Label(btn_frame, text="  ").pack(side='left')
        self.install_var = tk.BooleanVar(value=False)
        tk.Checkbutton(btn_frame, text="Instalar dependencias si faltan", variable=self.install_var).pack(side='left')

        tk.Label(main_frame, text="Formato de salida:").pack(anchor='w', pady=(12, 0))
        self.format_var = tk.StringVar(value="html")
        fmt_frame = tk.Frame(main_frame)
        fmt_frame.pack(anchor='w')
        tk.Radiobutton(fmt_frame, text="HTML", variable=self.format_var, value="html").pack(side='left')
        tk.Radiobutton(fmt_frame, text="PDF", variable=self.format_var, value="pdf").pack(side='left')

        self.convert_button = tk.Button(main_frame, text="Convertir", command=self.start_conversion, state='disabled')
        self.convert_button.pack(pady=14)

        self.status_label = tk.Label(main_frame, text="", anchor='w', justify='left', wraplength=440)
        self.status_label.pack(fill='x')

    def log(self, message, error=False):
        print(message)
        self.status_label.config(text=message)
        self.window.update_idletasks()

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Selecciona el archivo .ipynb",
            filetypes=[("Jupyter Notebook", "*.ipynb")]
        )
        if file_path:
            self.file_path = file_path
            self.file_label.config(text=f"Archivo: {os.path.basename(file_path)}")
            self.convert_button.config(state='normal')

    def clean_notebook(self, notebook_path):
        """Read with nbformat, sanitize outputs and metadata, write a cleaned file and return its path."""
        try:
            nb = nbformat.read(notebook_path, as_version=4)
        except Exception as e:
            raise RuntimeError(f"No se pudo leer el notebook con nbformat: {e}")

        # Keep minimal top-level metadata (kernelspec if present)
        nb_meta = {}
        if isinstance(nb.metadata, dict) and 'kernelspec' in nb.metadata:
            nb_meta['kernelspec'] = nb.metadata['kernelspec']
        nb.metadata = nb_meta

        for cell in nb.cells:
            cell.metadata = {}
            outputs = getattr(cell, 'outputs', None)
            if not outputs:
                continue
            new_outputs = []
            for out in outputs:
                if not isinstance(out, dict) and not hasattr(out, 'get'):
                    continue
                ot = out.get('output_type')
                if ot == 'stream':
                    name = out.get('name', 'stdout')
                    text = out.get('text', '')
                    new_outputs.append(nbformat.v4.new_output('stream', name=name, text=text))
                elif ot == 'execute_result':
                    data = out.get('data', {})
                    # skip widget view MIME types to avoid complex widget state
                    if any(k.startswith('application/vnd.jupyter.widget') for k in data.keys()):
                        continue
                    exec_count = out.get('execution_count')
                    new_outputs.append(nbformat.v4.new_output('execute_result', data=data, metadata={}, execution_count=exec_count))
                elif ot == 'display_data':
                    data = out.get('data', {})
                    if any(k.startswith('application/vnd.jupyter.widget') for k in data.keys()):
                        continue
                    new_outputs.append(nbformat.v4.new_output('display_data', data=data, metadata={}))
                elif ot == 'error':
                    ename = out.get('ename', '')
                    evalue = out.get('evalue', '')
                    traceback = out.get('traceback', [])
                    new_outputs.append(nbformat.v4.new_output('error', ename=ename, evalue=evalue, traceback=traceback))
                else:
                    # skip widget or other complex outputs
                    continue

            cell.outputs = new_outputs

        clean_path = notebook_path + '.clean'
        try:
            nbformat.write(nb, clean_path)
        except Exception as e:
            raise RuntimeError(f"No se pudo escribir el notebook limpio: {e}")
        return clean_path

    def run_subprocess(self, cmd, timeout=None):
        try:
            cp = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=timeout)
            return cp
        except subprocess.CalledProcessError as e:
            out = (e.stdout or '') + '\n' + (e.stderr or '')
            raise RuntimeError(f"Command failed: {' '.join(e.cmd)}\n{out}")

    def ensure_pip_package(self, package):
        try:
            __import__(package)
            return True
        except Exception:
            if not self.install_var.get():
                raise RuntimeError(f"Paquete requerido no encontrado: {package}")
            self.log(f"Instalando {package}...")
            try:
                self.run_subprocess([sys.executable, '-m', 'pip', 'install', package])
                return True
            except RuntimeError as e:
                raise RuntimeError(f"Fallo al instalar {package}: {e}")

    def ensure_pandoc_on_linux(self):
        try:
            self.run_subprocess(['pandoc', '--version'])
            return True
        except Exception:
            if not self.install_var.get():
                raise RuntimeError('pandoc no encontrado')
            if platform.system() != 'Linux':
                raise RuntimeError('Pandoc automático sólo soportado en Linux desde este script')
            distro = ''
            try:
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if line.startswith('ID='):
                            distro = line.strip().split('=', 1)[1].strip().strip('"').lower()
                            break
            except Exception:
                distro = ''
            if distro in ('ubuntu', 'debian', 'linuxmint'):
                self.log('Instalando pandoc y texlive-xetex (sudo requerido)...')
                try:
                    self.run_subprocess(['sudo', 'apt-get', 'update'], timeout=120)
                    self.run_subprocess(['sudo', 'apt-get', 'install', '-y', 'pandoc', 'texlive-xetex'], timeout=600)
                    self.run_subprocess(['pandoc', '--version'])
                    return True
                except Exception as e:
                    raise RuntimeError(f'Fallo instalando pandoc: {e}')
            else:
                raise RuntimeError(f'Distribución {distro} no soportada para instalación automática de pandoc')

    def convert(self):
        if not self.file_path:
            messagebox.showwarning('Aviso', 'No hay archivo seleccionado')
            return
        self.convert_button.config(state='disabled')
        try:
            self.log('Preparando elementos...')
            try:
                self.ensure_pip_package('nbconvert')
            except RuntimeError as e:
                messagebox.showerror('Error', str(e))
                return
            output_format = self.format_var.get()
            if output_format == 'pdf':
                try:
                    self.ensure_pip_package('pyppeteer')
                except RuntimeError as e:
                    messagebox.showerror('Error', f'Dependencia PDF faltante: {e}')
                    return
                if platform.system() == 'Linux':
                    try:
                        self.ensure_pandoc_on_linux()
                    except RuntimeError as e:
                        self.log(f'Advertencia pandoc: {e}')
            self.log('Limpiando notebook...')
            clean_path = self.clean_notebook(self.file_path)
            cmd = ['jupyter', 'nbconvert', clean_path, '--to', output_format]
            if output_format == 'html':
                cmd.extend(['--template', 'classic'])
            elif output_format == 'pdf':
                cmd.append('--allow-chromium-download')
            self.log(f'Convirtiendo a {output_format.upper()}...')
            cp = self.run_subprocess(cmd, timeout=600)
            generated = clean_path[:-6] + f'.{output_format}'
            final = os.path.splitext(self.file_path)[0] + f'.{output_format}'
            if os.path.exists(generated):
                os.replace(generated, final)
                self.log(f'Conversión exitosa. Archivo guardado en: {final}')
                messagebox.showinfo('Éxito', f'Archivo generado: {final}')
            else:
                raise RuntimeError('No se encontró el archivo convertido después de nbconvert')
        except Exception as e:
            self.log(f'Error durante la conversión: {e}', error=True)
            messagebox.showerror('Error', f'Error durante la conversión:\n{e}')
        finally:
            try:
                if 'clean_path' in locals() and os.path.exists(clean_path):
                    os.remove(clean_path)
            except Exception:
                pass
            self.convert_button.config(state='normal')

    def start_conversion(self):
        Thread(target=self.convert, daemon=True).start()


def main():
    root = tk.Tk()
    app = NotebookConverter(master=root)
    root.mainloop()


if __name__ == '__main__':
    main()