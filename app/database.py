
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

DB_PATH = DATA_DIR / "checkpoints.sqlite"


def get_checkpointer():

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    return SqliteSaver.from_conn_string(
        str(DB_PATH)
    )
