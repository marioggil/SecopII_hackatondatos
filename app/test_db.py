from models.db import db
estados = db(db.contratos.id > 0).select(db.contratos.estado_contrato, distinct=True)
print("Estados:", [e.estado_contrato for e in estados])

modalidades = db(db.contratos.id > 0).select(db.contratos.modalidad_contratacion, distinct=True)
print("Modalidades:", [m.modalidad_contratacion for m in modalidades])

departamentos = db(db.contratos.id > 0).select(db.contratos.departamento, distinct=True)
print("Departamentos:", [d.departamento for d in departamentos[:10]])
