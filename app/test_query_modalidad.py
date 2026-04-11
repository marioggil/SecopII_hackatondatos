import sys

sys.path.append(".")
from main3 import generar_nodos_y_enlaces

# Test with modalidad_contratacion filter
nodos, enlaces = generar_nodos_y_enlaces(modalidad_contratacion="Contratación directa")
print(f"Contratacion directa: Nodos {len(nodos)}, Enlaces {len(enlaces)}")

nodos, enlaces = generar_nodos_y_enlaces(modalidad_contratacion="Licitación pública")
print(f"Licitacion publica: Nodos {len(nodos)}, Enlaces {len(enlaces)}")
