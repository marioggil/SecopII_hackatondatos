from fastapi import FastAPI, Query, File, UploadFile,Form,HTTPException
from pydantic import BaseModel, field_validator, computed_field, Field as PydanticField
from typing import Dict, Annotated, Literal, Union,Optional, List
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
from pydal import DAL, Field
from datetime import date, datetime
from fastapi import FastAPI, HTTPException
import pandas as pd
from sodapy import Socrata


pwd = os.getcwd()
app = FastAPI()
def extractConfig(nameModel="SystemData",relPath=os.path.join(pwd,"private/experiment_config.json"),dataOut="keyantrophics"):
    configPath=os.path.join(os.getcwd(),relPath)
    with open(configPath, 'r', encoding='utf-8') as file:
        config = json.load(file)[nameModel]
    Output= config[dataOut]
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

@app.get('/', response_class=HTMLResponse)
async def root(request: Request):
    context = {
        "request": request}
    
    return templates.TemplateResponse("index.html", context)

@app.get('/html/index_info', response_class=HTMLResponse)
async def index_tot(request: Request):
    context = {
        "request": request}
    
    return templates.TemplateResponse("index_tot.html", context)

@app.get('/html/header', response_class=HTMLResponse)
async def header(request: Request):
    context = {
        "request": request}
    
    return templates.TemplateResponse("header.html", context)

@app.get('/html/section_cards', response_class=HTMLResponse)
async def section_cards(request: Request):
    context = {
        "request": request}
    
    return templates.TemplateResponse("section_cards.html", context)
@app.get('/html/footer', response_class=HTMLResponse)
async def footer(request: Request):
    context = {
        "request": request}
    
    return templates.TemplateResponse("footer.html", context)

@app.get('/html/index_graph.html', response_class=HTMLResponse)
async def graph(request: Request):
    context = {
        "request": request}
    
    return templates.TemplateResponse("graph_ente_prove.html", context)



# ============= CONFIGURACIÓN DE LA BASE DE DATOS =============
db = DAL('sqlite://contratos.db', folder='databases', pool_size=10)
db.define_table('contratos',
    # Información de la entidad
    Field('nombre_entidad', 'string', length=255),
    Field('nit_entidad', 'string', length=50),
    Field('departamento', 'string', length=100),
    Field('ciudad', 'string', length=100),
    Field('orden', 'string', length=50),
    Field('sector', 'string', length=100),
    Field('rama', 'string', length=50),
    Field('entidad_centralizada', 'string', length=50),
    Field('codigo_entidad', 'string', length=50),
    
    # Información del proceso y contrato
    Field('proceso_de_compra', 'string', length=100),
    Field('id_contrato', 'string', length=100, notnull=True, unique=True),
    Field('referencia_del_contrato', 'string', length=255),
    Field('estado_contrato', 'string', length=50),
    Field('codigo_de_categoria_principal', 'string', length=50),
    Field('descripcion_del_proceso', 'text'),
    Field('tipo_de_contrato', 'string', length=100),
    Field('modalidad_de_contratacion', 'string', length=100),
    Field('justificacion_modalidad_de', 'string', length=255),
    Field('objeto_del_contrato', 'text'),
    Field('duraci_n_del_contrato', 'string', length=50),
    
    # Fechas
    Field('fecha_de_firma', 'datetime'),
    Field('fecha_de_inicio_del_contrato', 'datetime'),
    Field('fecha_de_fin_del_contrato', 'datetime'),
    Field('fecha_inicio_liquidacion', 'datetime'),
    Field('fecha_fin_liquidacion', 'datetime'),
    Field('ultima_actualizacion', 'datetime'),
    
    # Información del proveedor
    Field('documento_proveedor', 'string', length=50),
    Field('proveedor_adjudicado', 'string', length=255),
    Field('codigo_proveedor', 'string', length=50),
    Field('es_grupo', 'string', length=10),
    Field('es_pyme', 'string', length=10),
    
    # Representante legal
    Field('nombre_representante_legal', 'string', length=255),
    Field('nacionalidad_representante_legal', 'string', length=10),
    Field('domicilio_representante_legal', 'string', length=255),
    Field('identificaci_n_representante_legal', 'string', length=50),
    
    # Condiciones y características
    Field('condiciones_de_entrega', 'string', length=100),
    Field('habilita_pago_adelantado', 'string', length=10),
    Field('liquidaci_n', 'string', length=10),
    Field('obligaci_n_ambiental', 'string', length=10),
    Field('obligaciones_postconsumo', 'string', length=10),
    Field('reversion', 'string', length=10),
    Field('el_contrato_puede_ser_prorrogado', 'string', length=10),
    Field('dias_adicionados', 'string', length=20),
    
    # Información financiera
    Field('origen_de_los_recursos', 'string', length=100),
    Field('destino_gasto', 'string', length=100),
    Field('valor_del_contrato', 'string', length=50),
    Field('valor_de_pago_adelantado', 'string', length=50),
    Field('valor_facturado', 'string', length=50),
    Field('valor_pendiente_de_pago', 'string', length=50),
    Field('valor_pagado', 'string', length=50),
    Field('valor_amortizado', 'string', length=50),
    Field('valor_pendiente_de', 'string', length=50),
    Field('valor_pendiente_de_ejecucion', 'string', length=50),
    Field('saldo_cdp', 'string', length=50),
    Field('saldo_vigencia', 'string', length=50),
    Field('recursos_propios_alcald_as_gobernaciones_y_resguardos_ind_genas_', 'string', length=50),
    

    
    # Postconflicto
    Field('espostconflicto', 'string', length=10),
    Field('puntos_del_acuerdo', 'string', length=100),
    Field('pilares_del_acuerdo', 'string', length=100),
    
    # URL y documentos
    Field('documentos_tipo', 'string', length=10),
    Field('descripcion_documentos_tipo', 'string', length=255),
    
    # Información bancaria
    Field('nombre_del_banco', 'string', length=100),
    Field('tipo_de_cuenta', 'string', length=50),
    
    # Ordenadores y supervisores
    Field('nombre_ordenador_del_gasto', 'string', length=255),
    Field('n_mero_de_documento_ordenador_del_gasto', 'string', length=50),
    Field('nombre_supervisor', 'string', length=255),
    Field('n_mero_de_documento_supervisor', 'string', length=50),
    Field('nombre_ordenador_de_pago', 'string', length=255),
    Field('n_mero_de_documento_ordenador_de_pago', 'string', length=50),
    
    format='%(id_contrato)s'
)


db.define_table('entidades',
    #Field('nombreEntidad', 'string', length=255, notnull=True),
    Field('nit_entidad', 'string', length=50, notnull=True, unique=True),
    Field('departamento', 'string', length=100),
    Field('ciudad', 'string', length=100),
    Field('orden', 'string', length=50),
    Field('sector', 'string', length=100),
    Field('rama', 'string', length=50),
    Field('entidad_centralizada', 'string', length=50),
    format='%(nombre_entidad)s'
)
db.define_table('personas',
    Field('documento', 'string', length=50, notnull=True, unique=True),
    Field('nombre', 'string', length=255, notnull=True),
    Field('es_grupo', 'string', length=10, default='No'),
    Field('es_pyme', 'string', length=10, default='No'),
    format='%(nombre)s'
)

db.define_table('adiciones',
    Field('id_contrato', required=True),
    Field('identificador', 'string', required=True),
    Field('tipo', 'string'),
    Field('descripcion', 'text'),
    Field('fecharegistro', 'date')
)

# ============= MODELOS Pydantic =============


class ContratoCreate(BaseModel):
    # # Información de la entidad
    # nombre_entidad: Optional[str] = PydanticField(None, max_length=255)
    # nit_entidad: Optional[str] = PydanticField(None, max_length=50)
    # departamento: Optional[str] = PydanticField(None, max_length=100)
    # ciudad: Optional[str] = PydanticField(None, max_length=100)
    # localizacion: Optional[str] = PydanticField(None, max_length=255)
    # orden: Optional[str] = PydanticField(None, max_length=50)
    # sector: Optional[str] = PydanticField(None, max_length=100)
    # rama: Optional[str] = PydanticField(None, max_length=50)
    # entidad_centralizada: Optional[str] = PydanticField(None, max_length=50)
    # codigo_entidad: Optional[str] = PydanticField(None, max_length=50)
    
    # # Información del proceso y contrato
    # proceso_de_compra: Optional[str] = PydanticField(None, max_length=100)
    id_contrato: str = PydanticField(..., max_length=100)
    # referencia_del_contrato: Optional[str] = PydanticField(None, max_length=255)
    # estado_contrato: Optional[str] = PydanticField(None, max_length=50)
    # codigo_de_categoria_principal: Optional[str] = PydanticField(None, max_length=50)
    # descripcion_del_proceso: Optional[str] = None
    # tipo_de_contrato: Optional[str] = PydanticField(None, max_length=100)
    # modalidad_de_contratacion: Optional[str] = PydanticField(None, max_length=100)
    # justificacion_modalidad_de: Optional[str] = PydanticField(None, max_length=255)
    # objeto_del_contrato: Optional[str] = None
    # duraci_n_del_contrato: Optional[str] = PydanticField(None, max_length=50)
    
    # # Fechas
    # fecha_de_firma: Optional[datetime] = None
    # fecha_de_inicio_del_contrato: Optional[datetime] = None
    # fecha_de_fin_del_contrato: Optional[datetime] = None
    # fecha_inicio_liquidacion: Optional[datetime] = None
    # fecha_fin_liquidacion: Optional[datetime] = None
    # ultima_actualizacion: Optional[datetime] = None
    
    # # Información del proveedor
    # tipodocproveedor: Optional[str] = PydanticField(None, max_length=50)
    # documento_proveedor: Optional[str] = PydanticField(None, max_length=50)
    # proveedor_adjudicado: Optional[str] = PydanticField(None, max_length=255)
    # codigo_proveedor: Optional[str] = PydanticField(None, max_length=50)
    # es_grupo: Optional[str] = PydanticField(None, max_length=10)
    # es_pyme: Optional[str] = PydanticField(None, max_length=10)
    
    # # Representante legal
    # nombre_representante_legal: Optional[str] = PydanticField(None, max_length=255)
    # nacionalidad_representante_legal: Optional[str] = PydanticField(None, max_length=10)
    # domicilio_representante_legal: Optional[str] = PydanticField(None, max_length=255)
    # identificaci_n_representante_legal: Optional[str] = PydanticField(None, max_length=50)
    
    # # Condiciones y características
    # condiciones_de_entrega: Optional[str] = PydanticField(None, max_length=100)
    # habilita_pago_adelantado: Optional[str] = PydanticField(None, max_length=10)
    # liquidaci_n: Optional[str] = PydanticField(None, max_length=10)
    # obligaci_n_ambiental: Optional[str] = PydanticField(None, max_length=10)
    # obligaciones_postconsumo: Optional[str] = PydanticField(None, max_length=10)
    # reversion: Optional[str] = PydanticField(None, max_length=10)
    # el_contrato_puede_ser_prorrogado: Optional[str] = PydanticField(None, max_length=10)
    # dias_adicionados: Optional[str] = PydanticField(None, max_length=20)
    
    # # Información financiera
    # origen_de_los_recursos: Optional[str] = PydanticField(None, max_length=100)
    # destino_gasto: Optional[str] = PydanticField(None, max_length=100)
    # valor_del_contrato: Optional[str] = PydanticField(None, max_length=50)
    # valor_de_pago_adelantado: Optional[str] = PydanticField(None, max_length=50)
    # valor_facturado: Optional[str] = PydanticField(None, max_length=50)
    # valor_pendiente_de_pago: Optional[str] = PydanticField(None, max_length=50)
    # valor_pagado: Optional[str] = PydanticField(None, max_length=50)
    # valor_amortizado: Optional[str] = PydanticField(None, max_length=50)
    # valor_pendiente_de: Optional[str] = PydanticField(None, max_length=50)
    # valor_pendiente_de_ejecucion: Optional[str] = PydanticField(None, max_length=50)
    # saldo_cdp: Optional[str] = PydanticField(None, max_length=50)
    # saldo_vigencia: Optional[str] = PydanticField(None, max_length=50)
    # recursos_propios_alcald_as_gobernaciones_y_resguardos_ind_genas_: Optional[str] = PydanticField(None, max_length=50)
    
    # # BPIN
    # estado_bpin: Optional[str] = PydanticField(None, max_length=50)
    # codigo_bpin: Optional[str] = PydanticField(None, max_length=50)
    # anno_bpin: Optional[str] = PydanticField(None, max_length=20)
    
    # # Postconflicto
    # espostconflicto: Optional[str] = PydanticField(None, max_length=10)
    # puntos_del_acuerdo: Optional[str] = PydanticField(None, max_length=100)
    # pilares_del_acuerdo: Optional[str] = PydanticField(None, max_length=100)
    
    # # URL y documentos

    # documentos_tipo: Optional[str] = PydanticField(None, max_length=10)
    # descripcion_documentos_tipo: Optional[str] = PydanticField(None, max_length=255)
    
    # # Información bancaria
    # nombre_del_banco: Optional[str] = PydanticField(None, max_length=100)
    # tipo_de_cuenta: Optional[str] = PydanticField(None, max_length=50)
    # numero_de_cuenta: Optional[str] = PydanticField(None, max_length=50)
    
    # # Ordenadores y supervisores
    # nombre_ordenador_del_gasto: Optional[str] = PydanticField(None, max_length=255)
    
    # n_mero_de_documento_ordenador_del_gasto: Optional[str] = PydanticField(None, max_length=50)
    # nombre_supervisor: Optional[str] = PydanticField(None, max_length=255)

    # n_mero_de_documento_supervisor: Optional[str] = PydanticField(None, max_length=50)
    # nombre_ordenador_de_pago: Optional[str] = PydanticField(None, max_length=255)

    # n_mero_de_documento_ordenador_de_pago: Optional[str] = PydanticField(None, max_length=50)

class EntidadModel(BaseModel):
    #nombreEntidad: str = PydanticField(..., max_length=255)
    nit_entidad: str = PydanticField(..., max_length=50)
    departamento: Optional[str] = PydanticField(None, max_length=100)
    ciudad: Optional[str] = PydanticField(None, max_length=100)
    orden: Optional[str] = PydanticField(None, max_length=50)
    sector: Optional[str] = PydanticField(None, max_length=100)
    rama: Optional[str] = PydanticField(None, max_length=50)
    entidad_centralizada: Optional[str] = PydanticField(None, max_length=50)

class PersonaModel(BaseModel):
    documento: str = PydanticField(..., max_length=50)
    nombre: str = PydanticField(..., max_length=255)
    es_grupo: str = PydanticField(default='No', max_length=10)
    es_pyme: str = PydanticField(default='No', max_length=10)
    es_sancionado: Optional[str] = PydanticField(default="No", max_length=10)
    @field_validator('documento')
    @classmethod
    def validar_documento(cls, v):
        if v.strip().lower() == 'no definido':
            raise ValueError('El documento no puede ser "No Definido"')
        return v
    
    @field_validator('nombre')
    @classmethod
    def validar_nombre(cls, v):
        if v.strip().lower() == 'no definido':
            raise ValueError('El nombre no puede ser "No Definido"')
        return v

class AdicionModel(BaseModel):
    id_contrato: str
    identificador: str
    tipo: Optional[str] = None
    descripcion: Optional[str] = None
    fecharegistro: Optional[date] = None

# ============= ENDPOINTS =============

def verificar_personas_entidades_contrato(AllData):
        claves_a_seleccionar=['nit_entidad','nombre_entidad',  'departamento',
        'ciudad',
        'orden',
        'sector',
        'rama',
        'entidad_centralizada']
        entidad = {k: v for k, v in AllData.items() if k in claves_a_seleccionar}

        claves_a_seleccionar=[  'documento_proveedor',
        'proveedor_adjudicado',
        'es_grupo',
        'es_pyme']
        proveedor = {k: v for k, v in AllData.items() if k in claves_a_seleccionar}


        claves_a_seleccionar=['nombre_representante_legal',
        'identificaci_n_representante_legal']
        representante_legal = {k: v for k, v in AllData.items() if k in claves_a_seleccionar}

        claves_a_seleccionar=['nombre_ordenador_del_gasto',
        'n_mero_de_documento_ordenador_del_gasto']
        ordenador_gasto = {k: v for k, v in AllData.items() if k in claves_a_seleccionar}


        claves_a_seleccionar=['nombre_supervisor',
        'n_mero_de_documento_supervisor']
        supervisor = {k: v for k, v in AllData.items() if k in claves_a_seleccionar}


        supervisor={"nombre": supervisor['nombre_supervisor'],
        "documento": supervisor['n_mero_de_documento_supervisor']}
        proveedor={"documento": proveedor['documento_proveedor'],"nombre": proveedor['proveedor_adjudicado'], "esGrupo": proveedor['es_grupo'], "esPyme": proveedor['es_pyme']}
        representante_legal={"nombre": representante_legal['nombre_representante_legal'],
        "documento": representante_legal['identificaci_n_representante_legal']}
        ordenador_gasto={"nombre": ordenador_gasto['nombre_ordenador_del_gasto'],
        "documento": ordenador_gasto['n_mero_de_documento_ordenador_del_gasto']}

        return entidad, proveedor, representante_legal, ordenador_gasto, supervisor

def insertar_entidad(entidad_data):
    if not entidad_data["nit_entidad"]:
        return []
    if entidad_data["nit_entidad"].strip().lower() == 'no definido':
        return []
    entidad_existente = db(db.entidades.nit_entidad == entidad_data["nit_entidad"]).select().first()
    if entidad_existente:
        return []
    id_registro = db.entidades.insert(**entidad_data)
    db.commit()
    return id_registro

def insertar_persona(persona_data):
    if not persona_data["documento"] or not persona_data["nombre"]:
        return []
    if persona_data["documento"].strip().lower() == 'no definido' or persona_data["nombre"].strip().lower() == 'no definido' or persona_data["documento"].strip().lower() == 'sin descripcion' or persona_data["nombre"].strip() == '':
        return []
    persona_existente = db(db.personas.documento == persona_data["documento"]).select().first()
    if persona_existente:
        return []
    id_registro = db.personas.insert(**persona_data)
    db.commit()
    return id_registro



@app.post("/contratos/", status_code=201)
async def crear_contrato(contrato: ContratoCreate):
    """
    Endpoint para crear un nuevo contrato en la base de datos.
    
    - **id_contrato**: Identificador único del contrato (requerido)
    - Todos los demás campos son opcionales
    """
    #try:
        # Aquí insertarías en tu base de datos con PyDAL
        # db.contratos.insert(**contrato.model_dump(exclude_none=True))
    pwd=os.path.dirname("app/private/experiment_config.json")
    claveApiSocrata=extractConfig(nameModel="SocratesApi",dataOut="claveAppApi")
    client = Socrata("www.datos.gov.co", claveApiSocrata)
    temp="id_contrato == '{}'".format(contrato.id_contrato)
    Contr=client.get("jbjy-vk9h" ,where="id_contrato == '{}'".format(contrato.id_contrato))
    entidad, proveedor, representante_legal, ordenador_gasto, supervisor=verificar_personas_entidades_contrato(Contr[0])
    print(entidad, proveedor, representante_legal, ordenador_gasto, supervisor)
    insertar_entidad(entidad)
    for temp in [proveedor, representante_legal, ordenador_gasto, supervisor]:
        try:
            insertar_persona(temp)
        except:
            pass

    try:
        db.contratos.insert(**Contr[0])
        db.commit()

        return {
            "message": "Contrato creado exitosamente",
            
            "id_contrato": contrato.id_contrato
        }
    
    except Exception as e:
        # Manejo de error de duplicado por unique constraint
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(
                status_code=400,
                detail=f"El id_contrato '{contrato.id_contrato}' ya existe"
            )
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/contratos/{id_contrato}")
async def obtener_contrato(id_contrato: str):
    """
    Endpoint para obtener un contrato específico por su ID.
    """
    try:
        contrato = db(db.contratos.id_contrato == id_contrato).select().first()
        
        if not contrato:
            raise HTTPException(status_code=404, detail="Contrato no encontrado")
        
        return contrato.as_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/entidad/{nit_entidad}")
def obtener_entidad(nit_entidad: str):
    try:
        # Buscar entidad por NIT
        entidad = db(db.entidades.nit_entidad == nit_entidad).select().first()
        
        if not entidad:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró una entidad con el NIT {nit_entidad}"
            )
        
        # Convertir a diccionario y retornar
        return entidad.as_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/personas/{documento}")
def obtener_persona(documento: str):
    try:
        # Buscar persona por documento
        persona = db(db.personas.documento == documento).select().first()
        
        if not persona:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró una persona con el documento {documento}"
            )
        
        # Convertir a diccionario y retornar
        return persona.as_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/adiciones/", status_code=201)
def crear_adicion(adicion: AdicionModel):
    #try:
    # Verificar que el contrato existe
    contrato = db(db.contratos.id_contrato == adicion.id_contrato).select().first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    
    # Preparar datos para inserción
    datos = adicion.model_dump()
    # Usar el id numérico de la referencia
    
    # Verificar si ya existe una adición con el mismo IdContrato e Identificador
    adicion_existente = db(
        (db.adiciones.id_contrato == adicion.id_contrato) & 
        (db.adiciones.identificador == adicion.identificador)
    ).select().first()
    
    if adicion_existente:
        # Comparar si la información es diferente
        datos_existentes = {k: v for k, v in adicion_existente.as_dict().items() 
                        if k not in ['id', 'created_on', 'modified_on']}
        datos_nuevos = {k: v for k, v in datos.items() 
                        if k not in ['id', 'created_on', 'modified_on']}
        
        if datos_existentes != datos_nuevos:
            # Actualizar el registro existente
            adicion_existente.update_record(**datos)
            db.commit()
            return {
                "message": "Adición actualizada exitosamente", 
                "id": adicion_existente.id,
                "action": "updated"
            }
        else:
            # La información es igual, no hacer nada
            return {
                "message": "La adición ya existe con la misma información", 
                "id": adicion_existente.id,
                "action": "no_change"
            }
    else:
        # No existe, crear nuevo registro
        id_registro = db.adiciones.insert(**datos)
        db.commit()
        return {
            "message": "Adición creada exitosamente", 
            "id": id_registro,
            "action": "created"
        }


    

    # except HTTPException:
    #     raise
    # except Exception as e:
    #     db.rollback()
    #     raise HTTPException(status_code=500, detail=str(e))
# Nota: Asume que 'db' es tu instancia de DAL ya configurada
# from pydal import DAL
# db = DAL('sqlite://storage.db')