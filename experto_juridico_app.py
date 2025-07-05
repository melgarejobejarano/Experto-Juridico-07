from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path

import openai
import streamlit as st
from docx import Document
from PyPDF2 import PdfReader

###############################################################################
# Configuración de la página y estilo                                          
###############################################################################

st.set_page_config(
    page_title="Experto Jurídico 7.0",
    page_icon="⚖️",
    layout="centered",
)

# Inyección de CSS para tema morado y centrado                                  
st.markdown(
    """
    <style>
        :root {
            --primary-color: #6a0dad;       /* Morado principal */
            --text-color: #000000;
            --background-color: #f7f2fc;
        }
        .stApp {
            background-color: var(--background-color);
        }
        footer {visibility: hidden;}
        .block-container {
            padding-top: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

###############################################################################
# Variables y utilidades                                                       
###############################################################################

ASSISTANT_IDS = {
    "Derecho Civil": "asst_JEqVhFH9ertyrJTGFNq1zIZ0",
    "Derecho de Familia": "asst_k72lXItROiR9tgnDBiqmWf9j",
}

openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    st.warning("⚠️  Defina la variable de entorno OPENAI_API_KEY para continuar.")

MAX_DOC_CHARS = 100_000  # límite para evitar desbordar tokens

###############################################################################
# Funciones de extracción de texto                                             
###############################################################################

def _extract_text_from_pdf(file) -> str:
    reader = PdfReader(file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _extract_text_from_docx(file) -> str:
    doc = Document(file)
    return "\n".join(p.text for p in doc.paragraphs)


def extract_text(uploaded_file) -> str:
    """Extrae texto de un PDF o Word subido."""
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix == ".pdf":
        return _extract_text_from_pdf(uploaded_file)
    if suffix == ".docx":
        return _extract_text_from_docx(uploaded_file)
    raise ValueError("Formato no soportado: debe ser PDF o DOCX")

###############################################################################
# Función de análisis con Assistants                                           
###############################################################################

@st.cache_data(show_spinner=False, ttl=3600, max_entries=32)
def ai_analyze(document_text: str, assistant_id: str, area: str) -> dict | None:
    """Envía el documento al asistente y obtiene la etapa procesal y soluciones."""
    # Reducir a tamaño manejable
    doc_chunk = document_text[:MAX_DOC_CHARS]

    thread = openai.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": (
                    "Revisa el siguiente documento legal y responde EXCLUSIVAMENTE "
                    "con un JSON que contenga las claves 'etapa_proceso' (string) "
                    "y 'soluciones' (lista de strings). No incluyas ningún texto adicional.\n\n"
                    f"Área de especialidad: {area}.\n\nDocumento:\n{doc_chunk}"
                ),
            }
        ]
    )

    run = openai.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)

    # Esperar a que termine
    while run.status not in {"completed", "failed", "cancelled"}:
        time.sleep(1)
        run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    if run.status != "completed":
        return None

    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    reply = messages.data[0].content[0].text.value.strip()

    try:
        data = json.loads(reply)
    except json.JSONDecodeError:
        # Intentar repararlo con un modelo de corrección rápida
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Corrige para que sea JSON válido sin comentarios."},
                {"role": "user", "content": reply},
            ],
            temperature=0.0,
        )
        data = json.loads(completion.choices[0].message.content)

    return data

###############################################################################
# Función de redacción de escrito                                              
###############################################################################

def ai_draft(solution: str, stage: str, assistant_id: str, area: str, original_text: str) -> str:
    """Solicita al asistente la redacción del escrito judicial."""
    prompt = (
        "Redacta el documento legal completo para presentar ante el Poder Judicial.\n"
        f"Área de especialidad: {area}\n"
        f"Etapa procesal: {stage}\n"
        f"Solución elegida: {solution}\n\n"
        "Basándote en el siguiente documento original:\n"
        f"{original_text[:MAX_DOC_CHARS]}\n\n"
        "Entrega únicamente el texto del documento, estructurado formalmente y sin encabezados de carta."
    )

    thread = openai.beta.threads.create(messages=[{"role": "user", "content": prompt}])
    run = openai.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)

    while run.status not in {"completed", "failed", "cancelled"}:
        time.sleep(1)
        run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    return messages.data[0].content[0].text.value.strip()

###############################################################################
# Interfaz principal                                                           
###############################################################################

# Crear layout de dos columnas para el título y la imagen
col1, col2 = st.columns([2, 1])  # La primera columna es el doble de ancha que la segunda

with col1:
    st.title("Experto Jurídico 7.0")

with col2:
    st.image("abogada experta japon.png", width=150)  # Tamaño fijo de 150 píxeles

# Selección del área
area = st.selectbox(
    "Seleccione la especialidad jurídica:",
    ("Derecho Civil", "Derecho de Familia"),
    index=None,
    placeholder="Elija una opción…",
)

uploaded_file = None
if area:
    uploaded_file = st.file_uploader(
        "Adjunte el documento (PDF o Word)",
        type=["pdf", "docx"],
        accept_multiple_files=False,
    )

if uploaded_file is not None:
    with st.spinner("Leyendo y analizando documento…"):
        try:
            text = extract_text(uploaded_file)
        except Exception as e:
            st.error(f"❌ {e}")
            st.stop()

        assistant_id = ASSISTANT_IDS[area]
        analysis = ai_analyze(text, assistant_id, area)

    if analysis is None:
        st.error("❌ No se pudo analizar el documento. Inténtelo de nuevo más tarde.")
        st.stop()

    stage = analysis.get("etapa_proceso", "Desconocida")
    suggestions = analysis.get("soluciones", [])

    st.success(f"**Etapa procesal identificada:** {stage}")

    if suggestions:
        choice = st.radio("Seleccione la solución legal a aplicar:", suggestions)
    else:
        st.warning("El asistente no devolvió soluciones. Modifique o reduzca el documento e intente nuevamente.")
        st.stop()

    if st.button("Generar escrito para el Poder Judicial") and choice:
        with st.spinner("Redactando escrito…"):
            draft_text = ai_draft(choice, stage, assistant_id, area, text)

        st.subheader("Borrador generado ✨")
        st.text_area("Documento", draft_text, height=500)

        # Generar documento Word
        doc = Document()
        doc.add_paragraph(draft_text)
        
        # Guardar temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            doc.save(tmp.name)
            
            # Leer el archivo para la descarga
            with open(tmp.name, "rb") as docx_file:
                docx_bytes = docx_file.read()
            
            st.download_button(
                label="Descargar como DOCX",
                data=docx_bytes,
                file_name="escrito_judicial.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            
            # Limpiar archivo temporal
            os.unlink(tmp.name) 