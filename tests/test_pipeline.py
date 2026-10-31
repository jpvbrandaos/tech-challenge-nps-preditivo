import nbformat

from src.pipeline import NOTEBOOKS, NOTEBOOKS_DIR, run_notebook


def test_pipeline_runs_every_notebook_in_numeric_order():
    assert NOTEBOOKS == sorted(path.name for path in NOTEBOOKS_DIR.glob("*.ipynb"))


def test_run_notebook_saves_outputs_without_run_times(tmp_path):
    path = tmp_path / "exemplo.ipynb"
    notebook = nbformat.v4.new_notebook()
    notebook.cells.append(nbformat.v4.new_code_cell("print(1 + 1)"))
    nbformat.write(notebook, path)

    run_notebook(path)

    cell = nbformat.read(path, as_version=4).cells[0]
    assert cell.execution_count == 1
    assert cell.outputs[0].text == "2\n"
    assert "execution" not in cell.metadata
