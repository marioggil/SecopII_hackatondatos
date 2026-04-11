from pydal import DAL, Field

import os, datetime

pwd = os.getcwd()
try:
    os.stat(pwd + '/databases')
except:
    os.mkdir(pwd + '/databases')

db = DAL('sqlite://contratos.db', folder='databases')

# Definición de la tabla (ejemplo simplificado, ajusta según necesites)
db.define_table('contratos',
    Field('nombre_entidad', 'string'),
    Field('nit_entidad', 'string'),
    Field('departamento', 'string'),
    Field('ciudad', 'string'),
    Field('localizacion', 'string'),
    Field('orden', 'string'),
    Field('sector', 'string'),
    Field('rama', 'string'),
    Field('entidad_centralizada', 'string'),
    Field('proceso_compra', 'string'),
    Field('id_contrato', 'string'),
    Field('referencia_contrato', 'string'),
    Field('estado_contrato', 'string'),
    Field('codigo_categoria_principal', 'string'),
    Field('descripcion_proceso', 'text'),
    Field('tipo_contrato', 'string'),
    Field('modalidad_contratacion', 'string'),
    Field('justificacion_modalidad', 'string'),
    Field('fecha_firma', 'datetime'),
    Field('fecha_inicio', 'datetime'),
    Field('fecha_fin', 'datetime'),
    Field('condiciones_entrega', 'string'),
    Field('tipo_doc_proveedor', 'string'),
    Field('documento_proveedor', 'string'),
    Field('proveedor_adjudicado', 'string'),
    Field('es_grupo', 'string'),
    Field('es_pyme', 'string'),
    Field('habilita_pago_adelantado', 'string'),
    Field('liquidacion', 'string'),
    Field('obligacion_ambiental', 'string'),
    Field('obligaciones_postconsumo', 'string'),
    Field('reversion', 'string'),
    Field('origen_recursos', 'string'),
    Field('destino_gasto', 'string'),
    Field('valor_contrato', 'decimal(15,2)'),
    Field('valor_pago_adelantado', 'decimal(15,2)'),
    Field('valor_facturado', 'decimal(15,2)'),
    Field('valor_pendiente_pago', 'decimal(15,2)'),
    Field('valor_pagado', 'decimal(15,2)'),
    Field('valor_amortizado', 'decimal(15,2)'),
    Field('valor_pendiente_amortizacion', 'decimal(15,2)'),
    Field('valor_pendiente_ejecucion', 'decimal(15,2)'),
    Field('estado_bpin', 'string'),
    Field('codigo_bpin', 'string'),
    Field('anno_bpin', 'string'),
    Field('saldo_cdp', 'decimal(15,2)'),
    Field('saldo_vigencia', 'decimal(15,2)'),
    Field('es_postconflicto', 'string'),
    Field('dias_adicionados', 'integer'),
    Field('puntos_acuerdo', 'string'),
    Field('pilares_acuerdo', 'string'),
    Field('url_proceso', 'string'),
    Field('nombre_representante_legal', 'string'),
    Field('nacionalidad_representante_legal', 'string'),
    Field('domicilio_representante_legal', 'string'),
    Field('tipo_identificacion_representante_legal', 'string'),
    Field('identificacion_representante_legal', 'string'),
    Field('genero_representante_legal', 'string'),
    Field('presupuesto_pgn', 'decimal(15,2)'),
    Field('sistema_participaciones', 'decimal(15,2)'),
    Field('sistema_regalias', 'decimal(15,2)'),
    Field('recursos_propios_alcaldias', 'decimal(15,2)'),
    Field('recursos_credito', 'decimal(15,2)'),
    Field('recursos_propios', 'decimal(15,2)'),
    Field('ultima_actualizacion', 'datetime'),
    Field('codigo_entidad', 'string'),
    Field('codigo_proveedor', 'string'),
    Field('fecha_inicio_liquidacion', 'datetime'),
    Field('fecha_fin_liquidacion', 'datetime'),
    Field('objeto_contrato', 'text'),
    Field('duracion_contrato', 'string'),
    Field('nombre_banco', 'string'),
    Field('tipo_cuenta', 'string'),
    Field('numero_cuenta', 'string'),
    Field('puede_prorrogarse', 'string'),
    Field('nombre_ordenador_gasto', 'string'),
    Field('tipo_doc_ordenador_gasto', 'string'),
    Field('num_doc_ordenador_gasto', 'string'),
    Field('nombre_supervisor', 'string'),
    Field('tipo_doc_supervisor', 'string'),
    Field('num_doc_supervisor', 'string'),
    Field('nombre_ordenador_pago', 'string'),
    Field('tipo_doc_ordenador_pago', 'string'),
    Field('num_doc_ordenador_pago', 'string')
)

db.define_table('adiciones',
    Field('id_adicion', 'string', unique=True),
    Field('id_contrato', 'string'),
    Field('tipo_modificacion', 'string'),
    Field('descripcion', 'text'),
    Field('fecha_registro', 'datetime')
)

# Definición de la tabla de ejecuciones
db.define_table('ejecuciones',
    Field('id_contrato', 'string'),
    Field('tipo_ejecucion', 'string'),
    Field('nombre_plan', 'string'),
    Field('fecha_entrega_esperada', 'datetime'),
    Field('porcentaje_avance_esperado', 'decimal(10,6)'),
    Field('fecha_entrega_real', 'datetime'),
    Field('porcentaje_avance_real', 'decimal(10,6)'),
    Field('estado_contrato', 'string'),
    Field('referencia_articulos', 'string'),
    Field('descripcion', 'text'),
    Field('unidad', 'string'),
    Field('cantidad_adjudicada', 'decimal(15,6)'),
    Field('cantidad_planeada', 'decimal(15,6)'),
    Field('cantidad_recibida', 'decimal(15,6)'),
    Field('cantidad_por_recibir', 'decimal(15,6)'),
    Field('fecha_creacion', 'datetime')
)


db.define_table('entidades',
    Field('nit_entidad', 'string', unique=True, notnull=True),
    Field('nombre_entidad', 'string'),
    Field('departamento', 'string'),
    Field('ciudad', 'string'),
    Field('orden', 'string'),
    Field('sector', 'string'),
    Field('rama', 'string'),
    Field('entidad_centralizada', 'string')
)

# Tabla de proveedores y personas
db.define_table('proveedoresypersonas',
    Field('documento', 'string', unique=True, notnull=True),
    Field('nombre', 'string'),
    Field('es_grupo', 'string'),
    Field('es_pyme', 'string'),
    Field('tipo', 'string')  # entidad, proveedor, representante_legal, ordenador_del_gasto, supervisor
)

db.define_table('sancionados',
    Field('documento', 'string', notnull=True),
    Field('tipo_inhabilitacion', 'string'),
    Field('primer_nombre', 'string'),
    Field('segundo_nombre', 'string'),
    Field('primer_apellido', 'string'),
    Field('segundo_apellido', 'string'),
    Field('nombre_completo', 'string'),  # Para amonestados SECOP
    Field('sancion', 'text'),
    Field('fecha_efectos_juridicos', 'date'),
    Field('numero_resolucion', 'string'),
    Field('origen', 'string')  # 'SIRI' o 'SECOP'
)

# Índice compuesto para mejorar consultas
db.executesql('CREATE INDEX IF NOT EXISTS idx_sancionados_documento ON sancionados(documento)')
