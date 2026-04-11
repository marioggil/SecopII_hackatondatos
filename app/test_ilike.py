import sys

sys.path.append(".")
from main3 import generar_nodos_y_enlaces
from models.db import db

# Let's see what happens with ilike
q = db.contratos.estado_contrato.ilike("Terminado")
print(db(q).count())
