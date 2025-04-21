# 🧠 NLP Research
This project focuses on developing an end-to-end NLP pipeline designed to process, analyze, and extract valuable insights from the research materials left behind by Dr. X


---

## ⚙️ Environment Setup

Make sure Python **3.12** is installed.

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Create a Virtual Environment

```bash
python3.12 -m venv venv
```

### 3. Activate the Environment

#### On Linux/macOS:

```bash
source venv/bin/activate
```

#### On Windows:

```bash
venv\Scripts\activate
```

### 4. Install Requirements

```bash
pip install -r requirements.txt
```

---

## 🐳 Ollama Setup

### 5. Install Ollama

Download and install Ollama from the official site:  
👉 [https://ollama.com/download](https://ollama.com/download)

### 6. Run the Model

```bash
ollama run gemma3:4b-it-qat
```

---

## 📒 Jupyter Notebooks

The project is modularized with the following notebooks:

- `data_extraction.ipynb` — Extracts content from documents
- `chunking.ipynb` — Splits extracted content into manageable chunks
- `vector_db.ipynb` — Embeds and stores text chunks in a vector database
- `rag_qa_system.ipynb` — graoh based RAG system for QA
- `translation.ipynb` — Translate text from one language to another 
- 

---

## ✅ Summary

- Python 3.12 environment setup
- Virtual environment and package installation
- Ollama for local LLM inference
- Jupyter notebooks for modular pipeline: extraction → chunking → vector DB, RAG system, Translation module

---

## 🧠 Future Improvements

- [ ] Integrate LangChain for orchestration
- [ ] Build a chatbot interface
- [ ] Add document upload feature
