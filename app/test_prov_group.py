from models.db import db

conteo_prov = db.contratos.documento_proveedor.count()
suma_prov = db.contratos.valor_contrato.sum()
res_prov = db(db.contratos.documento_proveedor != None).select(
    db.contratos.documento_proveedor,
    db.contratos.proveedor_adjudicado,
    conteo_prov,
    suma_prov,
    groupby=[db.contratos.documento_proveedor, db.contratos.proveedor_adjudicado],
    orderby=~conteo_prov,
    limitby=(0, 10),
)

for r in res_prov:
    print(r)
