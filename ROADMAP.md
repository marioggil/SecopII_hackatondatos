# Roadmap y Propuestas de Evolución Arquitectónica

Este documento expone las diferentes ideas o rutas de desarrollo futuro planteadas para escalar la herramienta de análisis y auditoría contractual (*Secop Visual*). Las propuestas buscan robustecer la capa analítica, optimizar el rendimiento y agregar automatización nativa a los pipelines de ingesta.

---

## 1. Análisis de Redes y Grafos de Conocimiento (Knowledge Graphs)

La estructuración actual de datos modela las identidades operacionales de forma relacional (Contratos, Entidades, Personas).

### Ideas sin desarrollar en profundidad:

- Ejecutar algoritmos de centralidad, detección de comunidades (Louvain) y recorridos de profundidad para identificar rápidamente redes cerradas de contratación.

## 2. Pipeline de Detección de Anomalías (Machine Learning / Heurística)

Actualmente las validaciones cruzan inhabilitaciones de forma determinística basándose en fechas. El siguiente nivel es la detección probabilística de sobrecostos o patrones inusuales.

### Especificaciones Técnicas:
- **Modelado:** Implementar algoritmos no supervisados como Isolation Forests o Autoencoders para definir clusters de normalidad (basándose en modalidad de contratación y sector).
- **Métricas:** Desviación en el monto adjudicado comparado con promedios móviles sectoriales, varianza en tiempos de ejecución esperados, y ratio anormal de adiciones contractuales.
- **Arquitectura:** Microservicio gRPC/FastAPI en Python montado sobre Scikit-Learn/XGBoost para generar scores de "riesgo de corrupción" a los contratos nuevos de manera automatizada, se podria hacer una ruta de entrenamiento con mlflow y  despliegue de modelos propios.

## 3. Ingesta Automática y Arquitectura Basada en Eventos

El sistema depende de procesos sincrónicos para ingestar la data. Para escalar de forma eficiente y mantenerse a la par con la data gubernamental se intentaria hacer actualizaciones cada semana  aunque la informacion es diaria para ir reduciendo los tiempos de actualizacion, requiere automatización en background.

### Especificaciones Técnicas:
- **Procesamiento Asíncrono:** Una propuesta sacada con investigacion guiada por AI es Instauración de Celery Workers utilizando Redis o RabbitMQ como message broker para orquestar los pipelines ETL, tendria que ver si esto seria la mejor opcion para este proyecto.
- **Scheduling:** Celery Beat (o temporalidades de CRON en orquestador) para capturar iterativamente los paginados proveídos por la API Socrata (Open Data) de SECOP, operando sin interacción del usuario.
- **Persistencia de Estados:** Guardar los timestamps procesados en caché para que las fallas de red implementen auto-retry y preserven la idempotencia del insert.

## 4. Motor Búsqueda Full-Text (FTS) e In-Memory Cache

Almacenar millones de registros contractuales generará cuellos de botella al realizar consultas ILIKE nativas sobre campos de texto libre como "Objeto del Contrato", este tambien es un campo desconocido para el desarrolador del proyecto pero se puede explorar.

### Especificaciones Técnicas:
- **Motores Indexadores:** Apalancar Meilisearch, Typesense o ElasticSearch para texto.
- **Enfoque de Lectura/Escritura:** CQRS pragmático. Los POST transaccionales operan en SQLite/PostgreSQL, desencadenando eventos de indexación hacia el motor FTS.
- **Resultados:** Capacidades de autocompletado en el front (HTMX/Alpine/JS nativo), tolerancia algorítmica a faltas ortográficas al buscar justificaciones, e interfaz reactiva con latencia bajo los ~20ms.

## 5. Módulo de Business Intelligence (BI) e Interfaces Analíticas Libres

Como herramienta de auditoría para un destrancar el activo de datos y permitirle al analista llevárselo y cruzarlo externamente añade un valor incalculable.

### Especificaciones Técnicas:
- **Almacenamiento Columnar:** Funcionalidades de volcado periódico de la bdd estructurada a formatos OLAP como Apache Parquet, reduciendo el peso y facilitando lecturas analíticas enormes.
- **Reporting Nativo:** Rutas programáticas para crear "Dossier de Proveedor" en PDF (generados en el server mediante headless browsers o librerías nativas) detallando su historial sancionatorio y estadístico.
- **Data Hookups:** Integración habilitada para PowerBI directamente leyendo de sub-sistemas OLAP o réplicas read-only.
