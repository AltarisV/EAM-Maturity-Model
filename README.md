# EAM-Maturity-Model

Dieses Repository stellt ein Werkzeug zur Analyse, Verwaltung und Visualisierung von **Enterprise Architecture Maturity Models** bereit.  
Die Anwendung kombiniert verschiedene Reifegradmodelle (z. B. in Deutsch und Englisch) und ermöglicht deren persistente Verwaltung sowie Visualisierung.

---

## 🚀 Features

- 📊 Unterstützung Reifegradmodel (`alba.csv`, `mehrwert.csv`)  
- 🌐 Mehrsprachigkeit: Modelle und Glossare in verschiedenen Sprachen  
- 🗂️ Persistente Speicherung und Verarbeitung der CSV-Daten  
- 🔎 Anpassbares Glossar für Begriffe und Konzepte  
- ⚙️ Flexible Konfiguration über `config.py`

---

## 📂 Projektstruktur
```
.
├── .devcontainer/ # Dev-Container Setup (VS Code / Remote Dev)
├── alba.csv # ALBA Reifegradmodell
├── mehrwert.csv # Mehrwertmodell
├── reifegradmodell_de.csv # Deutsches Reifegradmodell
├── reifegradmodell_en.csv # Englisches Reifegradmodell
├── app.py # Haupteinstiegspunkt (z. B. Flask/FastAPI/CLI)
├── config.py # Konfiguration & Glossarverwaltung
├── core.py # Zentrale Logik für Modelle und Glossar
├── exports.py # Exportfunktionen (z. B. Visualisierung, Reports)
├── requirements.txt # Python-Abhängigkeiten
├── runtime.txt # Python-Runtime Definition
└── README.md # Projektdokumentation
```

---

## ⚙️ Installation

1. Repository klonen:
```bash
git clone https://github.com/<USER>/EAM-Maturity-Model.git
cd EAM-Maturity-Model
```

2. Virtuelle Umgebung erstellen & aktivieren:

```python 
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

3. Abhängigkeiten installieren:

```python 
pip install -r requirements.txt
```

4. Nutzung

Starte die Streamlit-App mit:
```python 
streamlit run app.py
```

Danach öffnet sich die App automatisch im Browser unter:
👉 http://localhost:8501 


