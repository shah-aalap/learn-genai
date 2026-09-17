import sqlite3
from pathlib import Path
import re
from typing import Self
import polars as pl
from example_lib import ExampleClass

# pl.Config.set_fmt_str_lengths(1000)
# pl.Config.set_tbl_width_chars(1000)


class MainClass(ExampleClass):
    SKIP_WORDS = ["a", "an", "the",
                  "how", "what", "why",
                  "is", "are", "am",
                  "i", "me", "you", "he", "him", "she", "her", "they", "them",
                  "should", "can", "could", "will", "would", "may", "might", "do", "did",
                  "to", "from", "about",
                  "this", "that"]

    def __init__(self, config_path: str | Path) -> None:
        super().__init__(config=config_path)
        self._initialize()
        self._print_db()

    def run(self) -> Self:
        self._query_with_used_words()
        return self

    def _query_with_used_words(self) -> None:
        self._l.info("-" * 80)
        self._l.info("Querying with used words...")
        self._l.info(f"The skip words used are: {", ".join(self.SKIP_WORDS)}")
        query = self._config["query_with_used_words"]
        self._l.info(f"Query: {query}")

        query_cleaned = re.sub(r"[.!?,:;_=+{}()<>\-\[\]]", " ", query.lower())
        words_lc = [word for word in query_cleaned.split()
                    if word not in self.SKIP_WORDS]
        self._l.info(f"Searching for words: {", ".join(words_lc)}")


    def _initialize(self) -> None:
        db_path = Path(__file__).parent / "resources" / f"{self._example_num}.sqlite3"
        if self._config["force_initialize"] and db_path.exists():
            db_path.unlink()

        init_db = not db_path.exists()
        self._sqlite_conn = sqlite3.connect(db_path)
        if init_db:
            self._l.info(f"Initializing SQLite database '{db_path}'")
            cursor = self._sqlite_conn.cursor()
            cursor.execute("""
                CREATE TABLE return_policies(
                    id             INTEGER PRIMARY KEY,
                    category       TEXT NOT NULL,
                    applicability  TEXT,
                    policy         TEXT NOT NULL
                )
            """)
            cursor.executemany(
                "INSERT INTO return_policies (category, applicability, policy) VALUES (?, ?, ?);",
                [("consumable-perishables", "meat, dairy, milk, eggs, bread, fruits, vegetables", "Raise a complaint within 18 hours using the app and send pictures by email"),
                 ("consumable-nonperishables", "packaged groceries", "Raise a complaint within 24 hours using the app and send pictures by email"),
                 ("general-merchandise", "electronics, home furnishings, fashion", "Raise a complaint within 24 hours by talking to our customer support"),
                 ("specific-brands", "SoundStart audio products, CompKey computer accessories", "Raise a complaint within 48 hours by using the app and send pictures by email"),
                 ("severe-issues", "expired products, fungus, insects, foreign objects", "No time restriction"),
                 ("clothing-footwear", "select cities of Bengaluru and Chennai only", "Raise a complaint within 24 hours using the app, with 1 day fast return and refund or exchange for size and fit issues")]
            )
            self._sqlite_conn.commit()

    def _print_db(self) -> None:
        cursor = self._sqlite_conn.cursor()
        cursor.execute("SELECT * FROM return_policies")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pl.DataFrame(rows, schema=columns, orient="row")
        with pl.Config(fmt_str_lengths=200,
                       tbl_hide_dataframe_shape=True,
                       tbl_hide_column_data_types=True):
            self._l.info(f"Table 'return_policies' has following rows:\n{df}")

        cursor.execute("SELECT * FROM return_policies WHERE category = ?", (self._config["select_category"],))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pl.DataFrame(rows, schema=columns, orient="row")
        with pl.Config(fmt_str_lengths=200,
                       tbl_hide_dataframe_shape=True,
                       tbl_hide_column_data_types=True):
            self._l.info(f"Category '{self._config["select_category"]}' was selected from 'return_policies', "
                         f" You can change this key in configuration file '{self._example_dir_path}', key '{self._example_num}.select_category'\n{df}")
