
# 📄 Summary PDF avec IA - Résumeur Intelligent

![Banner](https://via.placeholder.com/800x200?text=PDF+Summary+with+Gemini+AI)

Une application Streamlit qui utilise l'IA Gemini de Google pour générer des résumés concis de vos documents PDF.

## ✨ Fonctionnalités

- Résumé automatique de PDFs locaux ou en ligne
- Support pour documents longs (segmentation intelligente)
- Interface simple et intuitive
- Téléchargement des résumés au format texte
- Intégration avec l'API Gemini 1.5 Pro

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.10+
- Clé API Google Gemini ([obtenez-la ici](https://aistudio.google.com/app/apikey))

### Installation

1. **Cloner le dépôt**:
   ```bash
   git clone https://github.com/votre-utilisateur/pdf-summary-app.git
   cd pdf-summary-app

## structure du projet

```bash
pdf-summary-app/
    ├── .github/
    │    └── workflows/
    │    └── test.yml
    ├── tests/
    │   ├── __init__.py
    │   └── test_app.py
    ├── app.py
    ├── pytest.ini
    ├── requirements.txt
    └── setup.py
````

**Virtual environnement**
```bash
python -m venv .venv
```
> .venv is the name of the virtual environnement 

**Connect to the venv** 

- mac/linux
`source .venv/bin/activate.fish`
- windows
`.venv/Scripts/activate` or `.venv/Scripts/activate.ps1` 

**Installez les dépendances**
Assurez-vous d'avoir Python installé, puis exécutez :
```bash
pip install -r requirements.txt
```

**Quit venv**
`deactivate` 