Automatización de Web Scraping y ETL

## 1. Introducción

Este documento describe de manera detallada el diseño, las decisiones técnicas y el uso de un script en Python cuyo objetivo es automatizar la **extracción, transformación y carga (ETL)** de datos desde un sitio web de comercio electrónico de prueba: **[http://books.toscrape.com/](http://books.toscrape.com/)**.

El proyecto está planteado con un enfoque profesional, alineado con buenas prácticas de **ingeniería de datos**, priorizando:

* Robustez ante errores
* Claridad del código
* Facilidad de mantenimiento
* Escalabilidad conceptual

---

## 2. Instalación y Ejecución del Proyecto

### 2.1 Requisitos del Sistema

* Python **3.9 o superior**
* Acceso a internet
* Sistema operativo Windows, Linux o macOS

---

### 2.2 Estructura del Proyecto

```text
web_scraping_books/
│
├── scraper.py            # Script principal
├── requirements.txt      # Dependencias del proyecto
├── productos.csv         # Salida en CSV
├── productos.json        # Salida en JSON
├── productos.db          # Base de datos SQLite
└── README.md             # Documentación
```

---

### 2.3 Instalación de Dependencias

Se recomienda el uso de un entorno virtual para aislar las dependencias del proyecto.

#### Paso 1: Crear entorno virtual (opcional pero recomendado)

```bash
python -m venv venv
```

Activación del entorno virtual:

* **Windows**:

```bash
venv\Scripts\activate
```

* **Linux / macOS**:

```bash
source venv/bin/activate
```

#### Paso 2: Instalar dependencias

```bash
pip install -r requirements.txt
```

Contenido de `requirements.txt`:

```text
requests
beautifulsoup4
```

---

### 2.4 Ejecución del Script

Para ejecutar el proceso completo de scraping y ETL:

```bash
python scraper.py
```

Al finalizar la ejecución se generarán automáticamente:

* `productos.csv`
* `productos.json`
* `productos.db`

Además, se mostrará información de progreso y advertencias mediante **logging**.

---

## 3. Elección Tecnológica: Requests + BeautifulSoup vs Selenium

### 3.1 Análisis del Sitio Web Objetivo

El sitio **books.toscrape.com** presenta las siguientes características:

* Contenido **estático**
* No depende de JavaScript para renderizar información
* Estructura HTML clara y predecible
* Paginación basada en enlaces HTML

---

### 3.2 Justificación de `requests + BeautifulSoup`

Se eligió esta combinación por las siguientes razones:

1. **Eficiencia**: menor consumo de recursos comparado con un navegador automatizado.
2. **Velocidad**: las peticiones HTTP directas son significativamente más rápidas.
3. **Simplicidad**: menor complejidad de implementación y mantenimiento.
4. **Escalabilidad**: más adecuado para scraping masivo y automatizado.
5. **Control del flujo**: manejo explícito de errores, tiempos de espera y parsing.

---

### 3.3 ¿Cuándo usar Selenium?

Selenium habría sido necesario si:

* El contenido se cargara dinámicamente con JavaScript
* Existieran interacciones complejas (clicks, formularios, login)
* El HTML no estuviera disponible en la respuesta inicial

Dado que **ninguna de estas condiciones aplica**, Selenium se consideró innecesario y menos óptimo para este caso.

---

## 4. Suposiciones y Decisiones de Diseño

### 4.1 Suposiciones

Durante el desarrollo se asumió que:

* El HTML del sitio es relativamente estable
* Cada producto sigue el patrón `article.product_pod`
* El precio siempre es representable como número decimal
* La valoración está codificada en clases CSS (`One`, `Two`, etc.)
* El texto de stock contiene un número cuando hay disponibilidad

Estas suposiciones son razonables para un sitio de prueba y se documentan explícitamente.

---

### 4.2 Decisiones de Diseño Clave

#### a) Robustez ante errores

* Cada producto se procesa dentro de un bloque `try/except`
* Un error en un producto **no detiene** el scraping completo
* Los errores se registran mediante `logging.warning`

#### b) Politeness

* Se implementa una pausa entre requests (`time.sleep`)
* Se evita saturar el servidor

#### c) Separación de responsabilidades

* Extracción (scraping)
* Transformación (parsing y limpieza)
* Carga (CSV, JSON, SQLite)

Esto facilita mantenimiento y escalabilidad.

---

## 5. Automatización en un Entorno de Producción

### Pregunta de reflexión:

**¿Cómo adaptarías este script para que se ejecute automáticamente todos los días en producción?**

### 5.1 Cron Jobs (Linux)

* Crear una tarea cron diaria:

```bash
0 2 * * * /usr/bin/python3 /ruta/scraper.py
```

Ventajas:

* Simple
* Bajo costo

Limitaciones:

* Poco control de dependencias
* Difícil monitoreo

---

### 5.2 Apache Airflow (Recomendado)

* Convertir el script en un DAG
* Programación diaria
* Manejo de retries
* Observabilidad y alertas

Ideal para pipelines de datos empresariales.

---

### 5.3 GitHub Actions

* Workflow diario con `schedule`
* Ejecución en contenedores
* Versionado del código

Útil para proyectos pequeños o medianos.

---

## 6. Escalabilidad a 100 Sitios Web

### Pregunta de reflexión:

**Si tuvieras que escalar este proceso a 100 sitios diferentes, ¿cómo sería la arquitectura?**

---

### 6.1 Componentes Principales de la Arquitectura

1. **Orquestador**

   * Apache Airflow / Prefect
   * Control de dependencias y scheduling

2. **Scrapers desacoplados por sitio**

   * Un módulo por dominio
   * Configuración externa (YAML/JSON)

3. **Cola de Mensajes**

   * RabbitMQ / Kafka
   * Desacopla extracción y procesamiento

4. **Almacenamiento Intermedio**

   * Data Lake (S3 / GCS / Azure Blob)

5. **Capa de Normalización**

   * Transformaciones comunes
   * Esquemas homogéneos

6. **Base de Datos Analítica**

   * PostgreSQL / BigQuery / Redshift

7. **Observabilidad**

   * Logging centralizado
   * Métricas
   * Alertas

---

### 6.2 Beneficios de esta Arquitectura

* Alta escalabilidad
* Tolerancia a fallos
* Reprocesamiento sencillo
* Separación clara de responsabilidades

---

## 7. Conclusión

Este proyecto demuestra una implementación completa y profesional de un pipeline de scraping y ETL, con énfasis en:

* Robustez
* Buenas prácticas
* Diseño escalable
* Pensamiento de ingeniería de datos

El enfoque adoptado es adecuado tanto para entornos académicos como para contextos reales de producción.
