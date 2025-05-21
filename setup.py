from setuptools import setup, find_packages

setup(
    name="pdf_summary_app",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.28.0",
        "langchain-community>=0.0.11",
        "google-generativeai>=0.3.0",
    ],
    python_requires=">=3.10",
)