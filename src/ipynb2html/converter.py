import logging
import platform
import subprocess
import sys
from pathlib import Path

import nbformat

logger = logging.getLogger(__name__)


class NotebookConverter:
    """Core logic to sanitize and convert Jupyter notebooks."""

    def __init__(self, install_missing=False):
        self.install_missing = install_missing

    def clean_notebook(self, notebook_path):
        """Read with nbformat, sanitize outputs and metadata, write a cleaned file."""
        notebook_path = Path(notebook_path)
        logger.info(f"Cleaning notebook: {notebook_path}")
        try:
            nb = nbformat.read(notebook_path, as_version=4)
        except Exception as e:
            raise RuntimeError(f"Could not read notebook with nbformat: {e}") from e

        # Keep minimal top-level metadata
        nb_meta = {}
        if isinstance(nb.metadata, dict) and "kernelspec" in nb.metadata:
            nb_meta["kernelspec"] = nb.metadata["kernelspec"]
        nb.metadata = nb_meta

        for cell in nb.cells:
            cell.metadata = {}
            outputs = getattr(cell, "outputs", None)
            if not outputs:
                continue
            new_outputs = []
            for out in outputs:
                if not isinstance(out, dict) and not hasattr(out, "get"):
                    continue
                ot = out.get("output_type")
                if ot == "stream":
                    name = out.get("name", "stdout")
                    text = out.get("text", "")
                    new_outputs.append(nbformat.v4.new_output("stream", name=name, text=text))
                elif ot == "execute_result":
                    data = out.get("data", {})
                    if any(k.startswith("application/vnd.jupyter.widget") for k in data):
                        continue
                    exec_count = out.get("execution_count")
                    new_outputs.append(
                        nbformat.v4.new_output(
                            "execute_result", data=data, metadata={}, execution_count=exec_count
                        )
                    )
                elif ot == "display_data":
                    data = out.get("data", {})
                    if any(k.startswith("application/vnd.jupyter.widget") for k in data):
                        continue
                    new_outputs.append(
                        nbformat.v4.new_output("display_data", data=data, metadata={})
                    )
                elif ot == "error":
                    ename = out.get("ename", "")
                    evalue = out.get("evalue", "")
                    traceback = out.get("traceback", [])
                    new_outputs.append(
                        nbformat.v4.new_output(
                            "error", ename=ename, evalue=evalue, traceback=traceback
                        )
                    )

            cell.outputs = new_outputs

        clean_path = notebook_path.with_suffix(notebook_path.suffix + ".clean")
        try:
            nbformat.write(nb, str(clean_path))
            logger.debug(f"Cleaned notebook saved to: {clean_path}")
        except Exception as e:
            raise RuntimeError(f"Could not write clean notebook: {e}") from e
        return clean_path

    def run_subprocess(self, cmd, timeout=None):
        try:
            logger.debug(f"Running command: {' '.join(cmd)}")
            return subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=timeout)
        except subprocess.CalledProcessError as e:
            out = (e.stdout or "") + "\n" + (e.stderr or "")
            logger.error(f"Command failed: {' '.join(e.cmd)}\n{out}")
            raise RuntimeError(f"Command failed: {' '.join(e.cmd)}\n{out}") from e

    def ensure_pip_package(self, package):
        try:
            __import__(package)
            return True
        except Exception:
            if not self.install_missing:
                raise RuntimeError(f"Required package not found: {package}") from None
            logger.info(f"Installing package: {package}...")
            try:
                self.run_subprocess([sys.executable, "-m", "pip", "install", package])
                return True
            except RuntimeError as e:
                raise RuntimeError(f"Failed to install {package}: {e}") from e

    def ensure_pandoc_on_linux(self):
        try:
            self.run_subprocess(["pandoc", "--version"])
            return True
        except Exception:
            if not self.install_missing:
                raise RuntimeError("pandoc not found") from None
            if platform.system() != "Linux":
                raise RuntimeError("Automatic pandoc install only supported on Linux") from None

            distro = ""
            try:
                os_release = Path("/etc/os-release")
                if os_release.exists():
                    with os_release.open() as f:
                        for line in f:
                            if line.startswith("ID="):
                                distro = line.strip().split("=", 1)[1].strip().strip('"').lower()
                                break
            except Exception:
                distro = ""

            if distro in ("ubuntu", "debian", "linuxmint"):
                logger.info("Installing pandoc and texlive-xetex (sudo required)...")
                try:
                    self.run_subprocess(["sudo", "apt-get", "update"], timeout=120)
                    self.run_subprocess(
                        ["sudo", "apt-get", "install", "-y", "pandoc", "texlive-xetex"], timeout=600
                    )
                    self.run_subprocess(["pandoc", "--version"])
                    return True
                except Exception as e:
                    raise RuntimeError(f"Failed to install pandoc: {e}") from e
            else:
                raise RuntimeError(
                    f"Distro {distro} not supported for automatic pandoc installation"
                ) from None

    def convert(self, notebook_path, output_format="html"):
        """Main conversion flow."""
        notebook_path = Path(notebook_path)
        logger.info(f"Converting {notebook_path} to {output_format.upper()}")

        # Check dependencies
        self.ensure_pip_package("nbconvert")
        if output_format == "pdf":
            self.ensure_pip_package("pyppeteer")
            if platform.system() == "Linux":
                try:
                    self.ensure_pandoc_on_linux()
                except RuntimeError as e:
                    logger.warning(f"Pandoc warning: {e}")

        clean_path = self.clean_notebook(notebook_path)
        try:
            cmd = ["jupyter", "nbconvert", str(clean_path), "--to", output_format]
            if output_format == "html":
                cmd.extend(["--template", "classic"])
            elif output_format == "pdf":
                cmd.append("--allow-chromium-download")

            self.run_subprocess(cmd, timeout=600)

            generated = clean_path.with_suffix(f".{output_format}")
            # If generated name is notebook.ipynb.clean.html, we need to map to notebook.html
            # nbconvert usually saves to [input_basename].[extension]
            # When input is notebook.ipynb.clean, output is notebook.ipynb.clean.[ext]

            # The original logic was: clean_path[:-6] + f'.{output_format}'
            # clean_path is Path object now.

            final = notebook_path.with_suffix(f".{output_format}")

            if generated.exists():
                generated.replace(final)
                logger.info(f"Successfully converted to {final}")
                return str(final)
            raise RuntimeError("Converted file not found after nbconvert execution")
        finally:
            if clean_path.exists():
                clean_path.unlink()
