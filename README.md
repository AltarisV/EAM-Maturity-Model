# ALBA - Architecture Landscape and Baseline Analysis

This repository provides a tool for the analysis, management, and visualization of 
**Enterprise Architecture Practices** in a Company. The application enables persistent management as well as interactive visualization.

---

## Features

- Support for multiple maturity models (`alba.csv`, `mehrwert.csv`)
- Multi-language support: models and glossaries available in different languages
- Persistent storage of CSV-based data
- Customizable glossary for terms and concepts
- Flexible configuration via `config.py`

---

## Project Structure

```text
.
├── .devcontainer/           # Development container setup (VS Code / Remote Dev)
├── alba.csv                 # ALBA maturity model
├── mehrwert.csv             # "Mehrwert" maturity model
├── reifegradmodell_de.csv   # German maturity model
├── reifegradmodell_en.csv   # English maturity model
├── app.py                   # Main entry point (Streamlit app)
├── config.py                # Configuration and glossary management
├── core.py                  # Core logic for models and glossary
├── exports.py               # Export functions (Excel & DOCX)
├── requirements.txt         # Python dependencies
├── runtime.txt              # Python runtime definition
└── README.md                # Project documentation
```

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/<USER>/ALBA.git
   cd ALBA
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate    # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Run the Application

Start the Streamlit app:
```bash
streamlit run app.py
```

Once started, the application will open in your browser at:
http://localhost:8501
