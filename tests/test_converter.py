from pathlib import Path

import nbformat
import pytest

from ipynb2html.converter import NotebookConverter


@pytest.fixture
def sample_notebook(tmp_path):
    nb = nbformat.v4.new_notebook()
    nb.cells.append(
        nbformat.v4.new_code_cell(
            "print('hello')",
            outputs=[nbformat.v4.new_output("stream", name="stdout", text="hello\n")],
        )
    )
    # Add a widget-like output to test sanitation
    nb.cells.append(
        nbformat.v4.new_code_cell(
            "display(w)",
            outputs=[
                nbformat.v4.new_output(
                    "display_data",
                    data={"application/vnd.jupyter.widget-view+json": {}},
                    metadata={},
                )
            ],
        )
    )

    path = tmp_path / "test.ipynb"
    nbformat.write(nb, str(path))
    return str(path)


def test_clean_notebook(sample_notebook):
    converter = NotebookConverter()
    clean_path = Path(converter.clean_notebook(sample_notebook))

    assert clean_path.exists()
    nb = nbformat.read(str(clean_path), as_version=4)

    # Check that widget output was removed
    assert len(nb.cells[1].outputs) == 0
    # Check that metadata was cleaned
    assert nb.cells[0].metadata == {}

    clean_path.unlink()


def test_converter_init():
    converter = NotebookConverter(install_missing=True)
    assert converter.install_missing is True
