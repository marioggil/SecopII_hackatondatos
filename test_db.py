import os
import sys
sys.path.append('app')
from app.models.db import db

conteo = db.contratos.documento_proveedor.count()
suma_valor = db.contratos.valor_contrato.sum()

top_proveedores_db = db(db.contratos.documento_proveedor != None).select(
    db.contratos.documento_proveedor,
    db.contratos.proveedor_adjudicado,
    conteo,
    suma_valor,
    groupby=[db.contratos.documento_proveedor, db.contratos.proveedor_adjudicado],
    orderby=~conteo,
    limitby=(0, 5)
)

for row in top_proveedores_db:
    print(row.contratos.proveedor_adjudicado, row[conteo], row[suma_valor])
