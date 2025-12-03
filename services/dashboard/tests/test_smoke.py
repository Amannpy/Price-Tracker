import importlib
import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest


def _install_dashboard_stubs(monkeypatch):
    # Streamlit stub
    st = types.ModuleType("streamlit")

    def noop(*args, **kwargs):
        return None

    class DummyColumn:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def metric(self, *args, **kwargs):
            return None

    def columns(arg):
        if isinstance(arg, int):
            count = arg
        else:
            count = len(arg) or 1
        return [DummyColumn() for _ in range(max(count, 1))]

    st.set_page_config = noop
    st.title = noop
    st.subheader = noop
    st.markdown = noop
    st.info = noop
    st.warning = noop
    st.success = noop
    st.metric = noop
    st.divider = noop
    st.caption = noop
    st.plotly_chart = noop
    st.json = noop
    st.button = lambda *a, **kw: False
    st.selectbox = lambda *a, **kw: None
    st.columns = columns
    st.cache_resource = lambda func: func

    def expander(*args, **kwargs):
        return DummyColumn()

    st.expander = expander

    monkeypatch.setitem(sys.modules, "streamlit", st)

    # Plotly stub
    plotly = types.ModuleType("plotly")
    go = types.ModuleType("plotly.graph_objects")
    px = types.ModuleType("plotly.express")

    class DummyFigure:
        def add_trace(self, *args, **kwargs):
            return None

        def update_layout(self, *args, **kwargs):
            return None

    go.Figure = DummyFigure
    px.line = noop

    plotly.graph_objects = go
    plotly.express = px
    monkeypatch.setitem(sys.modules, "plotly", plotly)
    monkeypatch.setitem(sys.modules, "plotly.graph_objects", go)
    monkeypatch.setitem(sys.modules, "plotly.express", px)

    # Pandas stub
    pandas = types.ModuleType("pandas")
    pandas.DataFrame = MagicMock()
    pandas.to_datetime = lambda x: x
    monkeypatch.setitem(sys.modules, "pandas", pandas)

    # psycopg2 stub
    class DummyCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def execute(self, *args, **kwargs):
            return None

        def fetchall(self):
            return []

        def fetchone(self):
            return None

    class DummyConnection:
        def cursor(self, *args, **kwargs):
            return DummyCursor()

        def commit(self):
            return None

        def close(self):
            return None

    psycopg2 = types.ModuleType("psycopg2")
    psycopg2.connect = lambda *a, **kw: DummyConnection()
    extras = types.ModuleType("psycopg2.extras")
    extras.RealDictCursor = object

    monkeypatch.setitem(sys.modules, "psycopg2", psycopg2)
    monkeypatch.setitem(sys.modules, "psycopg2.extras", extras)


@pytest.fixture(autouse=True)
def dashboard_stubs(monkeypatch):
    _install_dashboard_stubs(monkeypatch)


def test_streamlit_app_imports_with_stubs():
    importlib.import_module("services.dashboard.streamlit_app")


@pytest.mark.parametrize(
    "filename",
    ["1_Products.py", "2_Jobs.py", "3_Alerts.py"],
)
def test_dashboard_pages_import(filename):
    pages_dir = Path(__file__).resolve().parents[1] / "pages"
    path = pages_dir / filename
    spec = importlib.util.spec_from_file_location(
        f"dashboard_page_{filename.replace('.py', '')}", path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module is not None


