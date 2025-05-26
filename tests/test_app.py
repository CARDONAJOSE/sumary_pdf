import pytest
from unittest.mock import MagicMock, patch, mock_open
import streamlit as st
import tempfile
import io
# Importa la función que quieres testear
# Asegúrate de que 'app.py' exista en el mismo nivel o ajusta la importación
from app import upload_file


@pytest.fixture
def mock_streamlit():
    """
    Fixture pour mockear le module Streamlit et son st.session_state.
    """
    with patch('app.st', new_callable=MagicMock) as mock_st:
        # Mockear st.session_state comme un MagicMock pour permettre l'accès par attribut
        mock_st.session_state = MagicMock() 
        yield mock_st

@pytest.fixture
def mock_tempfile():
    """
    Fixture pour mockear tempfile.NamedTemporaryFile.
    """
    with patch('app.tempfile', new_callable=MagicMock) as mock_tf:
        mock_file_context = MagicMock()
        # Asegúrate de que el mock del archivo temporal tiene un nombre accesible
        mock_file_context.__enter__.return_value = MagicMock(name="mock_temp_file_handle")
        # Es crucial que el nombre del archivo mockeado sea un string, como lo espera PyPDFLoader
        mock_file_context.__enter__.return_value.name = "/tmp/mock_file.pdf"
        mock_tf.NamedTemporaryFile.return_value = mock_file_context
        yield mock_tf

# --- Tests "Télécharger un fichier pdf" ---

def test_upload_pdf_file_successful(mock_streamlit, mock_tempfile):
    """
    Test que simule le cas ou aucune erreur se produit lors de la subida d'un fichier PDF a travers st.file_uploader.
    """
    # 1. Configurer mocks specífiques
    mock_streamlit.radio.return_value = "Télécharger un fichier pdf"
    
    mock_uploaded_file = MagicMock(spec=io.BytesIO)
    mock_uploaded_file.read.return_value = b"%PDF-1.4\nTest PDF Content."
    mock_streamlit.file_uploader.return_value = mock_uploaded_file

    # Mockear PyPDFLoader
    with patch('app.PyPDFLoader') as mock_pdf_loader:
        mock_loader_instance = MagicMock()
        mock_loader_instance.load.return_value = ["doc1_page1", "doc1_page2"]
        mock_pdf_loader.return_value = mock_loader_instance
        
        # 2. appelle a la fonction
        upload_file()
        
        # 3. (Assertions)
        mock_streamlit.radio.assert_called_once_with(
            "Choisissez une option :",
            ("Télécharger un fichier pdf", "Entrer une URL")
        )
        mock_streamlit.file_uploader.assert_called_once_with(
            "Choisissez un fichier pdf", type="pdf"
        )
        
        # Verifier le fichier temporal
        mock_tempfile.NamedTemporaryFile.assert_called_once_with(delete=False, suffix=".pdf")
        
        # Verifie le contenu du fichier subi
        mock_uploaded_file.read.assert_called_once()
        mock_tempfile.NamedTemporaryFile.return_value.__enter__.return_value.write.assert_called_once_with(
            b"%PDF-1.4\nTest PDF Content."
        )
        
        # Verifier que PyPDFLoader a été instancié avec la route temporaire
        mock_pdf_loader.assert_called_once_with(mock_tempfile.NamedTemporaryFile.return_value.__enter__.return_value.name)
        
        # Verifier que le loader et les docs ont été enregistrés dans st.session_state
        assert mock_streamlit.session_state.loader == mock_loader_instance
        assert mock_streamlit.session_state.docs == ["doc1_page1", "doc1_page2"]
        
        # Verifier que le message de succès a été affiché
        mock_streamlit.subheader.assert_called_once_with("fichier bien charge")
        
        # Verifier que le fichier temporaire a été fermé et supprimé (impliqué par NamedTemporaryFile dans le contexte réel)
        # Ici, nous nous assurons que le contexte a été géré correctement.

def test_upload_pdf_file_no_file_uploaded(mock_streamlit):
    """
    Test que simule le cas où aucun fichier PDF n'est téléchargé.
    """
    mock_streamlit.radio.return_value = "Télécharger un fichier pdf"
    mock_streamlit.file_uploader.return_value = None # Simule que aucun fichier n'a été téléchargé
    # appelle a la fonction
    upload_file()

    mock_streamlit.radio.assert_called_once()
    mock_streamlit.file_uploader.assert_called_once()
    
    # Asegurarse de que no se intentó crear un fichier temporaire ni usar PyPDFLoader
    with patch('app.tempfile.NamedTemporaryFile') as mock_temp_file:
        mock_temp_file.assert_not_called()
    with patch('app.PyPDFLoader') as mock_pdf_loader:
        mock_pdf_loader.assert_not_called()
    
    # Verifier modification de st.session_state et subheader
    assert "loader" not in mock_streamlit.session_state
    assert "docs" not in mock_streamlit.session_state
    mock_streamlit.subheader.assert_not_called()
    mock_streamlit.error.assert_not_called() 

def test_upload_pdf_file_loading_error(mock_streamlit, mock_tempfile):
    """
    Test que simule un error durant la charge du PDF.
    """
    mock_streamlit.radio.return_value = "Télécharger un fichier pdf"
    
    mock_uploaded_file = MagicMock(spec=io.BytesIO)
    mock_uploaded_file.read.return_value = b"%PDF-1.4\nCorrupt content."
    mock_streamlit.file_uploader.return_value = mock_uploaded_file

    # Mockear PyPDFLoader  pour que levante une exception
    with patch('app.PyPDFLoader') as mock_pdf_loader:
        mock_pdf_loader.side_effect = Exception("Simulated PDF loading error.")
        
        upload_file()
        
        mock_streamlit.error.assert_called_once_with(
            "Erreur lors du chargement du fichier: Simulated PDF loading error."
        )
        assert "loader" not in mock_streamlit.session_state
        assert "docs" not in mock_streamlit.session_state
        mock_streamlit.subheader.assert_not_called()

# --- Tests pour l'option "Entrer une URL" ---

def test_upload_from_url_successful(mock_streamlit):
    """
    Test que simula la subida exitosa de un archivo PDF desde una URL.
    """
    mock_streamlit.radio.return_value = "Entrer une URL"
    mock_streamlit.text_input.return_value = "http://example.com/test.pdf"
    mock_streamlit.button.return_value = True # Simula que el botón fue clickeado

    # Mockear WebBaseLoader
    with patch('app.WebBaseLoader') as mock_web_base_loader:
        mock_loader_instance = MagicMock()
        mock_loader_instance.load.return_value = ["url_doc_page1"]
        mock_web_base_loader.return_value = mock_loader_instance
        
        upload_file()
        
        mock_streamlit.radio.assert_called_once()
        mock_streamlit.text_input.assert_called_once_with("Entrez l'URL du fichier pdf")
        mock_streamlit.button.assert_called_once_with("Charger le fichier depuis l'URL")
        
        mock_web_base_loader.assert_called_once_with("http://example.com/test.pdf", encoding='latin-1')
        assert mock_streamlit.session_state.loader == mock_loader_instance
        assert mock_streamlit.session_state.docs == ["url_doc_page1"]
        mock_streamlit.subheader.assert_called_once_with("Fichier chargé depuis l'URL")
        mock_streamlit.warning.assert_not_called()
        mock_streamlit.error.assert_not_called()

def test_upload_from_url_empty_url(mock_streamlit):
    """
    Test que simula el intento de cargar desde URL sin introducir una URL.
    """
    mock_streamlit.radio.return_value = "Entrer une URL"
    mock_streamlit.text_input.return_value = "" # URL vacía
    mock_streamlit.button.return_value = True

    upload_file()
    
    mock_streamlit.warning.assert_called_once_with("Veuillez entrer une URL valide.")
    mock_streamlit.error.assert_not_called()
    mock_streamlit.subheader.assert_not_called()
    assert "loader" not in mock_streamlit.session_state
    assert "docs" not in mock_streamlit.session_state

def test_upload_from_url_loading_error(mock_streamlit):
    """
    Test que simula un error durante la carga desde URL.
    """
    mock_streamlit.radio.return_value = "Entrer une URL"
    mock_streamlit.text_input.return_value = "http://bad-url.com/invalid.pdf"
    mock_streamlit.button.return_value = True

    # Mockear WebBaseLoader pour que levante une exception
    with patch('app.WebBaseLoader') as mock_web_base_loader:
        mock_web_base_loader.side_effect = Exception("Simulated URL loading error.")
        
        upload_file()
        
        mock_streamlit.error.assert_called_once_with(
            "Erreur lors du chargement: Simulated URL loading error."
        )
        mock_streamlit.subheader.assert_not_called()
        mock_streamlit.warning.assert_not_called()
        assert "loader" not in mock_streamlit.session_state
        assert "docs" not in mock_streamlit.session_state

def test_initial_state_no_action(mock_streamlit):
    """
    Test que verifica el estado inicial cuando no se realiza ninguna acción (ej. sin botón clickeado).
    """
    mock_streamlit.radio.return_value = "Entrer une URL" # O "Télécharger un fichier pdf"
    mock_streamlit.text_input.return_value = "http://example.com/test.pdf"
    mock_streamlit.button.return_value = False # Simula que el botón NO fue clickeado

    upload_file()

    # Asurez-vous que WebBaseLoader et PyPDFLoader n'ont pas été appelés
    with patch('app.WebBaseLoader') as mock_web_base_loader:
        mock_web_base_loader.assert_not_called()
    with patch('app.PyPDFLoader') as mock_pdf_loader:
        mock_pdf_loader.assert_not_called()

    mock_streamlit.warning.assert_not_called()
    mock_streamlit.error.assert_not_called()
    mock_streamlit.subheader.assert_not_called()
    assert "loader" not in mock_streamlit.session_state
    assert "docs" not in mock_streamlit.session_state

   