import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import WebBaseLoader
import google.generativeai as genai
import tempfile
import io

st.title("Summary pdf avec IA")
st.markdown(
    ":violet-badge[:material/star: LLMS]   :orange-badge[GEN_IA]   :gray-badge[Gemini]")

api_key= st.text_input("ajoute la api key de gemini", type= "password")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.0-pro')
else:
    st.warning("Veuillez ajouter la clé API Gemini")

def upload_file():
    """
    ***
    """
    upload_option = st.radio("Choisissez une option :", 
                             ("Télécharger un fichier pdf", "Entrer une URL"))
    if upload_option == "Télécharger un fichier pdf":
        uploaded_file = st.file_uploader("Choisissez un fichier pdf", type="pdf")
        if uploaded_file is not None:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_file_path = tmp_file.name
                loader = PyPDFLoader(tmp_file_path)
                st.session_state.loader= loader
                st.session_state.docs = loader.load()
                st.subheader("fichier bien charge")
            except Exception as e:
                st.error(f"Erreur lors du chargement du fichier: {str(e)}")

    elif upload_option == "Entrer une URL":
        url = st.text_input("Entrez l'URL du fichier pdf")
        if st.button("Charger le fichier depuis l'URL"):
            if url:
                try:
                    loader = WebBaseLoader(url, encoding='latin-1')
                    st.session_state.loader = loader  # Guarda los datos en el estado
                    st.session_state.docs = loader.load()
                    st.subheader("Fichier chargé depuis l'URL")
                except Exception as e:
                    st.error(f"Erreur lors du chargement: {str(e)}")
            else:
                st.warning("Veuillez entrer une URL valide.")

upload_file()

def resumir_con_gemini(texto):
    if not api_key:
        st.error("Clé API manquante")
        return ""
    
    try:
        response = model.generate_content(
            f"Resume el siguiente texto en español de manera concisa y profesional:\n\n{texto}",
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,  # Para respuestas más enfocadas
                max_output_tokens=2000
            )
        )
        return response.text
    except Exception as e:
        st.error(f"Error al generar el resumen: {str(e)}")
        return ""

# model = genai.GenerativeModel('gemini-pro')
# if api_key:
#     genai.configure(api_key=api_key)

#     def resumir_con_gemini(texto):
#         model = genai.GenerativeModel('veo-2.0-generate-001')
#         response = model.generate_content(f"Resume el siguiente texto en español:\n\n{texto}")
#         return response.text
# else:
#     st.warning("erreur, ajoute la api key")

if st.button("Générer le résumé", type='primary'):
    if "docs" in st.session_state and st.session_state.docs:
        full_text = "\n".join([doc.page_content for doc in st.session_state.docs])
        resumen = resumir_con_gemini(full_text)
        st.session_state.resumen = resumen  # Guardar para descarga
        st.text_area("Résumé", value=resumen, height=300)
    else:
        st.warning("Veuillez d'abord charger un PDF ou une URL.")

if "resumen" in st.session_state:
    st.download_button(
        label="Télécharger le résumé",
        data=st.session_state.resumen,
        file_name="resume.txt",
        mime="text/plain",
        type="primary",
        key="download_button"
    )
