from pydal import DAL, Field
db = DAL('postgres://usuario:password@localhost/base_datos', migrate=False)
db.define_table('contratos',
    Field('documento_proveedor', 'string'),
    Field('proveedor_adjudicado', 'string'),
    Field('valor_contrato', 'decimal(15,2)')
)
conteo_prov = db.contratos.documento_proveedor.count()
suma_prov = db.contratos.valor_contrato.sum()
query = db(db.contratos.documento_proveedor != None)._select(
    db.contratos.documento_proveedor,
    db.contratos.proveedor_adjudicado,
    conteo_prov,
    suma_prov,
    groupby=[db.contratos.documento_proveedor, db.contratos.proveedor_adjudicado],
    orderby=~conteo_prov,
    limitby=(0, 10),
)
print("Query generated for Postgres:")
print(query)
