import requests

res = requests.get(
    "http://127.0.0.1:8000/html/graph_rel/?estado_contrato=&modalidad_contratacion=&departamento=Antioquia&valor_minimo="
)
print(res.status_code)
print(res.text)
