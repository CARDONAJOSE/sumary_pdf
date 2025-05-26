import pytest
from unittest.mock import patch, MagicMock
import streamlit as st

@pytest.fixture(autouse=True)
def mock_streamlit():
    with patch('streamlit.radio'), \
         patch('streamlit.file_uploader'), \
         patch('streamlit.text_input'), \
         patch('streamlit.button'), \
         patch('streamlit.text_area'), \
         patch('streamlit.download_button'), \
         patch('streamlit.session_state', new_callable=MagicMock):
        yield

@pytest.fixture(autouse=True)
def mock_genai():
    with patch('google.generativeai.configure'), \
         patch('google.generativeai.GenerativeModel'), \
         patch('google.generativeai.list_models'):
        yield