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

pwd = os.getcwd()
app = FastAPI()
def extractConfig(nameModel="SystemData",relPath=os.path.join(pwd,"conf/experiment_config.json"),dataOut="keyantrophics"):
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



# Tabla de contratos

# ===== DEFINICIÓN DE LA TABLA CONTRATOS EN PYDAL =====

db.define_table('contratos',
    # Información de la entidad
    Field('nombre_entidad', 'string', length=255),
    Field('nit_entidad', 'string', length=50),
    Field('departamento', 'string', length=100),
    Field('ciudad', 'string', length=100),
    Field('localizacion', 'string', length=255),
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
    Field('duracion_del_contrato', 'string', length=50),
    
    # Fechas
    Field('fecha_de_firma', 'datetime'),
    Field('fecha_de_inicio_del_contrato', 'datetime'),
    Field('fecha_de_fin_del_contrato', 'datetime'),
    Field('fecha_inicio_liquidacion', 'datetime'),
    Field('fecha_fin_liquidacion', 'datetime'),
    Field('ultima_actualizacion', 'datetime'),
    
    # Información del proveedor
    Field('tipodocproveedor', 'string', length=50),
    Field('documento_proveedor', 'string', length=50),
    Field('proveedor_adjudicado', 'string', length=255),
    Field('codigo_proveedor', 'string', length=50),
    Field('es_grupo', 'string', length=10),
    Field('es_pyme', 'string', length=10),
    
    # Representante legal
    Field('nombre_representante_legal', 'string', length=255),
    Field('nacionalidad_representante_legal', 'string', length=10),
    Field('domicilio_representante_legal', 'string', length=255),
    Field('tipo_de_identificacion_representante_legal', 'string', length=100),
    Field('identificacion_representante_legal', 'string', length=50),
    Field('genero_representante_legal', 'string', length=20),
    
    # Condiciones y características
    Field('condiciones_de_entrega', 'string', length=100),
    Field('habilita_pago_adelantado', 'string', length=10),
    Field('liquidacion', 'string', length=10),
    Field('obligacion_ambiental', 'string', length=10),
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
    Field('recursos_propios_alcaldias_gobernaciones_y_resguardos_indigenas', 'string', length=50),
    
    # BPIN
    Field('estado_bpin', 'string', length=50),
    Field('codigo_bpin', 'string', length=50),
    Field('anno_bpin', 'string', length=20),
    
    # Postconflicto
    Field('espostconflicto', 'string', length=10),
    Field('puntos_del_acuerdo', 'string', length=100),
    Field('pilares_del_acuerdo', 'string', length=100),
    
    # URL y documentos
    Field('urlproceso', 'string', length=500),
    Field('documentos_tipo', 'string', length=10),
    Field('descripcion_documentos_tipo', 'string', length=255),
    
    # Información bancaria
    Field('nombre_del_banco', 'string', length=100),
    Field('tipo_de_cuenta', 'string', length=50),
    Field('numero_de_cuenta', 'string', length=50),
    
    # Ordenadores y supervisores
    Field('nombre_ordenador_del_gasto', 'string', length=255),
    Field('tipo_de_documento_ordenador_del_gasto', 'string', length=50),
    Field('numero_de_documento_ordenador_del_gasto', 'string', length=50),
    Field('nombre_supervisor', 'string', length=255),
    Field('tipo_de_documento_supervisor', 'string', length=50),
    Field('numero_de_documento_supervisor', 'string', length=50),
    Field('nombre_ordenador_de_pago', 'string', length=255),
    Field('tipo_de_documento_ordenador_de_pago', 'string', length=50),
    Field('numero_de_documento_ordenador_de_pago', 'string', length=50),
    
    format='%(id_contrato)s'
)

# Tabla de adiciones
db.define_table('adiciones',
    Field('IdContrato', 'reference contratos', required=True),
    Field('Identificador', 'string', required=True),
    Field('Tipo', 'string'),
    Field('Descripcion', 'text'),
    Field('FechaRegistro', 'date')
)

# Tabla de ejecucion
db.define_table('ejecucion',
    Field('IdContrato', 'reference contratos', required=True),
    Field('TipoDeEjecucion', 'string'),
    Field('NombreDelPlan', 'string'),
    Field('FechaDeEntregaEsperada', 'date'),
    Field('PorcentajeDeAvanceEsperado', 'double'),
    Field('FechaDeEntregaReal', 'date'),
    Field('PorcentajedeAvanceReal', 'double'),
    Field('EstadoDelContrato', 'string'),
    Field('CantidadAdjudicada', 'double'),
    Field('CantidadPlaneada', 'double'),
    Field('CantidadRecibida', 'double'),
    Field('CantidadPorRecibir', 'double')
)

db.define_table('entidades',
    #Field('nombreEntidad', 'string', length=255, notnull=True),
    Field('nitEntidad', 'string', length=50, notnull=True, unique=True),
    Field('departamento', 'string', length=100),
    Field('ciudad', 'string', length=100),
    Field('orden', 'string', length=50),
    Field('sector', 'string', length=100),
    Field('rama', 'string', length=50),
    Field('entidadCentralizada', 'string', length=50),
    format='%(nombre_entidad)s'
)
db.define_table('personas',
    Field('documento', 'string', length=50, notnull=True, unique=True),
    Field('nombre', 'string', length=255, notnull=True),
    Field('esGrupo', 'string', length=10, default='No'),
    Field('esPyme', 'string', length=10, default='No'),
    format='%(nombre)s'
)

# Tabla de estadisticas
db.define_table('estadisticas',
    Field('campo', 'string', required=True),#Como llamo al dato para analizar
    Field('entidad', 'string', required=True),#Filtrado por un dato Ejemplo año
    Field('year', 'string', required=True), #filtrado por otro dato ejemplo 2025
    Field('textoVisible', 'string'),
    Field('valor', 'string')
)


db.commit()

# ============= MODELOS PYDANTIC PARA FASTAPI =============
class ContratoModel(BaseModel):
    IdContrato: str
    EstadoContrato: Optional[str] = None
    TipodeContrato: Optional[str] = None
    ModalidadDeContratacion: Optional[str] = None
    JustificacionModalidadContratacion: Optional[str] = None
    ObjetoDelContrato: Optional[str] = None
    URLProceso: Optional[str] = None
    DuracióndelContrato: Optional[int] = None
    ElContratoPuedeSerProrrogado: Optional[bool] = None
    FechaDeNotificaciónDeProrrogación: Optional[date] = None
    FechaDeFirma: Optional[date] = None
    FechaDeInicioContrato: Optional[date] = None
    FechaDeFinContrato: Optional[date] = None
    DiasAdicionados: Optional[int] = None
    FechaInicioLiquidacion: Optional[date] = None
    FechaFinLiquidacion: Optional[date] = None
    #NombreEntidad: Optional[str] = None
    NitEntidad: Optional[str] = None
    EntidadCentralizada: Optional[bool] = None
    CodigoProveedor: Optional[str] = None
    DocumentoProveedor: Optional[str] = None
    ProveedorAdjudicado: Optional[str] = None
    EsGrupo: Optional[bool] = None
    EsPyme: Optional[bool] = None
    IdentificaciónRepresentanteLegal: Optional[str] = None
    NúmeroDeDocumentoOrdenadorDelGasto: Optional[str] = None
    NúmeroDeDocumentoSupervisor: Optional[str] = None
    NúmeroDeDocumentoOrdenadordePago: Optional[str] = None
    OrigendelosRecursos: Optional[str] = None
    DestinoGasto: Optional[str] = None
    ValordelContrato: Optional[float] = None
    ValorDePagoAdelantado: Optional[float] = None
    ValorFacturado: Optional[float] = None
    ValorPendienteDePago: Optional[float] = None
    ValorPagado: Optional[float] = None
    ValorAmortizado: Optional[float] = None
    ValorPendientedeAmortizacion: Optional[float] = None
    ValorPendienteDeEjecucion: Optional[float] = None
    SaldoCDP: Optional[float] = None
    SaldoVigencia: Optional[float] = None

class AdicionModel(BaseModel):
    IdContrato: str
    Identificador: str
    Tipo: Optional[str] = None
    Descripcion: Optional[str] = None
    FechaRegistro: Optional[date] = None

class EjecucionModel(BaseModel):
    IdContrato: str
    TipoDeEjecucion: Optional[str] = None
    NombreDelPlan: Optional[str] = None
    FechaDeEntregaEsperada: Optional[date] = None
    PorcentajeDeAvanceEsperado: Optional[float] = None
    FechaDeEntregaReal: Optional[date] = None
    PorcentajedeAvanceReal: Optional[float] = None
    EstadoDelContrato: Optional[str] = None
    CantidadAdjudicada: Optional[float] = None
    CantidadPlaneada: Optional[float] = None
    CantidadRecibida: Optional[float] = None
    CantidadPorRecibir: Optional[float] = None

class EstadisticaModel(BaseModel):
    campo: str
    seccion: str
    variable: str
    texto_visible: Optional[str] = None
    valor: Optional[str] = None

class EntidadModel(BaseModel):
    #nombreEntidad: str = PydanticField(..., max_length=255)
    nitEntidad: str = PydanticField(..., max_length=50)
    departamento: Optional[str] = PydanticField(None, max_length=100)
    ciudad: Optional[str] = PydanticField(None, max_length=100)
    orden: Optional[str] = PydanticField(None, max_length=50)
    sector: Optional[str] = PydanticField(None, max_length=100)
    rama: Optional[str] = PydanticField(None, max_length=50)
    entidadCentralizada: Optional[str] = PydanticField(None, max_length=50)

class PersonaModel(BaseModel):
    documento: str = PydanticField(..., max_length=50)
    nombre: str = PydanticField(..., max_length=255)
    esGrupo: str = PydanticField(default='No', max_length=10)
    esPyme: str = PydanticField(default='No', max_length=10)
    
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
    
# ===== ENDPOINTS PARA CONTRATOS =====
def verificar_personas_entidades_contrato(AllData):
        claves_a_seleccionar=['nit_entidad','nombre_entidad',  'departamento',
        'ciudad',
        'orden',
        'sector',
        'rama',
        'entidad_centralizada']
        entidad = {k: v for k, v in AllData["ContratosE"][0].items() if k in claves_a_seleccionar}

        claves_a_seleccionar=[  'documento_proveedor',
        'proveedor_adjudicado',
        'es_grupo',
        'es_pyme']
        proveedor = {k: v for k, v in AllData["ContratosE"][0].items() if k in claves_a_seleccionar}


        claves_a_seleccionar=['nombre_representante_legal',
        'identificaci_n_representante_legal']
        representante_legal = {k: v for k, v in AllData["ContratosE"][0].items() if k in claves_a_seleccionar}

        claves_a_seleccionar=['nombre_ordenador_del_gasto',
        'n_mero_de_documento_ordenador_del_gasto']
        ordenador_gasto = {k: v for k, v in AllData["ContratosE"][0].items() if k in claves_a_seleccionar}


        claves_a_seleccionar=['nombre_supervisor',
        'n_mero_de_documento_supervisor']
        supervisor = {k: v for k, v in AllData["ContratosE"][0].items() if k in claves_a_seleccionar}


        supervisor={"nombre": supervisor['nombre_supervisor'],
        "documento": supervisor['n_mero_de_documento_supervisor']}
        proveedor={"documento": proveedor['documento_proveedor'],"nombre": proveedor['proveedor_adjudicado'], "esGrupo": proveedor['es_grupo'], "esPyme": proveedor['es_pyme']}
        representante_legal={"nombre": representante_legal['nombre_representante_legal'],
        "documento": representante_legal['identificaci_n_representante_legal']}
        ordenador_gasto={"nombre": ordenador_gasto['nombre_ordenador_del_gasto'],
        "documento": ordenador_gasto['n_mero_de_documento_ordenador_del_gasto']}
        return entidad, proveedor, representante_legal, ordenador_gasto, supervisor

@app.post("/contratos/", status_code=201)
def crear_contrato(contrato: ContratoModel):
    
    try:
        # Verificar si ya existe
        existe = db(db.contratos.IdContrato == contrato.IdContrato).select().first()
        if existe:
            raise HTTPException(status_code=400, detail="El contrato ya existe")
        print(contrato.model_dump())
        id_registro = db.contratos.insert(**contrato.model_dump())
        db.commit()


        return {"message": "Contrato creado exitosamente", "id": id_registro}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/contratos/{id_contrato}")
def obtener_contrato(id_contrato: str):
    contrato = db(db.contratos.IdContrato == id_contrato).select().first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    return contrato.as_dict()

# ===== ENDPOINTS PARA ADICIONES =====
@app.post("/adiciones/", status_code=201)
def crear_adicion(adicion: AdicionModel):
    try:
        # Verificar que el contrato existe
        contrato = db(db.contratos.IdContrato == adicion.IdContrato).select().first()
        if not contrato:
            raise HTTPException(status_code=404, detail="Contrato no encontrado")
        
        # Preparar datos para inserción
        datos = adicion.model_dump()
        datos['IdContrato'] = contrato.id  # Usar el id numérico de la referencia
        
        # Verificar si ya existe una adición con el mismo IdContrato e Identificador
        adicion_existente = db(
            (db.adiciones.IdContrato == contrato.id) & 
            (db.adiciones.Identificador == adicion.Identificador)
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
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/adiciones/{id_contrato}")
def obtener_adiciones(id_contrato: str):
    contrato = db(db.contratos.IdContrato == id_contrato).select().first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    
    adiciones = db(db.adiciones.IdContrato == contrato.id).select()
    return [a.as_dict() for a in adiciones]

# ===== ENDPOINTS PARA EJECUCION =====
@app.post("/ejecucion/", status_code=201)
def crear_ejecucion(ejecucion: EjecucionModel):
    try:
        # Verificar que el contrato existe
        contrato = db(db.contratos.IdContrato == ejecucion.IdContrato).select().first()
        if not contrato:
            raise HTTPException(status_code=404, detail="Contrato no encontrado")
        
        # Preparar datos para inserción
        datos = ejecucion.model_dump()
        datos['IdContrato'] = contrato.id  # Usar el id numérico de la referencia
        
        id_registro = db.ejecucion.insert(**datos)
        db.commit()
        return {"message": "Ejecución creada exitosamente", "id": id_registro}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ejecucion/{id_contrato}")
def obtener_ejecucion(id_contrato: str):
    contrato = db(db.contratos.IdContrato == id_contrato).select().first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    
    ejecuciones = db(db.ejecucion.IdContrato == contrato.id).select()
    return [e.as_dict() for e in ejecuciones]

@app.post("/entidad/", status_code=201)
def crear_entidad(entidad: EntidadModel):
    try:
        # Verificar que el NIT no exista
        entidad_existente = db(db.entidades.nit_entidad == entidad.nit_entidad).select().first()
        
        if entidad_existente:
            raise HTTPException(
                status_code=400, 
                detail=f"Ya existe una entidad con el NIT {entidad.nit_entidad}"
            )
        
        # Insertar nueva entidad
        datos = entidad.dict()
        id_registro = db.entidades.insert(**datos)
        db.commit()
        
        return {
            "message": "Entidad creada exitosamente",
            "id": id_registro,
            "nit_entidad": entidad.nit_entidad
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
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


@app.post("/personas/", status_code=201)
def crear_persona(persona: PersonaModel):
    try:
        # Verificar que el documento no exista
        persona_existente = db(db.personas.documento == persona.documento).select().first()
        
        if persona_existente:
            raise HTTPException(
                status_code=400, 
                detail=f"Ya existe una persona con el documento {persona.documento}"
            )
        
        # Insertar nueva persona
        datos = persona.dict()
        id_registro = db.personas.insert(**datos)
        db.commit()
        
        return {
            "message": "Persona creada exitosamente",
            "id": id_registro,
            "documento": persona.documento
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
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

# ===== ENDPOINTS PARA ESTADISTICAS =====
@app.post("/estadisticas", status_code=201)
def crear_o_actualizar_estadistica(estadistica: EstadisticaModel):
    try:
        # Buscar si existe la combinación
        existe = db(
            (db.estadisticas.campo == estadistica.campo) &
            (db.estadisticas.seccion == estadistica.seccion) &
            (db.estadisticas.variable == estadistica.variable)
        ).select().first()
        
        if existe:
            # Actualizar
            existe.update_record(valor=estadistica.valor)
            existe.update_record(texto_visible=estadistica.texto_visible)
            db.commit()
            return {"message": "Estadística actualizada", "id": existe.id, "accion": "actualizar"}
        else:
            # Insertar
            id_registro = db.estadisticas.insert(**estadistica.dict())
            db.commit()
            return {"message": "Estadística creada", "id": id_registro, "accion": "crear"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/estadisticas/")
def obtener_estadisticas(campo: Optional[str] = None, 
                        seccion: Optional[str] = None,
                        
                        variable: Optional[str] = None):
    query = db.estadisticas.id > 0  # Query base
    
    if campo:
        query &= (db.estadisticas.campo == campo)
    if seccion:
        query &= (db.estadisticas.seccion == seccion)
    if variable:
        query &= (db.estadisticas.variable == variable)
    
    estadisticas = db(query).select()
    return [e.as_dict() for e in estadisticas]