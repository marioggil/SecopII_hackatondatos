from pydal import DAL, Field

import os
import json
import pandas as pd
import time
from models.db import db
from databaseUpgrade import verificar_registro_diferente,guardar_sancionado_siri,guardar_sancionado,parsear_fecha,limpiar_valor,normalizar_documento,extraer_datos_secop,guardar_amonestado_secop
from fastapi import FastAPI, Query, File, UploadFile, Form, HTTPException
from pydantic import BaseModel, field_validator, computed_field, Field as PydanticField
from typing import Dict, Annotated, Literal, Union, Optional, List
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
import time
import os
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
import json
import random
import requests
import uuid
import numpy as np
from datetime import date, datetime
from fastapi import FastAPI, HTTPException
from sodapy import Socrata

pwd = os.getcwd()
app = FastAPI()


def extractConfig(
    nameModel="SystemData",
    relPath=os.path.join(pwd, "private/experiment_config.json"),
    dataOut="keyantrophics",
):
    configPath = os.path.join(os.getcwd(), relPath)
    with open(configPath, "r", encoding="utf-8") as file:
        config = json.load(file)[nameModel]
    Output = config[dataOut]
    return Output


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Configurar templates (para archivos HTML externos)
templates = Jinja2Templates(directory="templates")

# Configurar archivos estáticos (CSS, JS, imágenes)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    context = {"request": request}

    return templates.TemplateResponse("index.html", context)


@app.get("/html/index_info", response_class=HTMLResponse)
async def index_tot(request: Request):
    context = {"request": request}

    return templates.TemplateResponse("index_tot.html", context)


@app.get("/estadisticas", response_class=HTMLResponse)
async def estadisticas(request: Request):
    # Contamos registros en las tablas principales
    count_entidades = db(db.entidades.id > 0).count()
    count_proveedores = db(db.proveedoresypersonas.id > 0).count()
    count_sancionados = db(db.sancionados.id > 0).count()
    count_contratos = db(db.contratos.id > 0).count()

    context = {
        "request": request,
        "stats": {
            "entidades": count_entidades,
            "proveedores": count_proveedores,
            "sancionados": count_sancionados,
            "contratos": count_contratos,
        },
    }
    return templates.TemplateResponse("estadisticas.html", context)


@app.get("/html/header", response_class=HTMLResponse)
async def header(request: Request):
    context = {"request": request}

    return templates.TemplateResponse("header.html", context)


@app.get("/html/section_cards", response_class=HTMLResponse)
async def section_cards(request: Request):
    # Top 10 Entidades con más contratos
    conteo_ent = db.contratos.nit_entidad.count()
    suma_ent = db.contratos.valor_contrato.sum()
    try:
        res_ent = db(db.contratos.nit_entidad != None).select(
            db.contratos.nit_entidad,
            db.contratos.nombre_entidad,
            conteo_ent,
            suma_ent,
            groupby=[db.contratos.nit_entidad, db.contratos.nombre_entidad],
            orderby=~conteo_ent,
            limitby=(0, 10),
        )
    except Exception as e:
        import traceback

        print("ERROR in section_cards_entidades:", e)
        traceback.print_exc()
        res_ent = []

    top_entidades = []
    for r in res_ent:
        nombre = r.contratos.nombre_entidad or "Desconocido"
        if len(nombre) > 50:
            nombre = nombre[:47] + "..."

        top_entidades.append(
            {
                "nit": r.contratos.nit_entidad,
                "nombre": nombre,
                "contratos": r[conteo_ent],
                "valor": float(r[suma_ent] or 0),
            }
        )

    context = {"request": request, "top_entidades": top_entidades}

    return templates.TemplateResponse("section_cards.html", context)


@app.get("/html/global_chart", response_class=HTMLResponse)
async def global_chart(request: Request):
    is_postgres = db._uri.startswith("postgres")
    if is_postgres:
        chart_query = """
            SELECT TO_CHAR(fecha_firma, 'YYYY-MM') as mes, count(id) as cantidad, sum(valor_contrato) as total 
            FROM contratos 
            WHERE fecha_firma IS NOT NULL
            GROUP BY TO_CHAR(fecha_firma, 'YYYY-MM') 
            ORDER BY mes
        """
    else:
        chart_query = """
            SELECT strftime('%Y-%m', fecha_firma) as mes, count(id) as cantidad, sum(valor_contrato) as total 
            FROM contratos 
            WHERE fecha_firma IS NOT NULL
            GROUP BY mes 
            ORDER BY mes
        """
    chart_data = "[]"
    try:
        chart_data_raw = db.executesql(chart_query, as_dict=True)
        chart_data = json.dumps(chart_data_raw)
    except Exception as e:
        print("Error global chart:", e)

    context = {"request": request, "chart_data": chart_data}
    return templates.TemplateResponse("global_chart.html", context)


@app.get("/html/section_cards_proveedores", response_class=HTMLResponse)
async def section_cards_proveedores(request: Request):
    # Top 10 Proveedores con más contratos
    conteo_prov = db.contratos.documento_proveedor.count()
    suma_prov = db.contratos.valor_contrato.sum()
    try:
        res_prov = db(db.contratos.documento_proveedor != None).select(
            db.contratos.documento_proveedor,
            db.contratos.proveedor_adjudicado,
            conteo_prov,
            suma_prov,
            groupby=[
                db.contratos.documento_proveedor,
                db.contratos.proveedor_adjudicado,
            ],
            orderby=~conteo_prov,
            limitby=(0, 10),
        )
    except Exception as e:
        import traceback

        print("ERROR in section_cards_proveedores:", e)
        traceback.print_exc()
        res_prov = []

    top_proveedores = []
    for r in res_prov:
        nombre = r.contratos.proveedor_adjudicado or "Desconocido"
        if len(nombre) > 50:
            nombre = nombre[:47] + "..."

        top_proveedores.append(
            {
                "documento": r.contratos.documento_proveedor,
                "nombre": nombre,
                "contratos": r[conteo_prov],
                "valor": float(r[suma_prov] or 0),
            }
        )

    context = {"request": request, "top_proveedores": top_proveedores}

    return templates.TemplateResponse("section_cards_prov.html", context)


@app.get("/html/section_cards_sancionados", response_class=HTMLResponse)
async def section_cards_sancionados(request: Request):
    # Buscar todos los documentos que tienen alguna sanción
    docs_sancionados = [
        r.documento
        for r in db(db.sancionados.id > 0).select(
            db.sancionados.documento, distinct=True
        )
        if r.documento
    ]

    if not docs_sancionados:
        return HTMLResponse("")  # Si no hay sancionados, no mostramos nada

    conteo_prov = db.contratos.documento_proveedor.count()
    suma_prov = db.contratos.valor_contrato.sum()

    # Filtrar los contratos donde el proveedor esté en la lista de sancionados
    res_prov = db(db.contratos.documento_proveedor.belongs(docs_sancionados)).select(
        db.contratos.documento_proveedor,
        db.contratos.proveedor_adjudicado,
        conteo_prov,
        suma_prov,
        groupby=[db.contratos.documento_proveedor, db.contratos.proveedor_adjudicado],
    )

    if not res_prov:
        return HTMLResponse("")

    res_list = list(res_prov)

    # Lógica solicitada: máximo 10, si hay más, aleatorios.
    if len(res_list) > 10:
        res_list = random.sample(res_list, 10)
    else:
        # Si son 10 o menos, los ordenamos por cantidad de contratos
        res_list.sort(key=lambda x: x[conteo_prov], reverse=True)

    top_sancionados = []
    for r in res_list:
        nombre = r.contratos.proveedor_adjudicado or "Desconocido"
        if len(nombre) > 50:
            nombre = nombre[:47] + "..."

        top_sancionados.append(
            {
                "documento": r.contratos.documento_proveedor,
                "nombre": nombre,
                "contratos": r[conteo_prov],
                "valor": float(r[suma_prov] or 0),
            }
        )

    context = {"request": request, "top_sancionados": top_sancionados}

    return templates.TemplateResponse("section_cards_sancionados.html", context)


@app.get("/html/footer", response_class=HTMLResponse)
async def footer(request: Request):
    context = {"request": request}

    return templates.TemplateResponse("footer.html", context)


def generar_nodos_y_enlaces(
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
):
    """
    Genera dos listas:
    1. nodos: Lista de diccionarios con entidades y proveedores
    2. enlaces: Lista de diccionarios con las relaciones entre entidades y proveedores

    Parámetros:
    - nit_entidad: Filtrar por un NIT de entidad específico
    - documento_proveedor: Filtrar por documento de proveedor específico
    - departamento: Filtrar por departamento
    - fecha_inicio: Filtrar contratos desde esta fecha
    - fecha_fin: Filtrar contratos hasta esta fecha
    - valor_minimo: Valor mínimo del contrato
    - valor_maximo: Valor máximo del contrato
    - tamano_min: Tamaño mínimo de los nodos (default: 5)
    - tamano_max: Tamaño máximo de los nodos (default: 50)
    - limit_entidades: Límite de top entidades a graficar
    - limit_proveedores: Límite de top proveedores a graficar
    """

    nodos = []
    enlaces = []
    enlaces_dict = {}

    # ============= CONSTRUIR QUERY BASE =============
    query_base = db.contratos.id > 0

    if nit_entidad:
        query_base &= db.contratos.nit_entidad == nit_entidad

    if documento_proveedor:
        query_base &= db.contratos.documento_proveedor == documento_proveedor

    if departamento:
        query_base &= db.contratos.departamento == departamento

    if fecha_inicio:
        query_base &= db.contratos.fecha_inicio >= fecha_inicio

    if fecha_fin:
        query_base &= db.contratos.fecha_fin <= fecha_fin

    if valor_minimo:
        query_base &= db.contratos.valor_contrato >= valor_minimo

    if valor_maximo:
        query_base &= db.contratos.valor_contrato <= valor_maximo

    if estado_contrato:
        query_base &= db.contratos.estado_contrato.ilike(estado_contrato)

    if modalidad_contratacion:
        query_base &= db.contratos.modalidad_contratacion.ilike(modalidad_contratacion)

    # ============= PROCESAR ENTIDADES =============
    resultado = db.contratos.nit_entidad.count()
    suma_valor = db.contratos.valor_contrato.sum()

    query_entidades = query_base & (db.contratos.nit_entidad != None)

    conteos = db(query_entidades).select(
        db.contratos.nit_entidad,
        resultado,
        suma_valor,
        groupby=db.contratos.nit_entidad,
        having=resultado > 0,
        orderby=~resultado,
        limitby=(0, limit_entidades),
    )

    # Lista temporal para almacenar nodos de entidades
    nodos_entidades = []

    for row in conteos:
        nitActual = row.contratos.nit_entidad
        valor_total = float(row[suma_valor] or 0)

        # Buscar datos de la entidad
        dataEntidad = db(db.entidades.nit_entidad == nitActual).select().last()

        try:
            nodo_entidad = {
                "id": nitActual,
                "name": dataEntidad.nombre_entidad,
                "departamento": dataEntidad.departamento,
                "tipo": "entidad",
                "url": "",
                "color": "#6da2c4",
                "size": 0,  # Se calculará después
                "cantidad_contratos": row[resultado],
                "valor_contrato": valor_total,
            }
            nodos_entidades.append(nodo_entidad)
        except:
            # Si no existe en tabla entidades, usar datos del contrato
            dataContrato = db(db.contratos.nit_entidad == nitActual).select().first()
            if dataContrato:
                nodo_entidad = {
                    "id": nitActual,
                    "name": dataContrato.nombre_entidad or "Entidad Desconocida",
                    "departamento": dataContrato.departamento or "",
                    "tipo": "entidad",
                    "url": "",
                    "color": "#6da2c4",
                    "size": 0,  # Se calculará después
                    "cantidad_contratos": row[resultado],
                    "valor_contrato": valor_total,
                }
                nodos_entidades.append(nodo_entidad)

    # ============= PROCESAR PROVEEDORES =============
    resultadoProv = db.contratos.documento_proveedor.count()
    suma_valor_prov = db.contratos.valor_contrato.sum()

    query_proveedores = query_base & (db.contratos.documento_proveedor != None)

    conteosProv = db(query_proveedores).select(
        db.contratos.documento_proveedor,
        resultadoProv,
        suma_valor_prov,
        groupby=db.contratos.documento_proveedor,
        having=resultadoProv > 0,
        orderby=~resultadoProv,
        limitby=(0, limit_proveedores),
    )

    # Lista temporal para almacenar nodos de proveedores
    nodos_proveedores = []

    for row in conteosProv:
        docActual = row.contratos.documento_proveedor
        valor_total = float(row[suma_valor_prov] or 0)

        # Buscar datos del proveedor
        dataProv = db(db.proveedoresypersonas.documento == docActual).select().last()

        try:
            nodo_proveedor = {
                "id": docActual,
                "name": dataProv.nombre,
                "es_pyme": dataProv.es_pyme or "No",
                "es_grupo": dataProv.es_grupo or "No",
                "tipo": "proveedor",
                "url": "",
                "color": "#1dc96a",
                "size": 0,  # Se calculará después
                "cantidad_contratos": row[resultadoProv],
                "valor_contrato": valor_total,
            }
            nodos_proveedores.append(nodo_proveedor)
        except:
            # Si no existe en tabla proveedores, usar datos del contrato
            dataContrato = (
                db(db.contratos.documento_proveedor == docActual).select().first()
            )
            if dataContrato:
                nodo_proveedor = {
                    "id": docActual,
                    "name": dataContrato.proveedor_adjudicado
                    or "Proveedor Desconocido",
                    "es_pyme": dataContrato.es_pyme or "No",
                    "es_grupo": dataContrato.es_grupo or "No",
                    "tipo": "proveedor",
                    "url": "",
                    "color": "#1dc96a",
                    "size": 0,  # Se calculará después
                    "cantidad_contratos": row[resultadoProv],
                    "valor_contrato": valor_total,
                }
                nodos_proveedores.append(nodo_proveedor)

    # ============= NORMALIZAR TAMAÑOS =============
    # Combinar todos los nodos para calcular valores min y max globales
    todos_nodos = nodos_entidades + nodos_proveedores

    if len(todos_nodos) > 0:
        # Obtener valores mínimo y máximo de contratos
        valores = [
            nodo["valor_contrato"] for nodo in todos_nodos if nodo["valor_contrato"] > 0
        ]

        if len(valores) > 0:
            valor_min_global = min(valores)
            valor_max_global = max(valores)

            # Evitar división por cero si todos los valores son iguales
            rango_valores = valor_max_global - valor_min_global

            if rango_valores > 0:
                # Normalización lineal: size = tamano_min + (valor - min) / (max - min) * (tamano_max - tamano_min)
                for nodo in todos_nodos:
                    if nodo["valor_contrato"] > 0:
                        valor_normalizado = (
                            nodo["valor_contrato"] - valor_min_global
                        ) / rango_valores
                        nodo["size"] = tamano_min + valor_normalizado * (
                            tamano_max - tamano_min
                        )
                    else:
                        nodo["size"] = tamano_min
            else:
                # Si todos los valores son iguales, usar tamaño promedio
                tamano_promedio = (tamano_min + tamano_max) / 2
                for nodo in todos_nodos:
                    nodo["size"] = tamano_promedio
        else:
            # Si no hay valores, usar tamaño mínimo
            for nodo in todos_nodos:
                nodo["size"] = tamano_min

    # Agregar nodos normalizados a la lista final
    nodos = todos_nodos

    # ============= GENERAR ENLACES (RELACIONES) =============
    query_enlaces = (
        query_base
        & (db.contratos.nit_entidad != None)
        & (db.contratos.documento_proveedor != None)
    )

    contratos = db(query_enlaces).select(
        db.contratos.nit_entidad,
        db.contratos.documento_proveedor,
        db.contratos.valor_contrato,
    )

    # Agrupar enlaces y sumar valores
    for contrato in contratos:
        source = contrato.nit_entidad
        target = contrato.documento_proveedor
        identificador = f"{source}_{target}"

        if identificador not in enlaces_dict:
            enlaces_dict[identificador] = {
                "source": source,
                "target": target,
                "identificador": identificador,
                "color": "#ff0000",
                "cantidad_contratos": 0,
                "valor_contrato": 0,
            }

        enlaces_dict[identificador]["cantidad_contratos"] += 1
        enlaces_dict[identificador]["valor_contrato"] += float(
            contrato.valor_contrato or 0
        )

    # Filtrar enlaces donde ambos nodos existen en nuestra lista acotada de nodos
    ids_validos = {nodo["id"] for nodo in todos_nodos}

    # Convertir diccionario de enlaces a lista filtrada
    enlaces = [
        enlace
        for enlace in enlaces_dict.values()
        if enlace["source"] in ids_validos and enlace["target"] in ids_validos
    ]

    return nodos, enlaces


def generar_html_grafo(
    nodos, enlaces, titulo="Grafo de Contratos", nombre_archivo="grafo_contratos.html"
):
    """
    Genera un archivo HTML con visualización de grafo D3.js a partir de nodos y enlaces

    Parámetros:
    - nodos: Lista de diccionarios con nodos (entidades y proveedores)
    - enlaces: Lista de diccionarios con enlaces entre nodos
    - titulo: Título del grafo
    - nombre_archivo: Nombre del archivo HTML a generar
    """

    # Convertir nodos a formato JavaScript
    nodos_js = "[\n"
    for i, nodo in enumerate(nodos):
        nname = nodo["name"].replace("'", "")
        coma = "," if i < len(nodos) - 1 else ""
        nodos_js += f"    {{ id: '{nodo['id']}', name: '{nname}', "

        # Agregar campos según el tipo de nodo
        if nodo["tipo"] == "entidad":
            nodos_js += f"dep: '{nodo.get('departamento', '')}', "
        else:  # proveedor
            nodos_js += f"es_pyme: '{nodo.get('es_pyme', 'No')}', es_grupo: '{nodo.get('es_grupo', 'No')}', "

        nodos_js += f"url: '{nodo.get('url', '')}', color: '{nodo['color']}', "
        nodos_js += f"cantidad_contratos: {nodo['cantidad_contratos']}, size: {nodo['size']}, valor: {nodo['valor_contrato']}, tipo: '{nodo['tipo']}'}}{coma}\n"
    nodos_js += "]"

    # Convertir enlaces a formato JavaScript
    enlaces_js = "[\n"
    for i, enlace in enumerate(enlaces):
        coma = "," if i < len(enlaces) - 1 else ""
        enlaces_js += (
            f"    {{ source: '{enlace['source']}', target: '{enlace['target']}', "
        )
        enlaces_js += (
            f"identificador: '{enlace['identificador']}', color: '{enlace['color']}', "
        )
        enlaces_js += f"cantidad_contratos: {enlace['cantidad_contratos']}, "
        enlaces_js += f"valor_contrato: {enlace['valor_contrato']}}}{coma}\n"
    enlaces_js += "]"

    # Generar items de leyenda para entidades
    leyenda_entidades = ""
    entidades_unicas = {}
    for nodo in nodos:
        if nodo["tipo"] == "entidad":
            dep = nodo.get("departamento", "Sin departamento")
            if dep not in entidades_unicas:
                entidades_unicas[dep] = nodo["color"]

    for dep, color in list(entidades_unicas.items())[
        :10
    ]:  # Limitar a 10 para no saturar
        leyenda_entidades += f"""
            <div class="legend-item">
                <div class="legend-color" style="background: {color};"></div>
                <span>{dep}</span>
            </div>"""

    # Template HTML
    html_content = f"""

    
    <div class="infodiv" style="flex: 1; display: flex; flex-direction: column; width: 100%; height: 100%;">
        <div id="title" class="title" style="min-height: 50px; justify-content: center; background: rgba(26, 35, 126, 0.9);">
            <p style="margin: 0px">{titulo}</p>
        </div>
        <div id="tooltip" class="tooltip"></div>
        <svg id="graph" style="flex: 1; width: 100%; height: 100%;"></svg>
        


    <script>
    (() => {{
        const nodes = {nodos_js};
        
        const links = {enlaces_js};

        function toggleLegend() {{
            const legend = document.getElementById('legend');
            legend.classList.toggle('hidden');
        }}

        function formatNumber(num) {{
            return new Intl.NumberFormat('es-CO', {{ 
                style: 'currency', 
                currency: 'COP',
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            }}).format(num);
        }}

        // Configuración del SVG
        const container = document.getElementById('graph-container') || document.body;
        const width = container.clientWidth || (window.innerWidth - 300);
        const height = container.clientHeight || (window.innerHeight - 80);

        const svg = d3.select('#graph')
            .attr('width', width)
            .attr('height', height);

        const tooltip = d3.select('#tooltip');

        // Contenedor para zoom
        const g = svg.append('g');

        // Zoom
        const zoom = d3.zoom()
            .scaleExtent([0.1, 10])
            .on('zoom', (event) => {{
                g.attr('transform', event.transform);
            }});

        svg.call(zoom);
        svg.call(zoom.transform, d3.zoomIdentity
            .translate(width / 2, height / 2)
            .scale(0.5)
            .translate(-width / 2, -height / 2)
        );

        // Simulación de fuerzas
        const simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(links).id(d => d.id).distance(50))
            .force('charge', d3.forceManyBody().strength(-2))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(d => d.size +5 ));

        // Crear enlaces
        const link = g.append('g')
            .selectAll('line')
            .data(links)
            .join('line')
            .attr('class', 'link')
            .attr('stroke', d => d.color)
            .attr('stroke-width', d => Math.max(2, Math.min(10, d.cantidad_contratos / 2)))
            .on('mouseover', (event, d) => {{
                tooltip
                    .style('opacity', 1)
                    .html(`
                        <strong>Relación Contractual</strong><br>
                        Entidad: ${{nodes.find(n => n.id === d.source.id).name}}<br>
                        Proveedor: ${{nodes.find(n => n.id === d.target.id).name}}<br>
                        Contratos: ${{d.cantidad_contratos}}<br>
                        Valor total: ${{formatNumber(d.valor_contrato)}}
                    `)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 10) + 'px');
                
                node
                    .filter(n => n.id === d.source.id || n.id === d.target.id)
                    .attr('stroke', '#2cf105')
                    .attr('stroke-width', 3);
            }})
            .on('mouseout', () => {{
                tooltip.style('opacity', 0);
                node
                    .attr('stroke', '#fff')
                    .attr('stroke-width', 2);
            }});

        // Crear nodos
        const node = g.append('g')
            .selectAll('circle')
            .data(nodes)
            .join('circle')
            .attr('class', 'node')
            .attr('r', d => Math.max(5, Math.min(50, d.size)))
            .attr('fill', d => d.color)
            .attr('stroke', '#fff')
            .attr('stroke-width', 2)
            .style('cursor', 'pointer')
            .call(drag(simulation))
            .on('click', (event, d) => {{
                if (d.tipo === 'entidad') {{
                    window.open('/entidad/' + d.id, '_blank');
                }} else {{
                    window.open('/proveedor/' + d.id, '_blank');
                }}
            }})
            .on('mouseover', (event, d) => {{
                let tooltipContent = `<strong>${{d.name}}</strong><br>`;
                tooltipContent += `Tipo: ${{d.tipo === 'entidad' ? 'Entidad' : 'Proveedor'}}<br>`;
                tooltipContent += `ID: ${{d.id}}<br>`;
                
                if (d.tipo === 'entidad') {{
                    tooltipContent += `Departamento: ${{d.dep || 'N/A'}}<br>`;
                }} else {{
                    tooltipContent += `PyME: ${{d.es_pyme}}<br>`;
                    tooltipContent += `Grupo: ${{d.es_grupo}}<br>`;
                }}
                
                tooltipContent += `Contratos: ${{d.cantidad_contratos}}<br>`;
                tooltipContent += `Valor total: ${{formatNumber(d.valor)}}`;
                
                tooltip
                    .style('opacity', 1)
                    .html(tooltipContent)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 10) + 'px');
            }})
            .on('mouseout', () => {{
                tooltip.style('opacity', 0);
            }});

        // Etiquetas de nodos
        const label = g.append('g')
            .selectAll('text')
            .data(nodes)
            .join('text')
            .attr('class', 'node-label')
            .attr('text-anchor', 'middle')
            .attr('dy', d => -(Math.max(5, Math.min(50, d.size)) + 5));
            //.text(d => d.name.length > 30 ? d.name.substring(0, 30) + '...' : d.name);

        // Actualizar posiciones en cada tick
        simulation.on('tick', () => {{
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            node
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);

            label
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        }});

        // Función de arrastre
        function drag(simulation) {{
            function dragstarted(event) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                event.subject.fx = event.subject.x;
                event.subject.fy = event.subject.y;
            }}

            function dragged(event) {{
                event.subject.fx = event.x;
                event.subject.fy = event.y;
            }}

            function dragended(event) {{
                if (!event.active) simulation.alphaTarget(0);
                event.subject.fx = null;
                event.subject.fy = null;
            }}

            return d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended);
        }}

        // Ajustar tamaño al cambiar ventana
        window.addEventListener('resize', () => {{
            const c = document.getElementById('graph-container') || document.body;
            const newWidth = c.clientWidth || (window.innerWidth - 300);
            const newHeight = c.clientHeight || (window.innerHeight - 80);
            svg.attr('width', newWidth).attr('height', newHeight);
            simulation.force('center', d3.forceCenter(newWidth / 2, newHeight / 2));
            simulation.alpha(0.3).restart();
        }});
    }})();
    </script>
"""

    return html_content


# ============= EJEMPLO DE USO COMPLETO =============


@app.get("/html/graph_rel/", response_class=HTMLResponse)
async def graph(
    request: Request,
    estado_contrato: Optional[str] = Query(None),
    modalidad_contratacion: Optional[str] = Query(None),
    departamento: Optional[str] = Query(None),
    valor_minimo: Optional[str] = Query(None),
    valor_maximo: Optional[str] = Query(None),
):

    v_minimo = float(valor_minimo) if valor_minimo and valor_minimo.strip() else None
    v_maximo = float(valor_maximo) if valor_maximo and valor_maximo.strip() else None

    nodos, enlaces = generar_nodos_y_enlaces(
        estado_contrato=estado_contrato if estado_contrato else None,
        modalidad_contratacion=modalidad_contratacion
        if modalidad_contratacion
        else None,
        departamento=departamento if departamento else None,
        valor_minimo=v_minimo,
        valor_maximo=v_maximo,
        tamano_min=3,
        tamano_max=120,
        limit_entidades=40,
        limit_proveedores=100,
    )
    html_content = generar_html_grafo(
        nodos=nodos,
        enlaces=enlaces,
        titulo="Top Relaciones Contractuales",
        nombre_archivo="grafo_normalizado.html",
    )

    return HTMLResponse(
        content=html_content
    )  # templates.TemplateResponse("graph_ente_prove.html", context)


@app.get("/html/leyenda.html", response_class=HTMLResponse)
async def leyend(request: Request):

    html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grafo de Contratos</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: #f5f5f5;
            align-items: center;
            justify-content: center;
        }
                .legend {
            position: fixed;
            top: 80px;
            right: 20px;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            max-width: 300px;
            max-height: 80vh;
            overflow-y: auto;
            z-index: 999;
            transition: transform 0.3s ease;
        }
        .legend.hidden {
            transform: translateX(350px);
        }
        .legend h3 {
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 16px;
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 8px;
        }
        .legend-section {
            margin-bottom: 20px;
        }
        .legend-section h4 {
            margin: 0 0 10px 0;
            font-size: 14px;
            color: #666;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
            font-size: 12px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 10px;
            border: 2px solid #fff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }
        .legend-line {
            width: 30px;
            height: 3px;
            margin-right: 10px;
        }
        </style>
    </head>
<body>
    <div id="legend" class="legend">
            <h3>Leyenda del Grafo</h3>

            <div class="legend-section">
                <h4>Nodos - Entidades</h4>
                <div class="legend-item">
                    <div class="legend-color" style="background: #6da2c4;"></div>
                    <span>Entidades (azul)</span>
                </div>
            </div>

            <div class="legend-section">
                <h4>Nodos - Proveedores</h4>
                <div class="legend-item">
                    <div class="legend-color" style="background: #1dc96a;"></div>
                    <span>Proveedores (verde)</span>
                </div>
            </div>

            <div class="legend-section">
                <h4>Enlaces (Contratos)</h4>
                <div class="legend-item">
                    <div class="legend-line" style="background: #ff0000;"></div>
                    <span>Relación contractual</span>
                </div>
            </div>

            <div class="legend-section">
                <h4>Tamaño de nodos</h4>
                <div class="legend-item">
                    <span>Representa el número de contratos</span>
                </div>
            </div>

            <div class="legend-section">
                <h4>Estadísticas</h4>
                <div class="legend-item">
                    <span>Total nodos: {len(nodos)}</span>
                </div>
                <div class="legend-item">
                    <span>Total enlaces: {len(enlaces)}</span>
                </div>
                <div class="legend-item">
                    <span>Entidades: {len([n for n in nodos if n['tipo'] == 'entidad'])}</span>
                </div>
                <div class="legend-item">
                    <span>Proveedores: {len([n for n in nodos if n['tipo'] == 'proveedor'])}</span>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.get("/entidad/{nit}", response_class=HTMLResponse)
async def entidad_detalle(
    request: Request,
    nit: str,
    page: int = 1,
    search: Optional[str] = Query(None),
    sort_by: str = Query("fecha"),
):
    entidad = db(db.entidades.nit_entidad == nit).select().first()
    if not entidad:
        raise HTTPException(status_code=404, detail="Entidad no encontrada")

    query = db.contratos.nit_entidad == nit

    if search:
        query &= db.contratos.id_contrato.ilike(
            f"%{search}%"
        ) | db.contratos.referencia_contrato.ilike(f"%{search}%")

    if sort_by == "valor":
        orderby = ~db.contratos.valor_contrato
    else:
        orderby = ~db.contratos.fecha_firma

    limit = 50
    offset = (page - 1) * limit

    contratos = db(query).select(orderby=orderby, limitby=(offset, offset + limit))

    stats = {"total_contratos": 0, "valor_total": 0.0, "promedio": 0.0}
    chart_data = "[]"
    is_htmx = request.headers.get("HX-Request")

    if not is_htmx or page == 1:
        conteo = db.contratos.id.count()
        suma = db.contratos.valor_contrato.sum()
        stats_query = db(db.contratos.nit_entidad == nit).select(conteo, suma).first()

        stats = {
            "total_contratos": stats_query[conteo] or 0,
            "valor_total": float(stats_query[suma] or 0),
            "promedio": float(stats_query[suma] or 0) / (stats_query[conteo] or 1),
        }

        is_postgres = db._uri.startswith("postgres")
        if is_postgres:
            chart_query = """
                SELECT TO_CHAR(fecha_firma, 'YYYY-MM') as mes, count(id) as cantidad, sum(valor_contrato) as total 
                FROM contratos 
                WHERE nit_entidad = %s AND fecha_firma IS NOT NULL
                GROUP BY TO_CHAR(fecha_firma, 'YYYY-MM') 
                ORDER BY mes
            """
        else:
            chart_query = """
                SELECT strftime('%Y-%m', fecha_firma) as mes, count(id) as cantidad, sum(valor_contrato) as total 
                FROM contratos 
                WHERE nit_entidad = ? AND fecha_firma IS NOT NULL
                GROUP BY mes 
                ORDER BY mes
            """
        try:
            chart_data_raw = db.executesql(
                chart_query, placeholders=[nit], as_dict=True
            )
            chart_data = json.dumps(chart_data_raw)
        except Exception as e:
            print("Error chart:", e)

    context = {
        "request": request,
        "entidad": entidad,
        "contratos": contratos,
        "stats": stats,
        "chart_data": chart_data,
        "page": page,
        "search": search or "",
        "sort_by": sort_by,
    }

    if is_htmx:
        return templates.TemplateResponse("entidad_filas.html", context)

    return templates.TemplateResponse("entidad_detalle.html", context)


@app.get("/proveedor/{documento}", response_class=HTMLResponse)
async def proveedor_detalle(
    request: Request,
    documento: str,
    page: int = 1,
    search: Optional[str] = Query(None),
    sort_by: str = Query("fecha"),
):
    proveedor = db(db.proveedoresypersonas.documento == documento).select().first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    query = db.contratos.documento_proveedor == documento

    if search:
        query &= db.contratos.id_contrato.ilike(
            f"%{search}%"
        ) | db.contratos.nombre_entidad.ilike(f"%{search}%")

    if sort_by == "valor":
        orderby = ~db.contratos.valor_contrato
    else:
        orderby = ~db.contratos.fecha_firma

    limit = 50
    offset = (page - 1) * limit

    contratos = db(query).select(orderby=orderby, limitby=(offset, offset + limit))

    stats = {"total_contratos": 0, "valor_total": 0.0, "promedio": 0.0}
    chart_data = "[]"
    is_htmx = request.headers.get("HX-Request")

    if not is_htmx or page == 1:
        conteo = db.contratos.id.count()
        suma = db.contratos.valor_contrato.sum()
        stats_query = (
            db(db.contratos.documento_proveedor == documento)
            .select(conteo, suma)
            .first()
        )

        stats = {
            "total_contratos": stats_query[conteo] or 0,
            "valor_total": float(stats_query[suma] or 0),
            "promedio": float(stats_query[suma] or 0) / (stats_query[conteo] or 1),
        }

        is_postgres = db._uri.startswith("postgres")
        if is_postgres:
            chart_query = """
                SELECT TO_CHAR(fecha_firma, 'YYYY-MM') as mes, count(id) as cantidad, sum(valor_contrato) as total 
                FROM contratos 
                WHERE documento_proveedor = %s AND fecha_firma IS NOT NULL
                GROUP BY TO_CHAR(fecha_firma, 'YYYY-MM') 
                ORDER BY mes
            """
        else:
            chart_query = """
                SELECT strftime('%Y-%m', fecha_firma) as mes, count(id) as cantidad, sum(valor_contrato) as total 
                FROM contratos 
                WHERE documento_proveedor = ? AND fecha_firma IS NOT NULL
                GROUP BY mes 
                ORDER BY mes
            """
        try:
            chart_data_raw = db.executesql(
                chart_query, placeholders=[documento], as_dict=True
            )
            chart_data = json.dumps(chart_data_raw)
        except Exception as e:
            print("Error chart:", e)

    sanciones = db(db.sancionados.documento == documento).select()

    contratos_post_sancion = 0
    if len(sanciones) > 0:
        fechas_sanciones = [
            s.fecha_efectos_juridicos for s in sanciones if s.fecha_efectos_juridicos
        ]
        if fechas_sanciones:
            primera_sancion = min(fechas_sanciones)
            contratos_post_sancion = db(
                (db.contratos.documento_proveedor == documento)
                & (db.contratos.fecha_firma >= primera_sancion)
            ).count()

    context = {
        "request": request,
        "proveedor": proveedor,
        "contratos": contratos,
        "stats": stats,
        "chart_data": chart_data,
        "sanciones": sanciones,
        "contratos_post_sancion": contratos_post_sancion,
        "page": page,
        "search": search or "",
        "sort_by": sort_by,
    }

    if is_htmx:
        return templates.TemplateResponse("proveedor_filas.html", context)

    return templates.TemplateResponse("proveedor_detalle.html", context)


@app.get("/populed")
async def populed(request: Request):
    try:
        claveApiSocrata = extractConfig(nameModel="SocratesApi", dataOut="claveAppApi")
    except:
        claveApiSocrata = os.getenv("claveApiSocrata")

    print(f"API Key: {claveApiSocrata[:20] if claveApiSocrata else 'None'}...")

    client = Socrata("www.datos.gov.co", app_token=claveApiSocrata)
    SancionesSecopI = "4n4q-k399"
    reloj = time.time()
    t = 0
    insertados = 0
    duplicados = 0
    errores = 0

    for item in client.get_all(SancionesSecopI):
        resultado = guardar_amonestado_secop(item)
        if resultado:
            if resultado.get("exito"):
                if resultado.get("accion") == "insertado":
                    insertados += 1
                elif resultado.get("accion") == "duplicado":
                    duplicados += 1
            else:
                errores += 1
                print(f"Error: {resultado.get('mensaje')}")
        t += 1
        if t % 500 == 0:
            db.commit()
            print(
                f"Procesados: {t}, Insertados: {insertados}, Duplicados: {duplicados}, Errores: {errores}"
            )

    db.commit()
    AntededentesSiri = "iaeu-rcn6"
    reloj = time.time()
    t = 0
    for item in client.get_all(AntededentesSiri):
        guardar_sancionado_siri(item)
        t += 1
        if t % 500 == 0:
            db.commit()
    db.commit()
    return {
        "listo": True,
        "tiempo": time.time() - reloj,
        "total": t,
        "insertados": insertados,
        "duplicados": duplicados,
        "errores": errores,
    }











