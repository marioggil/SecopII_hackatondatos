from models.db import db

# Let's try to group by year and month using PyDAL
try:
    nit = (
        db(db.contratos.id > 0)
        .select(db.contratos.nit_entidad, limitby=(0, 1))
        .first()
        .nit_entidad
    )
    print(f"Testing for NIT: {nit}")

    # Raw SQL approach if PyDAL expressions fail
    rows = db.executesql(
        "SELECT strftime('%Y-%m', fecha_firma) as mes, count(id) as cantidad, sum(valor_contrato) as total FROM contratos WHERE nit_entidad = ? GROUP BY mes ORDER BY mes",
        placeholders=[nit],
        as_dict=True,
    )
    print("Results:")
    for r in rows:
        print(r)
except Exception as e:
    print("Error:", e)
