import requests

res = requests.get(
    "http://127.0.0.1:8000/html/graph_rel/?estado_contrato=&modalidad_contratacion=Licitación+pública&departamento=Antioquia&valor_minimo="
)
print(res.status_code)
# It should be 200 now instead of 422
