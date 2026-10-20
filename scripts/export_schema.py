"""Write db/schema.sql from the SQLAlchemy models. Run: python -m scripts.export_schema"""
from pathlib import Path

from sqlalchemy.schema import CreateIndex, CreateTable

import app.models  # noqa: F401  (registers the tables)
from app.database import Base, engine

lines = ["-- MeeSeva Saathi database schema (generated from app/models.py; SQLite dialect)",
         "-- Regenerate: python -m scripts.export_schema   |   Load sample data: python -m app.seed", ""]
for table in Base.metadata.sorted_tables:
    lines.append(str(CreateTable(table).compile(engine)).strip() + ";\n")
    lines += [str(CreateIndex(ix).compile(engine)).strip() + ";\n" for ix in table.indexes]
Path(__file__).resolve().parent.parent.joinpath("db", "schema.sql").write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote db/schema.sql ({len(Base.metadata.sorted_tables)} tables)")
