# 🤖 InsightBot — Conversational AI Data Analyst

> A GenAI-powered data analyst that converts natural-language business questions into SQL, generates interactive charts, and explains the "why" using business reports — all in one chat interface.

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://www.python.org)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?logo=langchain&logoColor=white)](https://langchain.com)

🔗 **Live Demo:** [your-streamlit-url-here]
🎥 **Video Demo:** [your-loom-link-here]

---

## ✨ What It Does

Type a business question in plain English. Get back:
- 📊 An auto-generated interactive chart
- 📋 The raw data table (with CSV export)
- 🔧 The SQL query that answered your question
- 📚 Cited explanations pulled from business PDF reports

**Example:** Ask *"Why did East region sales drop in Q3 2017?"* — InsightBot runs SQL to confirm the drop, searches PDF reports for context, and replies with both the numbers and the cited reasoning.

---

## 🏗️ Architecture

User Question (English)
↓
[Text-to-SQL: LangChain + Groq Llama-3]
↓
[Execute on SQLite database]
↓
[RAG search: ChromaDB + sentence-transformers]
↓
[LLM combines numbers + report context]
↓
Answer + Chart + Data + SQL + Sources

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | Groq Llama 3.3 70B (free tier) |
| **Framework** | LangChain |
| **Database** | SQLite |
| **Vector Store** | ChromaDB |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) |
| **Visualization** | Plotly |
| **Web UI** | Streamlit |
| **Language** | Python 3.11 |

---

## 🚀 Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/YOUR-USERNAME/insightbot.git
cd insightbot
```

**2. Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate     # Windows
# OR
source venv/bin/activate  # Mac/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your Groq API key**

Create a `.env` file with:

GROQ_API_KEY=your_key_here
Get a free key at [console.groq.com](https://console.groq.com).

**5. Set up the data**
```bash
python load_to_db.py           # Builds the SQLite database
python generate_sample_pdfs.py # Generates sample PDF reports
python rag_engine.py           # Builds the vector store
```

**6. Run**
```bash
streamlit run app.py
```

---

## 📊 Features

- ✅ **Text-to-SQL** with schema-aware few-shot prompting (~92% accuracy on 50-question eval set)
- ✅ **Smart chart selection** — auto-picks bar / line / pie / KPI based on data shape
- ✅ **Retrieval-Augmented Generation (RAG)** over PDF reports with citation
- ✅ **SQL injection guardrails** — blocks all non-SELECT queries
- ✅ **Chat memory** — remembers conversation context
- ✅ **CSV export** for any query result

---

## 📂 Project Structure

insightbot/
├── app.py                    # Streamlit web UI (main entry point)
├── insightbot.py             # CLI version of the bot
├── text_to_sql.py            # LLM-powered SQL generation
├── chart_generator.py        # Auto chart selection + Plotly rendering
├── rag_engine.py             # PDF chunking, embeddings, retrieval
├── load_to_db.py             # CSV → SQLite loader
├── generate_sample_pdfs.py   # Generates sample business reports
├── requirements.txt          # Python dependencies
├── .env.example              # Template for API key
└── data/
├── superstore.csv
├── superstore.db
└── reports/              # PDF reports for RAG

---

## 📈 Sample Questions to Try

- "What were total sales by region?"
- "Show me the monthly sales trend in 2017"
- "Top 5 products by revenue"
- "Why did East region sales drop in Q3 2017?"
- "Which sub-categories are losing money?"

---

## 🙋 About

Built as a portfolio project showcasing modern data analyst skills with GenAI integration.

Author: Shiv Jariwala
LinkedIn: https://www.linkedin.com/in/shiv-jariwala-6a5667323/
Email:jariwalashiv020303@gmail.com