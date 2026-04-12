from pydal import DAL, Field
from datetime import datetime
import os
import json
import pandas as pd
from sodapy import Socrata
import time
from models.db import db
# Configuración de la base de datos
pwd = os.path.dirname("private/experiment_config.json")

# Mapeo de nombres de columnas (original -> nombre en BD)
COLUMN_MAPPING = {
    "nombre_entidad": "nombre_entidad",
    "nit_entidad": "nit_entidad",
    "departamento": "departamento",
    "ciudad": "ciudad",
    "localizaci_n": "localizacion",
    "orden": "orden",
    "sector": "sector",
    "rama": "rama",
    "entidad_centralizada": "entidad_centralizada",
    "proceso_de_compra": "proceso_compra",
    "id_contrato": "id_contrato",
    "referencia_del_contrato": "referencia_contrato",
    "estado_contrato": "estado_contrato",
    "codigo_de_categoria_principal": "codigo_categoria_principal",
    "descripcion_del_proceso": "descripcion_proceso",
    "tipo_de_contrato": "tipo_contrato",
    "modalidad_de_contratacion": "modalidad_contratacion",
    "justificacion_modalidad_de": "justificacion_modalidad",
    "fecha_de_firma": "fecha_firma",
    "fecha_de_inicio_del_contrato": "fecha_inicio",
    "fecha_de_fin_del_contrato": "fecha_fin",
    "condiciones_de_entrega": "condiciones_entrega",
    "tipodocproveedor": "tipo_doc_proveedor",
    "documento_proveedor": "documento_proveedor",
    "proveedor_adjudicado": "proveedor_adjudicado",
    "es_grupo": "es_grupo",
    "es_pyme": "es_pyme",
    "habilita_pago_adelantado": "habilita_pago_adelantado",
    "liquidaci_n": "liquidacion",
    "obligaci_n_ambiental": "obligacion_ambiental",
    "obligaciones_postconsumo": "obligaciones_postconsumo",
    "reversion": "reversion",
    "origen_de_los_recursos": "origen_recursos",
    "destino_gasto": "destino_gasto",
    "valor_del_contrato": "valor_contrato",
    "valor_de_pago_adelantado": "valor_pago_adelantado",
    "valor_facturado": "valor_facturado",
    "valor_pendiente_de_pago": "valor_pendiente_pago",
    "valor_pagado": "valor_pagado",
    "valor_amortizado": "valor_amortizado",
    "valor_pendiente_de": "valor_pendiente_amortizacion",
    "valor_pendiente_de_ejecucion": "valor_pendiente_ejecucion",
    "estado_bpin": "estado_bpin",
    "c_digo_bpin": "codigo_bpin",
    "anno_bpin": "anno_bpin",
    "saldo_cdp": "saldo_cdp",
    "saldo_vigencia": "saldo_vigencia",
    "espostconflicto": "es_postconflicto",
    "dias_adicionados": "dias_adicionados",
    "puntos_del_acuerdo": "puntos_acuerdo",
    "pilares_del_acuerdo": "pilares_acuerdo",
    "urlproceso": "url_proceso",
    "nombre_representante_legal": "nombre_representante_legal",
    "nacionalidad_representante_legal": "nacionalidad_representante_legal",
    "domicilio_representante_legal": "domicilio_representante_legal",
    "tipo_de_identificaci_n_representante_legal": "tipo_identificacion_representante_legal",
    "identificaci_n_representante_legal": "identificacion_representante_legal",
    "g_nero_representante_legal": "genero_representante_legal",
    "presupuesto_general_de_la_nacion_pgn": "presupuesto_pgn",
    "sistema_general_de_participaciones": "sistema_participaciones",
    "sistema_general_de_regal_as": "sistema_regalias",
    "recursos_propios_alcald_as_gobernaciones_y_resguardos_ind_genas_": "recursos_propios_alcaldias",
    "recursos_de_credito": "recursos_credito",
    "recursos_propios": "recursos_propios",
    "ultima_actualizacion": "ultima_actualizacion",
    "codigo_entidad": "codigo_entidad",
    "codigo_proveedor": "codigo_proveedor",
    "fecha_inicio_liquidacion": "fecha_inicio_liquidacion",
    "fecha_fin_liquidacion": "fecha_fin_liquidacion",
    "objeto_del_contrato": "objeto_contrato",
    "duraci_n_del_contrato": "duracion_contrato",
    "nombre_del_banco": "nombre_banco",
    "tipo_de_cuenta": "tipo_cuenta",
    "n_mero_de_cuenta": "numero_cuenta",
    "el_contrato_puede_ser_prorrogado": "puede_prorrogarse",
    "nombre_ordenador_del_gasto": "nombre_ordenador_gasto",
    "tipo_de_documento_ordenador_del_gasto": "tipo_doc_ordenador_gasto",
    "n_mero_de_documento_ordenador_del_gasto": "num_doc_ordenador_gasto",
    "nombre_supervisor": "nombre_supervisor",
    "tipo_de_documento_supervisor": "tipo_doc_supervisor",
    "n_mero_de_documento_supervisor": "num_doc_supervisor",
    "nombre_ordenador_de_pago": "nombre_ordenador_pago",
    "tipo_de_documento_ordenador_de_pago": "tipo_doc_ordenador_pago",
    "n_mero_de_documento_ordenador_de_pago": "num_doc_ordenador_pago",
}


def limpiar_valor(valor):
    """
    Convierte valores 'No Definido', 'No definido', etc. a None.
    También maneja diccionarios extrayendo valores específicos.
    """
    if isinstance(valor, dict):
        # Si es un diccionario, intenta extraer el valor 'url' o devuelve None
        return valor.get("url") if "url" in valor else None

    if isinstance(valor, str):
        valores_nulos = [
            "no definido",
            "no válido",
            "sin descripcion",
            "sin descripción",
        ]
        if valor.strip().lower() in valores_nulos:
            return None

    return valor


def transformar_nombres_columnas(registro, mapeo=None):
    """
    Transforma los nombres de las columnas según el mapeo proporcionado.

    Args:
        registro (dict): Diccionario con los datos originales
        mapeo (dict): Diccionario con el mapeo de nombres (original -> nuevo)
                    Si es None, usa COLUMN_MAPPING por defecto

    Returns:
        dict: Diccionario con los nombres transformados
    """
    if mapeo is None:
        mapeo = COLUMN_MAPPING

    registro_transformado = {}

    for key_original, valor in registro.items():
        # Usa el nombre mapeado o el original si no existe en el mapeo
        key_nuevo = mapeo.get(key_original, key_original)
        registro_transformado[key_nuevo] = limpiar_valor(valor)

    return registro_transformado


def guardar_contratos(datos, tabla="contratos", mapeo=None, batch_size=100):
    """
    Guarda una lista de contratos en la base de datos.

    Args:
        datos (list): Lista de diccionarios con los datos de contratos
        tabla (str): Nombre de la tabla donde guardar
        mapeo (dict): Mapeo de nombres de columnas (opcional)
        batch_size (int): Tamaño del lote para inserciones masivas

    Returns:
        dict: Estadísticas de la operación (insertados, errores)
    """
    stats = {"insertados": 0, "errores": 0, "detalles_errores": []}

    try:
        for i, registro in enumerate(datos):
            try:
                # Transformar nombres de columnas y limpiar valores
                registro_limpio = transformar_nombres_columnas(registro, mapeo)

                # Insertar en la base de datos
                db[tabla].insert(**registro_limpio)
                stats["insertados"] += 1

            except Exception as e:
                stats["errores"] += 1
                stats["detalles_errores"].append(
                    {
                        "indice": i,
                        "error": str(e),
                        "registro": registro.get("id_contrato", "N/A"),
                    }
                )

        # Confirmar transacción
        db.commit()

    except Exception as e:
        db.rollback()
        stats["error_general"] = str(e)

    return stats


# Mapeo de nombres de columnas para adiciones (original -> nombre en BD)
ADICIONES_COLUMN_MAPPING = {
    "identificador": "id_adicion",
    "id_contrato": "id_contrato",
    "tipo": "tipo_modificacion",
    "descripcion": "descripcion",
    "fecharegistro": "fecha_registro",
}


def limpiar_valor_adicion(valor):
    """
    Convierte valores 'No Definido', 'No definido', etc. a None.
    También maneja diccionarios y otros casos especiales.

    Args:
        valor: Valor a limpiar

    Returns:
        Valor limpio o None
    """
    if isinstance(valor, dict):
        # Si es un diccionario, intenta extraer el valor 'url' o devuelve None
        return valor.get("url") if "url" in valor else None

    if isinstance(valor, str):
        valores_nulos = [
            "no definido",
            "no válido",
            "sin descripcion",
            "sin descripción",
            "n/a",
            "na",
        ]
        if valor.strip().lower() in valores_nulos:
            return None

    return valor


def transformar_nombres_columnas_adicion(registro, mapeo=None):
    """
    Transforma los nombres de las columnas según el mapeo proporcionado.

    Args:
        registro (dict): Diccionario con los datos originales
        mapeo (dict): Diccionario con el mapeo de nombres (original -> nuevo)
                    Si es None, usa ADICIONES_COLUMN_MAPPING por defecto

    Returns:
        dict: Diccionario con los nombres transformados y valores limpios
    """
    if mapeo is None:
        mapeo = ADICIONES_COLUMN_MAPPING

    registro_transformado = {}

    for key_original, valor in registro.items():
        # Usa el nombre mapeado o el original si no existe en el mapeo
        key_nuevo = mapeo.get(key_original, key_original)
        registro_transformado[key_nuevo] = limpiar_valor_adicion(valor)

    return registro_transformado


def guardar_adiciones(
    datos, tabla="adiciones", mapeo=None, actualizar_existentes=False
):
    """
    Guarda una lista de adiciones/modificaciones en la base de datos.

    Args:
        datos (list): Lista de diccionarios con los datos de adiciones
        tabla (str): Nombre de la tabla donde guardar (default: 'adiciones')
        mapeo (dict): Mapeo de nombres de columnas (opcional)
        actualizar_existentes (bool): Si True, actualiza registros existentes en lugar de fallar

    Returns:
        dict: Estadísticas de la operación (insertados, actualizados, errores)
    """
    stats = {"insertados": 0, "actualizados": 0, "errores": 0, "detalles_errores": []}

    try:
        for i, registro in enumerate(datos):
            try:
                # Transformar nombres de columnas y limpiar valores
                registro_limpio = transformar_nombres_columnas_adicion(registro, mapeo)

                # Verificar si el registro ya existe (por id_adicion)
                id_adicion = registro_limpio.get("id_adicion")

                if actualizar_existentes and id_adicion:
                    # Buscar registro existente
                    existe = db(db[tabla].id_adicion == id_adicion).select().first()

                    if existe:
                        # Actualizar registro existente
                        db(db[tabla].id_adicion == id_adicion).update(**registro_limpio)
                        stats["actualizados"] += 1
                    else:
                        # Insertar nuevo registro
                        db[tabla].insert(**registro_limpio)
                        stats["insertados"] += 1
                else:
                    # Insertar en la base de datos
                    db[tabla].insert(**registro_limpio)
                    stats["insertados"] += 1

            except Exception as e:
                stats["errores"] += 1
                stats["detalles_errores"].append(
                    {
                        "indice": i,
                        "error": str(e),
                        "registro": registro.get("identificador", "N/A"),
                    }
                )

        # Confirmar transacción
        db.commit()

    except Exception as e:
        db.rollback()
        stats["error_general"] = str(e)

    return stats


# def obtener_adiciones_por_contrato(id_contrato, tabla='adiciones'):
#     """
#     Obtiene todas las adiciones/modificaciones de un contrato específico.

#     Args:
#         id_contrato (str): ID del contrato
#         tabla (str): Nombre de la tabla

#     Returns:
#         list: Lista de registros de adiciones
#     """
#     adiciones = db(db[tabla].id_contrato == id_contrato).select(
#         orderby=db[tabla].fecha_registro
#     )
#     return adiciones.as_list()


# def obtener_adiciones_por_tipo(tipo_modificacion, tabla='adiciones'):
#     """
#     Obtiene todas las adiciones/modificaciones de un tipo específico.

#     Args:
#         tipo_modificacion (str): Tipo de modificación
#         tabla (str): Nombre de la tabla

#     Returns:
#         list: Lista de registros de adiciones
#     """
#     adiciones = db(db[tabla].tipo_modificacion == tipo_modificacion).select(
#         orderby=db[tabla].fecha_registro
#     )
#     return adiciones.as_list()


# def estadisticas_adiciones(tabla='adiciones'):
#     """
#     Genera estadísticas sobre las adiciones en la base de datos.

#     Args:
#         tabla (str): Nombre de la tabla

#     Returns:
#         dict: Diccionario con estadísticas
#     """
#     total = db(db[tabla]).count()

#     # Contar por tipo
#     tipos = db(db[tabla]).select(
#         db[tabla].tipo_modificacion,
#         db[tabla].id_adicion.count(),
#         groupby=db[tabla].tipo_modificacion
#     )

#     tipos_dict = {row[db[tabla]].tipo_modificacion: row[db[tabla].id_adicion.count()]
#                   for row in tipos}

#     return {
#         'total_adiciones': total,
#         'por_tipo': tipos_dict
#     }

# Mapeo de nombres de columnas para ejecuciones (original -> nombre en BD)
EJECUCIONES_COLUMN_MAPPING = {
    "identificadorcontrato": "id_contrato",
    "tipoejecucion": "tipo_ejecucion",
    "nombreplan": "nombre_plan",
    "fechadeentregaesperada": "fecha_entrega_esperada",
    "porcentajedeavanceesperado": "porcentaje_avance_esperado",
    "fechadeentregareal": "fecha_entrega_real",
    "porcentaje_de_avance_real": "porcentaje_avance_real",
    "estado_del_contrato": "estado_contrato",
    "referencia_de_articulos": "referencia_articulos",
    "descripci_n": "descripcion",
    "unidad": "unidad",
    "cantidad_adjudicada": "cantidad_adjudicada",
    "cantidad_planeada": "cantidad_planeada",
    "cantidadrecibida": "cantidad_recibida",
    "cantidadporrecibir": "cantidad_por_recibir",
    "fechacreacion": "fecha_creacion",
}


def limpiar_valor_ejecucion(valor):
    """
    Convierte valores 'No Definido', 'No definido', etc. a None.
    También maneja valores numéricos con formatos especiales.

    Args:
        valor: Valor a limpiar

    Returns:
        Valor limpio o None
    """
    if isinstance(valor, dict):
        # Si es un diccionario, intenta extraer el valor 'url' o devuelve None
        return valor.get("url") if "url" in valor else None

    if isinstance(valor, str):
        # Limpiar espacios
        valor_limpio = valor.strip()

        # Valores considerados nulos
        valores_nulos = [
            "no definido",
            "no válido",
            "sin descripcion",
            "sin descripción",
            "n/a",
            "na",
        ]

        if valor_limpio.lower() in valores_nulos:
            return None

        # Manejar valores numéricos mal formateados como '.000000'
        if valor_limpio.startswith(".") and all(c in "0." for c in valor_limpio):
            return "0"

    return valor


def transformar_nombres_columnas_ejecucion(registro, mapeo=None):
    """
    Transforma los nombres de las columnas según el mapeo proporcionado.

    Args:
        registro (dict): Diccionario con los datos originales
        mapeo (dict): Diccionario con el mapeo de nombres (original -> nuevo)
                    Si es None, usa EJECUCIONES_COLUMN_MAPPING por defecto

    Returns:
        dict: Diccionario con los nombres transformados y valores limpios
    """
    if mapeo is None:
        mapeo = EJECUCIONES_COLUMN_MAPPING

    registro_transformado = {}

    for key_original, valor in registro.items():
        # Usa el nombre mapeado o el original si no existe en el mapeo
        key_nuevo = mapeo.get(key_original, key_original)
        registro_transformado[key_nuevo] = limpiar_valor_ejecucion(valor)

    return registro_transformado


def guardar_ejecuciones(datos, tabla="ejecuciones", mapeo=None, batch_size=100):
    """
    Guarda una lista de ejecuciones de contratos en la base de datos.

    Args:
        datos (list): Lista de diccionarios con los datos de ejecuciones
        tabla (str): Nombre de la tabla donde guardar (default: 'ejecuciones')
        mapeo (dict): Mapeo de nombres de columnas (opcional)
        batch_size (int): Tamaño del lote para inserciones masivas

    Returns:
        dict: Estadísticas de la operación (insertados, errores)
    """
    stats = {"insertados": 0, "errores": 0, "detalles_errores": []}

    try:
        for i, registro in enumerate(datos):
            try:
                # Transformar nombres de columnas y limpiar valores
                registro_limpio = transformar_nombres_columnas_ejecucion(
                    registro, mapeo
                )

                # Insertar en la base de datos
                db[tabla].insert(**registro_limpio)
                stats["insertados"] += 1

                # Commit cada batch_size registros para mejorar rendimiento
                if (i + 1) % batch_size == 0:
                    db.commit()

            except Exception as e:
                stats["errores"] += 1
                stats["detalles_errores"].append(
                    {
                        "indice": i,
                        "error": str(e),
                        "registro": registro.get("identificadorcontrato", "N/A"),
                    }
                )

        # Confirmar transacción final
        db.commit()

    except Exception as e:
        db.rollback()
        stats["error_general"] = str(e)

    return stats


# def obtener_ejecuciones_por_contrato(id_contrato, tabla='ejecuciones'):
#     """
#     Obtiene todas las ejecuciones de un contrato específico.

#     Args:
#         id_contrato (str): ID del contrato
#         tabla (str): Nombre de la tabla

#     Returns:
#         list: Lista de registros de ejecuciones
#     """
#     ejecuciones = db(db[tabla].id_contrato == id_contrato).select(
#         orderby=db[tabla].fecha_creacion
#     )
#     return ejecuciones.as_list()


# def obtener_ejecuciones_por_estado(estado, tabla='ejecuciones'):
#     """
#     Obtiene todas las ejecuciones con un estado específico.

#     Args:
#         estado (str): Estado del contrato
#         tabla (str): Nombre de la tabla

#     Returns:
#         list: Lista de registros de ejecuciones
#     """
#     ejecuciones = db(db[tabla].estado_contrato == estado).select(
#         orderby=db[tabla].fecha_creacion
#     )
#     return ejecuciones.as_list()


# def obtener_ejecuciones_por_tipo(tipo_ejecucion, tabla='ejecuciones'):
#     """
#     Obtiene todas las ejecuciones de un tipo específico.

#     Args:
#         tipo_ejecucion (str): Tipo de ejecución (ej: 'PORCENTAJE', 'CANTIDAD')
#         tabla (str): Nombre de la tabla

#     Returns:
#         list: Lista de registros de ejecuciones
#     """
#     ejecuciones = db(db[tabla].tipo_ejecucion == tipo_ejecucion).select(
#         orderby=db[tabla].fecha_creacion
#     )
#     return ejecuciones.as_list()


# def calcular_avance_contrato(id_contrato, tabla='ejecuciones'):
#     """
#     Calcula el avance promedio de un contrato basado en sus ejecuciones.

#     Args:
#         id_contrato (str): ID del contrato
#         tabla (str): Nombre de la tabla

#     Returns:
#         dict: Diccionario con información de avance
#     """
#     ejecuciones = db(db[tabla].id_contrato == id_contrato).select()

#     if not ejecuciones:
#         return {
#             'id_contrato': id_contrato,
#             'total_ejecuciones': 0,
#             'avance_esperado_promedio': 0,
#             'avance_real_promedio': 0,
#             'diferencia': 0
#         }

#     avance_esperado = sum(float(e.porcentaje_avance_esperado or 0) for e in ejecuciones)
#     avance_real = sum(float(e.porcentaje_avance_real or 0) for e in ejecuciones)
#     total = len(ejecuciones)

#     return {
#         'id_contrato': id_contrato,
#         'total_ejecuciones': total,
#         'avance_esperado_promedio': avance_esperado / total if total > 0 else 0,
#         'avance_real_promedio': avance_real / total if total > 0 else 0,
#         'diferencia': (avance_real - avance_esperado) / total if total > 0 else 0
#     }


# def estadisticas_ejecuciones(tabla='ejecuciones'):
#     """
#     Genera estadísticas sobre las ejecuciones en la base de datos.

#     Args:
#         tabla (str): Nombre de la tabla

#     Returns:
#         dict: Diccionario con estadísticas
#     """
#     total = db(db[tabla]).count()

#     # Contar por estado
#     estados = db(db[tabla]).select(
#         db[tabla].estado_contrato,
#         db[tabla].id.count(),
#         groupby=db[tabla].estado_contrato
#     )

#     estados_dict = {row[db[tabla]].estado_contrato: row[db[tabla].id.count()]
#                     for row in estados}

#     # Contar por tipo de ejecución
#     tipos = db(db[tabla]).select(
#         db[tabla].tipo_ejecucion,
#         db[tabla].id.count(),
#         groupby=db[tabla].tipo_ejecucion
#     )

#     tipos_dict = {row[db[tabla]].tipo_ejecucion: row[db[tabla].id.count()]
#                   for row in tipos}

#     return {
#         'total_ejecuciones': total,
#         'por_estado': estados_dict,
#         'por_tipo': tipos_dict
#     }


# def obtener_ejecuciones_atrasadas(tabla='ejecuciones'):
#     """
#     Obtiene ejecuciones donde el avance real es menor al esperado.

#     Args:
#         tabla (str): Nombre de la tabla

#     Returns:
#         list: Lista de ejecuciones atrasadas
#     """
#     ejecuciones = db(
#         (db[tabla].porcentaje_avance_real < db[tabla].porcentaje_avance_esperado) &
#         (db[tabla].estado_contrato != 'Terminado')
#     ).select(orderby=~(db[tabla].porcentaje_avance_esperado - db[tabla].porcentaje_avance_real))

#     return ejecuciones.as_list()

# ============================================================================
# MAPEOS DE COLUMNAS
# ============================================================================

ENTIDADES_MAPPING = {
    "nit_entidad": "nit_entidad",
    "nombre_entidad": "nombre_entidad",
    "departamento": "departamento",
    "ciudad": "ciudad",
    "orden": "orden",
    "sector": "sector",
    "rama": "rama",
    "entidad_centralizada": "entidad_centralizada",
}

# ============================================================================
# FUNCIONES DE LIMPIEZA
# ============================================================================

# def limpiar_valor(valor):
#     """
#     Convierte valores 'No Definido', 'No definido', etc. a None.
#     """
#     if isinstance(valor, dict):
#         return valor.get('url') if 'url' in valor else None

#     if isinstance(valor, str):
#         valores_nulos = [
#             'no definido',
#             'no válido',
#             'sin descripcion',
#             'sin descripción',
#             'n/a',
#             'na',
#             'no d'
#         ]
#         if valor.strip().lower() in valores_nulos:
#             return None

#     return valor


def convertir_si_no_a_bool(valor):
    """
    Convierte 'Si'/'No' a valores string o None.
    """
    if isinstance(valor, str):
        valor_limpio = valor.strip().lower()
        if valor_limpio == "si" or valor_limpio == "sí":
            return "Si"
        elif valor_limpio == "no":
            return "No"
    return None


# ============================================================================
# FUNCIONES PARA ENTIDADES
# ============================================================================


def guardar_entidad(datos_contrato):
    """
    Guarda o actualiza una entidad desde los datos de un contrato.

    Args:
        datos_contrato (dict): Diccionario con los datos del contrato

    Returns:
        dict: Resultado de la operación
    """
    resultado = {"exito": False, "accion": None, "mensaje": ""}

    try:
        nit = limpiar_valor(datos_contrato.get("nit_entidad"))

        if not nit:
            resultado["mensaje"] = "NIT de entidad no válido"
            return resultado

        # Preparar datos de la entidad
        datos_entidad = {
            "nit_entidad": nit,
            "nombre_entidad": limpiar_valor(datos_contrato.get("nombre_entidad")),
            "departamento": limpiar_valor(datos_contrato.get("departamento")),
            "ciudad": limpiar_valor(datos_contrato.get("ciudad")),
            "orden": limpiar_valor(datos_contrato.get("orden")),
            "sector": limpiar_valor(datos_contrato.get("sector")),
            "rama": limpiar_valor(datos_contrato.get("rama")),
            "entidad_centralizada": limpiar_valor(
                datos_contrato.get("entidad_centralizada")
            ),
        }

        # Verificar si la entidad ya existe
        entidad_existente = db(db.entidades.nit_entidad == nit).select().first()

        if entidad_existente:
            # Actualizar solo si hay nuevos datos
            db(db.entidades.nit_entidad == nit).update(**datos_entidad)
            resultado["exito"] = True
            resultado["accion"] = "actualizado"
            resultado["mensaje"] = f"Entidad {nit} actualizada"
        else:
            # Insertar nueva entidad
            db.entidades.insert(**datos_entidad)
            resultado["exito"] = True
            resultado["accion"] = "insertado"
            resultado["mensaje"] = f"Entidad {nit} creada"

        db.commit()

    except Exception as e:
        db.rollback()
        resultado["mensaje"] = f"Error: {str(e)}"

    return resultado


# ============================================================================
# FUNCIONES PARA PROVEEDORES Y PERSONAS
# ============================================================================


def guardar_proveedor_o_persona(documento, nombre, tipo, es_grupo=None, es_pyme=None):
    """
    Guarda o actualiza un proveedor o persona.

    Args:
        documento (str): Documento de identidad
        nombre (str): Nombre de la persona/entidad
        tipo (str): Tipo (proveedor, representante_legal, etc.)
        es_grupo (str): 'Si' o 'No', opcional
        es_pyme (str): 'Si' o 'No', opcional

    Returns:
        dict: Resultado de la operación
    """
    resultado = {"exito": False, "accion": None, "mensaje": ""}

    try:
        documento_limpio = limpiar_valor(documento)
        nombre_limpio = limpiar_valor(nombre)

        if not documento_limpio:
            resultado["mensaje"] = "Documento no válido"
            return resultado

        if not nombre_limpio:
            resultado["mensaje"] = "Nombre no válido"
            return resultado

        # Limpiar es_grupo y es_pyme
        es_grupo_limpio = convertir_si_no_a_bool(es_grupo) if es_grupo else None
        es_pyme_limpio = convertir_si_no_a_bool(es_pyme) if es_pyme else None

        # Verificar si ya existe
        persona_existente = (
            db(db.proveedoresypersonas.documento == documento_limpio).select().first()
        )

        if persona_existente:
            # Verificar si el nuevo nombre es más largo
            nombre_actual = persona_existente.nombre or ""
            nombre_nuevo = nombre_limpio

            actualizar = False
            datos_actualizacion = {}

            # Solo actualizar nombre si el nuevo es más largo
            if len(nombre_nuevo) > len(nombre_actual):
                datos_actualizacion["nombre"] = nombre_nuevo
                actualizar = True

            # Actualizar es_grupo si se proporciona y no existe
            if es_grupo_limpio and not persona_existente.es_grupo:
                datos_actualizacion["es_grupo"] = es_grupo_limpio
                actualizar = True

            # Actualizar es_pyme si se proporciona y no existe
            if es_pyme_limpio and not persona_existente.es_pyme:
                datos_actualizacion["es_pyme"] = es_pyme_limpio
                actualizar = True

            # Actualizar tipo si no existe o agregar el nuevo tipo
            if tipo and tipo not in (persona_existente.tipo or ""):
                tipo_actual = persona_existente.tipo or ""
                if tipo_actual:
                    datos_actualizacion["tipo"] = f"{tipo_actual},{tipo}"
                else:
                    datos_actualizacion["tipo"] = tipo
                actualizar = True

            if actualizar:
                db(db.proveedoresypersonas.documento == documento_limpio).update(
                    **datos_actualizacion
                )
                resultado["exito"] = True
                resultado["accion"] = "actualizado"
                resultado["mensaje"] = f"Persona {documento_limpio} actualizada"
            else:
                resultado["exito"] = True
                resultado["accion"] = "sin_cambios"
                resultado["mensaje"] = (
                    f"Persona {documento_limpio} sin cambios necesarios"
                )
        else:
            # Insertar nueva persona
            db.proveedoresypersonas.insert(
                documento=documento_limpio,
                nombre=nombre_limpio,
                es_grupo=es_grupo_limpio,
                es_pyme=es_pyme_limpio,
                tipo=tipo,
            )
            resultado["exito"] = True
            resultado["accion"] = "insertado"
            resultado["mensaje"] = f"Persona {documento_limpio} creada"

        db.commit()

    except Exception as e:
        db.rollback()
        resultado["mensaje"] = f"Error: {str(e)}"

    return resultado


def procesar_personas_del_contrato(datos_contrato):
    """
    Procesa y guarda todas las personas relacionadas con un contrato.

    Args:
        datos_contrato (dict): Diccionario con los datos del contrato

    Returns:
        dict: Resultados de todas las operaciones
    """
    resultados = {
        "proveedor": None,
        "representante_legal": None,
        "ordenador_gasto": None,
        "supervisor": None,
        "ordenador_pago": None,
    }

    # Proveedor
    doc_proveedor = datos_contrato.get("documento_proveedor")
    nombre_proveedor = datos_contrato.get("proveedor_adjudicado")
    es_grupo = datos_contrato.get("es_grupo")
    es_pyme = datos_contrato.get("es_pyme")

    if doc_proveedor and nombre_proveedor:
        resultados["proveedor"] = guardar_proveedor_o_persona(
            doc_proveedor, nombre_proveedor, "proveedor", es_grupo, es_pyme
        )

    # Representante legal
    doc_repr = datos_contrato.get("identificaci_n_representante_legal")
    nombre_repr = datos_contrato.get("nombre_representante_legal")

    if doc_repr and nombre_repr:
        resultados["representante_legal"] = guardar_proveedor_o_persona(
            doc_repr, nombre_repr, "representante_legal"
        )

    # Ordenador del gasto
    doc_ord_gasto = datos_contrato.get("n_mero_de_documento_ordenador_del_gasto")
    nombre_ord_gasto = datos_contrato.get("nombre_ordenador_del_gasto")

    if doc_ord_gasto and nombre_ord_gasto:
        resultados["ordenador_gasto"] = guardar_proveedor_o_persona(
            doc_ord_gasto, nombre_ord_gasto, "ordenador_del_gasto"
        )

    # Supervisor
    doc_supervisor = datos_contrato.get("n_mero_de_documento_supervisor")
    nombre_supervisor = datos_contrato.get("nombre_supervisor")

    if doc_supervisor and nombre_supervisor:
        resultados["supervisor"] = guardar_proveedor_o_persona(
            doc_supervisor, nombre_supervisor, "supervisor"
        )

    # Ordenador de pago
    doc_ord_pago = datos_contrato.get("n_mero_de_documento_ordenador_de_pago")
    nombre_ord_pago = datos_contrato.get("nombre_ordenador_de_pago")

    if doc_ord_pago and nombre_ord_pago:
        resultados["ordenador_pago"] = guardar_proveedor_o_persona(
            doc_ord_pago, nombre_ord_pago, "ordenador_de_pago"
        )

    return resultados


# ============================================================================
# FUNCIÓN PRINCIPAL DE PROCESAMIENTO
# ============================================================================


def procesar_contrato_completo(datos_contrato):
    """
    Procesa un contrato completo: entidad, proveedores y personas.

    Args:
        datos_contrato (dict): Diccionario con todos los datos del contrato

    Returns:
        dict: Resumen de todas las operaciones
    """
    resumen = {"entidad": None, "personas": None}

    # Guardar entidad
    resumen["entidad"] = guardar_entidad(datos_contrato)

    # Guardar personas
    resumen["personas"] = procesar_personas_del_contrato(datos_contrato)

    return resumen


# ============================================================================
# FUNCIONES DE CONSULTA
# ============================================================================

# def obtener_entidad(nit):
#     """Obtiene una entidad por su NIT."""
#     return db(db.entidades.nit_entidad == nit).select().first()


# def obtener_persona(documento):
#     """Obtiene una persona por su documento."""
#     return db(db.proveedoresypersonas.documento == documento).select().first()


# def obtener_personas_por_tipo(tipo):
#     """Obtiene todas las personas de un tipo específico."""
#     return db(db.proveedoresypersonas.tipo.contains(tipo)).select()


# def estadisticas_entidades():
#     """Genera estadísticas de entidades."""
#     total = db(db.entidades).count()

#     por_sector = db(db.entidades).select(
#         db.entidades.sector,
#         db.entidades.nit_entidad.count(),
#         groupby=db.entidades.sector
#     )

#     return {
#         'total': total,
#         'por_sector': {row[db.entidades].sector: row[db.entidades.nit_entidad.count()]
#                     for row in por_sector if row[db.entidades].sector}
#     }


# def estadisticas_personas():
#     """Genera estadísticas de personas."""
#     total = db(db.proveedoresypersonas).count()

#     proveedores = db(db.proveedoresypersonas.tipo.contains('proveedor')).count()
#     representantes = db(db.proveedoresypersonas.tipo.contains('representante_legal')).count()
#     supervisores = db(db.proveedoresypersonas.tipo.contains('supervisor')).count()

#     return {
#         'total': total,
#         'proveedores': proveedores,
#         'representantes_legales': representantes,
#         'supervisores': supervisores
#     }


# ============================================================================
# FUNCIONES DE LIMPIEZA Y NORMALIZACIÓN
# ============================================================================

# def limpiar_valor(valor):
#     """
#     Convierte valores 'No Definido', vacíos, etc. a None.
#     """
#     if isinstance(valor, str):
#         valor_limpio = valor.strip()

#         valores_nulos = [
#             'no definido',
#             'no válido',
#             'sin descripcion',
#             'sin descripción',
#             'n/a',
#             'na',
#             ''
#         ]

#         if valor_limpio.lower() in valores_nulos or not valor_limpio:
#             return None

#         return valor_limpio

#     return valor


def normalizar_documento(documento):
    """
    Normaliza un documento eliminando espacios y caracteres innecesarios.
    """
    if not documento:
        return None

    doc_limpio = str(documento).strip().replace(" ", "")
    return doc_limpio if doc_limpio else None


def parsear_fecha(fecha_str):
    """
    Parsea una fecha en diferentes formatos.
    Soporta: DD/MM/YYYY, YYYY-MM-DD, YYYY-MM-DDTHH:MM:SS.fff
    """
    if not fecha_str:
        return None

    fecha_limpia = limpiar_valor(fecha_str)
    if not fecha_limpia:
        return None

    # Formatos comunes
    formatos = ["%d/%m/%Y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"]

    for formato in formatos:
        try:
            return datetime.strptime(fecha_limpia, formato).date()
        except ValueError:
            continue

    return None


# ============================================================================
# FUNCIONES PARA SANCIONADOS SIRI
# ============================================================================


def extraer_datos_siri(datos_siri):
    """
    Extrae los campos relevantes de un registro SIRI.

    Args:
        datos_siri (dict): Diccionario con datos del SIRI

    Returns:
        dict: Datos normalizados
    """
    documento = normalizar_documento(datos_siri.get("numero_identificacion"))

    if not documento:
        return None

    # Construir nombre completo para comparación
    primer_nombre = limpiar_valor(datos_siri.get("primer_nombre"))
    segundo_nombre = limpiar_valor(datos_siri.get("segundo_nombre"))
    primer_apellido = limpiar_valor(datos_siri.get("primer_apellido"))
    segundo_apellido = limpiar_valor(datos_siri.get("segundo_apellido"))

    return {
        "documento": documento,
        "tipo_inhabilitacion": limpiar_valor(datos_siri.get("tipo_inhabilidad")),
        "primer_nombre": primer_nombre,
        "segundo_nombre": segundo_nombre,
        "primer_apellido": primer_apellido,
        "segundo_apellido": segundo_apellido,
        "nombre_completo": None,
        "sancion": limpiar_valor(datos_siri.get("sanciones")),
        "fecha_efectos_juridicos": parsear_fecha(
            datos_siri.get("fecha_efectos_juridicos")
        ),
        "numero_resolucion": None,
        "origen": "SIRI",
    }


# ============================================================================
# FUNCIONES PARA AMONESTADOS SECOP
# ============================================================================


def extraer_datos_secop(datos_secop):
    """
    Extrae los campos relevantes de un registro SECOP.

    Args:
        datos_secop (dict): Diccionario con datos del SECOP

    Returns:
        dict: Datos normalizados
    """
    documento = normalizar_documento(datos_secop.get("documento_contratista"))

    if not documento:
        return None

    return {
        "documento": documento,
        "tipo_inhabilitacion": "AMONESTACION",  # Tipo fijo para SECOP
        "primer_nombre": None,
        "segundo_nombre": None,
        "primer_apellido": None,
        "segundo_apellido": None,
        "nombre_completo": limpiar_valor(datos_secop.get("nombre_contratista")),
        "sancion": None,
        "fecha_efectos_juridicos": parsear_fecha(datos_secop.get("fecha_de_firmeza")),
        "numero_resolucion": limpiar_valor(datos_secop.get("numero_de_resolucion")),
        "origen": "SECOP",
    }


# ============================================================================
# FUNCIÓN PRINCIPAL DE GUARDADO
# ============================================================================


def verificar_registro_diferente(documento, nuevos_datos):
    """
    Verifica si el nuevo registro tiene al menos un campo diferente
    a los registros existentes para el mismo documento.

    Args:
        documento (str): Número de documento
        nuevos_datos (dict): Nuevos datos a comparar

    Returns:
        bool: True si hay diferencias, False si es duplicado
    """
    registros_existentes = db(db.sancionados.documento == documento).select()

    if not registros_existentes:
        return True  # No hay registros, es nuevo

    # Campos a comparar (excluyendo id, documento y origen)
    campos_comparar = [
        "tipo_inhabilitacion",
        "primer_nombre",
        "segundo_nombre",
        "primer_apellido",
        "segundo_apellido",
        "nombre_completo",
        "sancion",
        "fecha_efectos_juridicos",
        "numero_resolucion",
    ]

    for registro in registros_existentes:
        es_igual = True

        for campo in campos_comparar:
            valor_existente = getattr(registro, campo)
            valor_nuevo = nuevos_datos.get(campo)

            # Normalizar None y strings vacíos
            if valor_existente == "" or valor_existente is None:
                valor_existente = None
            if valor_nuevo == "" or valor_nuevo is None:
                valor_nuevo = None

            # Si encuentra alguna diferencia, el registro es diferente
            if valor_existente != valor_nuevo:
                es_igual = False
                break

        # Si encontró un registro idéntico, no insertar
        if es_igual:
            return False

    # No se encontró ningún registro idéntico
    return True


def guardar_sancionado(datos_normalizados):
    """
    Guarda un registro de sancionado/amonestado si es diferente.

    Args:
        datos_normalizados (dict): Datos ya normalizados

    Returns:
        dict: Resultado de la operación
    """
    resultado = {"exito": False, "accion": None, "mensaje": ""}

    try:
        documento = datos_normalizados.get("documento")

        if not documento:
            resultado["mensaje"] = "Documento no válido"
            return resultado

        # Verificar si el registro es diferente
        if verificar_registro_diferente(documento, datos_normalizados):
            # Insertar nuevo registro
            db.sancionados.insert(**datos_normalizados)
            db.commit()

            resultado["exito"] = True
            resultado["accion"] = "insertado"
            resultado["mensaje"] = f"Sanción registrada para documento {documento}"
        else:
            resultado["exito"] = True
            resultado["accion"] = "duplicado"
            resultado["mensaje"] = (
                f"Registro duplicado para documento {documento}, no se insertó"
            )

    except Exception as e:
        db.rollback()
        resultado["mensaje"] = f"Error: {str(e)}"

    return resultado


def guardar_sancionado_siri(datos_siri):
    """
    Procesa y guarda un registro del SIRI.

    Args:
        datos_siri (dict): Diccionario con datos originales del SIRI

    Returns:
        dict: Resultado de la operación
    """
    datos_normalizados = extraer_datos_siri(datos_siri)

    if not datos_normalizados:
        return {
            "exito": False,
            "accion": None,
            "mensaje": "No se pudieron extraer datos válidos del SIRI",
        }

    return guardar_sancionado(datos_normalizados)


def guardar_amonestado_secop(datos_secop):
    """
    Procesa y guarda un registro de SECOP.

    Args:
        datos_secop (dict): Diccionario con datos originales del SECOP

    Returns:
        dict: Resultado de la operación
    """
    datos_normalizados = extraer_datos_secop(datos_secop)

    if not datos_normalizados:
        return {
            "exito": False,
            "accion": None,
            "mensaje": "No se pudieron extraer datos válidos del SECOP",
        }

    return guardar_sancionado(datos_normalizados)


# ============================================================================
# FUNCIONES DE PROCESAMIENTO MASIVO
# ============================================================================


def procesar_multiples_siri(lista_siri):
    """
    Procesa múltiples registros del SIRI.

    Args:
        lista_siri (list): Lista de diccionarios con datos del SIRI

    Returns:
        dict: Estadísticas del procesamiento
    """
    stats = {
        "total_procesados": 0,
        "insertados": 0,
        "duplicados": 0,
        "errores": 0,
        "detalles_errores": [],
    }

    for i, registro in enumerate(lista_siri):
        try:
            resultado = guardar_sancionado_siri(registro)
            stats["total_procesados"] += 1

            if resultado["exito"]:
                if resultado["accion"] == "insertado":
                    stats["insertados"] += 1
                elif resultado["accion"] == "duplicado":
                    stats["duplicados"] += 1
            else:
                stats["errores"] += 1
                stats["detalles_errores"].append(
                    {
                        "indice": i,
                        "documento": registro.get("numero_identificacion", "N/A"),
                        "error": resultado["mensaje"],
                    }
                )

        except Exception as e:
            stats["errores"] += 1
            stats["detalles_errores"].append({"indice": i, "error": str(e)})

    return stats


def procesar_multiples_secop(lista_secop):
    """
    Procesa múltiples registros de SECOP.

    Args:
        lista_secop (list): Lista de diccionarios con datos del SECOP

    Returns:
        dict: Estadísticas del procesamiento
    """
    stats = {
        "total_procesados": 0,
        "insertados": 0,
        "duplicados": 0,
        "errores": 0,
        "detalles_errores": [],
    }

    for i, registro in enumerate(lista_secop):
        try:
            resultado = guardar_amonestado_secop(registro)
            stats["total_procesados"] += 1

            if resultado["exito"]:
                if resultado["accion"] == "insertado":
                    stats["insertados"] += 1
                elif resultado["accion"] == "duplicado":
                    stats["duplicados"] += 1
            else:
                stats["errores"] += 1
                stats["detalles_errores"].append(
                    {
                        "indice": i,
                        "documento": registro.get("documento_contratista", "N/A"),
                        "error": resultado["mensaje"],
                    }
                )

        except Exception as e:
            stats["errores"] += 1
            stats["detalles_errores"].append({"indice": i, "error": str(e)})

    return stats


# ============================================================================
# FUNCIONES DE CONSULTA
# ============================================================================

# def obtener_sanciones_por_documento(documento):
#     """
#     Obtiene todas las sanciones de un documento.

#     Args:
#         documento (str): Número de documento

#     Returns:
#         list: Lista de sanciones
#     """
#     doc_normalizado = normalizar_documento(documento)
#     return db(db.sancionados.documento == doc_normalizado).select(
#         orderby=db.sancionados.fecha_efectos_juridicos
#     ).as_list()


# def obtener_sancionados_por_tipo(tipo_inhabilitacion):
#     """
#     Obtiene sancionados por tipo de inhabilitación.

#     Args:
#         tipo_inhabilitacion (str): Tipo de inhabilitación

#     Returns:
#         list: Lista de sancionados
#     """
#     return db(db.sancionados.tipo_inhabilitacion == tipo_inhabilitacion).select(
#         orderby=db.sancionados.fecha_efectos_juridicos
#     ).as_list()


# def obtener_sancionados_por_origen(origen):
#     """
#     Obtiene sancionados por origen (SIRI o SECOP).

#     Args:
#         origen (str): 'SIRI' o 'SECOP'

#     Returns:
#         list: Lista de sancionados
#     """
#     return db(db.sancionados.origen == origen).select(
#         orderby=db.sancionados.fecha_efectos_juridicos
#     ).as_list()


# def estadisticas_sancionados():
#     """
#     Genera estadísticas de sancionados.

#     Returns:
#         dict: Diccionario con estadísticas
#     """
#     total = db(db.sancionados).count()

#     por_tipo = db(db.sancionados).select(
#         db.sancionados.tipo_inhabilitacion,
#         db.sancionados.id.count(),
#         groupby=db.sancionados.tipo_inhabilitacion
#     )

#     por_origen = db(db.sancionados).select(
#         db.sancionados.origen,
#         db.sancionados.id.count(),
#         groupby=db.sancionados.origen
#     )

#     return {
#         'total': total,
#         'por_tipo': {row[db.sancionados].tipo_inhabilitacion: row[db.sancionados.id.count()]
#                      for row in por_tipo if row[db.sancionados].tipo_inhabilitacion},
#         'por_origen': {row[db.sancionados].origen: row[db.sancionados.id.count()]
#                        for row in por_origen if row[db.sancionados].origen}
#     }


def extractConfig(
    nameModel="SystemData",
    relPath=os.path.join(pwd, "experiment_config.json"),
    dataOut="keyantrophics",
):
    configPath = os.path.join(os.getcwd(), relPath)
    with open(configPath, "r", encoding="utf-8") as file:
        config = json.load(file)[nameModel]
        Output = config[dataOut]
    return Output


if __name__ == "__main__":
    print("iniciando")
    claveApiSocrata = extractConfig(nameModel="SocratesApi", dataOut="claveAppApi")

    # Unauthenticated client only works with public data sets.
    client = Socrata("www.datos.gov.co", claveApiSocrata)
    print("client", client)

    SancionesSecopI = "4n4q-k399"
    AntededentesSiri = "iaeu-rcn6"
    ContratosSecopII = "jbjy-vk9h"
    AdicionesSecopII = "cb9c-h8sn"
    EjecucionesSecopII = "mfmm-jqmq"

    reloj = time.time()
    print("Iniciando sincronización por lotes...")

    # ==========================================
    # 1. Sincronizar Sanciones SECOP I
    # ==========================================
    t = 0
    for item in client.get_all(SancionesSecopI):
        guardar_amonestado_secop(item)
        t += 1
        if t % 500 == 0:
            db.commit()
    db.commit()
    print("fin sanciones")
    # ==========================================
    # 2. Sincronizar Antecedentes SIRI
    # ==========================================
    t = 0
    for item in client.get_all(AntededentesSiri):
        guardar_sancionado_siri(item)
        t += 1
        if t % 500 == 0:
            db.commit()
    db.commit()
    print("fin antecedentes")
    # ==========================================
    # 3. Sincronizar Contratos (Bulk Optimization)
    # ==========================================
    print("Sincronizando contratos de forma optimizada...")
    LIMIT = 2000
    offset = 0
    total_procesados = 0

    while True:
        # Bajar contratos por lote
        batch = client.get(ContratosSecopII, limit=LIMIT, offset=offset)
        if not batch:
            break

        # Extraer todos los IDs del lote
        ids_lote = [item["id_contrato"] for item in batch if "id_contrato" in item]

        # Hacer UN SOLO select a la base de datos para ver cuáles ya existen
        existentes_query = db(db.contratos.id_contrato.belongs(ids_lote)).select(
            db.contratos.id_contrato
        )
        existentes_ids = set(row.id_contrato for row in existentes_query)

        # Filtrar solo los contratos nuevos
        contratos_nuevos = [
            item for item in batch if item.get("id_contrato") not in existentes_ids
        ]

        if contratos_nuevos:
            print(
                f"Lote offset {offset}: Encontrados {len(contratos_nuevos)} contratos nuevos."
            )
            # Insertamos todos los contratos de una (Bulk Insert)
            # Primero transformamos y limpiamos
            contratos_limpios = [
                transformar_nombres_columnas(c) for c in contratos_nuevos
            ]
            db.contratos.bulk_insert(contratos_limpios)

            # Ahora procesamos entidades y personas
            for item in contratos_nuevos:
                procesar_contrato_completo(item)

            db.commit()

        total_procesados += len(batch)
        offset += LIMIT

        # Freno de emergencia (para que no baje millones)
        if total_procesados >= 5000:
            print("Límite de prueba (5000) alcanzado.")
            break
    print("fin contratos")
    # ==========================================
    # 4. Sincronizar Adiciones y Ejecuciones
    # ==========================================
    # Obtenemos todos los IDs de contratos que tenemos en la BD
    contratosindb = db(db.contratos).select(db.contratos.id_contrato, distinct=True)
    contractsindb = [c.id_contrato for c in contratosindb]

    print(f"Buscando adiciones para {len(contractsindb)} contratos...")
    # Podríamos optimizarlo armando queries con IN (...) en lugar de hacer 1 query por contrato
    # pero para mantenerlo simple y funcional por ahora:
    t = 0
    for contracindb in contractsindb:
        for item in client.get(AdicionesSecopII, where=f"id_contrato == '{contracindb}'"):
            t += 1
            guardar_adiciones([item], actualizar_existentes=True)
            if t % 500 == 0:
                print(f"Adiciones guardadas: {t}")

    print(f"Buscando ejecuciones para {len(contractsindb)} contratos...")
    t = 0
    for contracindb in contractsindb:
        for item in client.get(EjecucionesSecopII, where=f"identificadorcontrato == '{contracindb}'"):
            t += 1
            guardar_ejecuciones([item])
            if t % 500 == 0:
                print(f"Ejecuciones guardadas: {t}")

    print(f"Proceso finalizado en {time.time() - reloj:.2f} segundos.")
