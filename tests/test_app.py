import pytest
from unittest.mock import patch, MagicMock
import tempfile
import os
from io import BytesIO
import streamlit as st

# Mock pour Streamlit
@pytest.fixture
def mock_streamlit():
    with patch('streamlit.text_input'), \
         patch('streamlit.radio'), \
         patch('streamlit.file_uploader'), \
         patch('streamlit.button'), \
         patch('streamlit.session_state'), \
         patch('streamlit.text_area'), \
         patch('streamlit.download_button'), \
         patch('streamlit.error'), \
         patch('streamlit.warning'), \
         patch('streamlit.success'), \
         patch('streamlit.subheader'):
        yield

# Mock pour Google GenerativeAI
@pytest.fixture
def mock_genai():
    with patch('google.generativeai.configure'), \
         patch('google.generativeai.GenerativeModel'), \
         patch('google.generativeai.list_models'):
        yield

def test_upload_pdf_file(mock_streamlit, mock_genai):
    from app import upload_file
    
    # Mock du fichier uploadé
    mock_file = MagicMock()
    mock_file.read.return_value = b"PDF content"
    
    # Configurer les mocks Streamlit
    st.radio.return_value = "Télécharger un fichier pdf"
    st.file_uploader.return_value = mock_file
    
    # Appeler la fonction
    upload_file()
    
    # Vérifier que le fichier a été traité
    assert 'docs' in st.session_state

def test_load_from_url(mock_streamlit, mock_genai):
    from app import upload_file
    
    # Configurer les mocks Streamlit
    st.radio.return_value = "Entrer une URL"
    st.text_input.return_value = "http://example.com/test.pdf"
    st.button.return_value = True
    
    # Mock WebBaseLoader
    with patch('langchain_community.document_loaders.WebBaseLoader') as mock_loader:
        mock_loader.return_value.load.return_value = ["doc1", "doc2"]
        
        # Appeler la fonction
        upload_file()
        
        # Vérifications
        mock_loader.assert_called_once()
        assert 'docs' in st.session_state

def test_generate_summary(mock_streamlit, mock_genai):
    from app import resumir_con_gemini
    
    # Mock de la réponse de Gemini
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Résumé de test"
    mock_model.generate_content.return_value = mock_response
    
    # Configurer le mock
    genai.GenerativeModel.return_value = mock_model
    
    # Appeler la fonction
    result = resumir_con_gemini("Texte à résumer")
    
    # Vérifications
    assert result == "Résumé de test"
    mock_model.generate_content.assert_called_once()