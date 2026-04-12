# SECOP II Visual

## 📊 Descripción del Proyecto

SECOP II Visual es una herramienta de visualización y análisis de datos de contratación pública en Colombia. El Sistema Electrónico de Contratación Pública (SECOP II) contiene información de todos los contratos de la administración pública, pero su gran volumen y complejidad dificultan su análisis. Este proyecto transforma esos datos en visualizaciones intuitivas y comprensibles.

## 🎯 Objetivo

Hacer accesible y comprensible la información de contratación pública mediante visualizaciones interactivas que permitan:

- Identificar patrones en la contratación estatal
- Detectar relaciones entre entidades y proveedores
- Analizar tendencias temporales y presupuestarias
- Facilitar la transparencia y el control ciudadano

## ✨ Características Principales

### 1. Vista General Exploratoria
Para usuarios que no tienen un objetivo específico de búsqueda:
- Dashboard con métricas clave de contratación
- Resumen ejecutivo de la actividad contractual
- Estadísticas generales por sector y región

### 2. Análisis de Relaciones
- **Entidades vs Proveedores**: Visualización de red mostrando cantidad de contratos entre entidades públicas y proveedores
- **Concentración contractual**: Identificación de relaciones preferenciales
- **Análisis de competencia**: Número de proponentes por proceso

### 3. Análisis Temporal
- Evolución histórica de la contratación
- Estacionalidad en procesos de contratación
- Líneas de tiempo de proyectos y ejecución contractual
- Tendencias por año, mes y período

### 4. Análisis Presupuestal
- Distribución de presupuestos por entidad
- Montos contratados vs montos ejecutados
- Análisis de eficiencia presupuestal
- Comparativas de costos por sector

### 5. Análisis de Adiciones y Modificaciones
- **Entidades con más adiciones**: Ranking de entidades que más modifican sus contratos
- **Proveedores con más adiciones**: Análisis de contratistas que frecuentemente reciben adiciones
- Porcentajes de incremento sobre valor inicial
- Alertas de adiciones atípicas

## 🛠️ Tecnologías

- **Backend**: FastAPI
- **Python**: 3.11
- **Gestor de paquetes**: uv (ultrafast Python package installer)
- **ORM/DAL**: PyDAL (Python Database Abstraction Layer)
- **Base de datos**: Compatible con múltiples motores (SQLite, PostgreSQL, MySQL, etc.)
- **Visualización**: D3.js
- **Frontend**: HTML5, CSS3, JavaScript

## 📋 Requisitos Previos

```bash
Python 3.11
uv (https://github.com/astral-sh/uv)
```

### Instalación de uv

```bash
# macOS y Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Con pip (alternativa)
pip install uv
```

## 🚀 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/secop2-visual.git
cd secop2-visual

# Crear entorno virtual con uv
uv venv

# Activar entorno virtual
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias con uv
uv pip install -r requirements.txt

# O sincronizar desde pyproject.toml (si usas uv project)
uv sync

# Configurar base de datos
# PyDAL soporta múltiples motores: SQLite, PostgreSQL, MySQL, etc.
# Por defecto usa SQLite (no requiere instalación adicional)

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones
```

## ⚙️ Configuración

Edita el archivo `.env` con los siguientes parámetros:

```env
# Configuración de PyDAL
# Para SQLite (desarrollo)
DATABASE_URI=sqlite://storage.db

# Para PostgreSQL (producción)
# DATABASE_URI=postgres://user:password@localhost/secop2

# Para MySQL
# DATABASE_URI=mysql://user:password@localhost/secop2

API_PORT=8000
SECOP_API_KEY=tu_api_key
```

## 🏃 Ejecución

```bash
# Modo desarrollo
uv run uvicorn main3:app --reload

# O si ya tienes el entorno activado
uvicorn main:app --reload

# Modo producción
uv run uvicorn main3:app --host 0.0.0.0 --port 8000
```

La aplicación estará disponible en: `http://localhost:8000`

Documentación interactiva de la API: `http://localhost:8000/docs`

## 📁 Estructura del Proyecto

```
secop2-visual/
├── app/
│   ├── api/
│   │   └── endpoints/
│   ├── core/
│   │   ├── config.py
│   │   └── database.py         # Configuración PyDAL
│   ├── models/
│   │   └── tables.py           # Definición de tablas PyDAL
│   ├── services/
│   │   ├── secop_service.py
│   │   └── analytics_service.py
│   └── static/
│       ├── css/
│       ├── js/
│       │   └── d3-visualizations.js
│       └── data/
├── templates/
│   └── index.html
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

## 🔌 Endpoints Principales

```
En desarrollo
```

## 📊 Ejemplos de Uso

### Consultar contratos de una entidad específica
```bash
curl http://localhost:8000/api/v1/contracts?entity_id=123&year=2024
```

### Obtener análisis de adiciones
```bash
curl http://localhost:8000/api/v1/analysis/additions?limit=10
```

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

## 👥 Autores

- marioggil - [@marioggil](https://github.com/marioggil)


---

**Nota**: Este proyecto es una iniciativa independiente de análisis de datos públicos y no está afiliado con Colombia Compra Eficiente ni con ninguna entidad gubernamental.
