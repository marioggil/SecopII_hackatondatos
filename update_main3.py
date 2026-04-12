import re

with open('app/main3.py', 'r') as f:
    content = f.read()

# Add parameters to generar_nodos_y_enlaces
old_def = """def generar_nodos_y_enlaces(
    nit_entidad=None,
    documento_proveedor=None,
    departamento=None,
    fecha_inicio=None,
    fecha_fin=None,
    valor_minimo=None,
    valor_maximo=None,
    tamano_min=5,
    tamano_max=50,
    limit_entidades=30,
    limit_proveedores=70,
):"""

new_def = """def generar_nodos_y_enlaces(
    nit_entidad=None,
    documento_proveedor=None,
    departamento=None,
    fecha_inicio=None,
    fecha_fin=None,
    valor_minimo=None,
    valor_maximo=None,
    estado_contrato=None,
    modalidad_contratacion=None,
    tamano_min=5,
    tamano_max=50,
    limit_entidades=30,
    limit_proveedores=70,
):"""
content = content.replace(old_def, new_def)

# Add filter logic inside generar_nodos_y_enlaces
old_logic = """    if valor_maximo:
        query_base &= db.contratos.valor_contrato <= valor_maximo"""

new_logic = """    if valor_maximo:
        query_base &= db.contratos.valor_contrato <= valor_maximo

    if estado_contrato:
        query_base &= db.contratos.estado_contrato == estado_contrato

    if modalidad_contratacion:
        query_base &= db.contratos.modalidad_contratacion == modalidad_contratacion"""
content = content.replace(old_logic, new_logic)

# Update the graph endpoint
old_graph_endpoint = """@app.get("/html/graph_rel/", response_class=HTMLResponse)
async def graph(request: Request):

    nodos, enlaces = generar_nodos_y_enlaces(
        tamano_min=3, tamano_max=120, limit_entidades=40, limit_proveedores=100
    )"""

new_graph_endpoint = """@app.get("/html/graph_rel/", response_class=HTMLResponse)
async def graph(
    request: Request,
    departamento: Optional[str] = Query(None),
    estado_contrato: Optional[str] = Query(None),
    modalidad_contratacion: Optional[str] = Query(None),
    valor_minimo: Optional[float] = Query(None)
):
    nodos, enlaces = generar_nodos_y_enlaces(
        departamento=departamento if departamento else None,
        estado_contrato=estado_contrato if estado_contrato else None,
        modalidad_contratacion=modalidad_contratacion if modalidad_contratacion else None,
        valor_minimo=valor_minimo if valor_minimo else None,
        tamano_min=3, tamano_max=120, limit_entidades=40, limit_proveedores=100
    )"""

content = content.replace(old_graph_endpoint, new_graph_endpoint)

with open('app/main3.py', 'w') as f:
    f.write(content)
print("Updated main3.py")
