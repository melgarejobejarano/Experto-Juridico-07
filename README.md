# Experto Jurídico 7.0 🏛️

Aplicación Streamlit que permite analizar documentos legales utilizando agentes especializados y generar escritos listos para presentar ante el Poder Judicial.

## Características

- 📄 Análisis de documentos PDF y Word (DOCX)
- 🤖 Utiliza OpenAI Assistants API para análisis especializado
- ⚖️ Soporte para Derecho Civil y Derecho de Familia
- 💜 Interfaz moderna con tema personalizado
- 📝 Generación de escritos judiciales
- 💾 Descarga de documentos en formato TXT

## Requisitos

- Python 3.8 o superior
- Clave de API de OpenAI con acceso a Assistants
- IDs de asistentes configurados para cada especialidad

## Instalación

1. Clone el repositorio:
   ```bash
   git clone <url-del-repositorio>
   cd experto-juridico
   ```

2. Instale las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure la variable de entorno con su clave de API de OpenAI:
   ```bash
   export OPENAI_API_KEY='su-clave-api-aquí'
   ```

## Uso

1. Inicie la aplicación:
   ```bash
   streamlit run experto_juridico_app.py
   ```

2. Abra su navegador en `http://localhost:8501`

3. Seleccione la especialidad jurídica

4. Suba su documento (PDF o DOCX)

5. Revise el análisis y seleccione la solución propuesta

6. Genere y descargue el escrito judicial

## Notas Importantes

- La aplicación limita el tamaño de los documentos a analizar para evitar exceder los límites de tokens de la API
- Los asistentes deben estar previamente configurados en OpenAI con los IDs correctos
- Para un tema persistente, cree el archivo `.streamlit/config.toml` con:
  ```toml
  [theme]
  primaryColor = "#6a0dad"
  ```

## IDs de Asistentes

- Derecho Civil: `asst_JEqVhFH9ertyrJTGFNq1zIZ0`
- Derecho de Familia: `asst_k72lXItROiR9tgnDBiqmWf9j`

## Licencia

Este proyecto está bajo la Licencia MIT. Vea el archivo `LICENSE` para más detalles. 