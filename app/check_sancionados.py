from models.db import db

# Ver qué columnas tiene la tabla sancionados
campos = db.sancionados.fields
print("Columnas en db.sancionados:", campos)

# Ver un registro de ejemplo
ejemplo = db(db.sancionados.id > 0).select().first()
if ejemplo:
    print("Ejemplo de sanción:", ejemplo)
else:
    print("La tabla de sancionados está vacía.")
