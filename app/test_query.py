import sys
sys.path.append('.')
from main3 import generar_nodos_y_enlaces

# Test with departamento filter
nodos, enlaces = generar_nodos_y_enlaces(departamento="Antioquia")
print(f"Antioquia: Nodos {len(nodos)}, Enlaces {len(enlaces)}")

# Test with estado_contrato filter
nodos, enlaces = generar_nodos_y_enlaces(estado_contrato="Terminado")
print(f"Terminado: Nodos {len(nodos)}, Enlaces {len(enlaces)}")

# Test with valor_minimo
nodos, enlaces = generar_nodos_y_enlaces(valor_minimo=50000000)
print(f"Valor minimo 50M: Nodos {len(nodos)}, Enlaces {len(enlaces)}")

# Test with No filters
nodos, enlaces = generar_nodos_y_enlaces()
print(f"No filters: Nodos {len(nodos)}, Enlaces {len(enlaces)}")
