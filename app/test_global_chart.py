import sys

sys.path.append(".")
from models.db import db

try:
    rows = db.executesql(
        "SELECT strftime('%Y-%m', fecha_firma) as mes, count(id) as cantidad, sum(valor_contrato) as total FROM contratos WHERE fecha_firma IS NOT NULL GROUP BY mes ORDER BY mes",
        as_dict=True,
    )
    print("Total rows:", len(rows))
    print("First 5:", rows[:5])
    print("Last 5:", rows[-5:])
except Exception as e:
    print("Error:", e)
