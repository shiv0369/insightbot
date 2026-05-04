# InsightBot — Conversational AI Data Analyst

InsightBot is a Python-based AI assistant that lets you ask business questions in plain English and get back real answers — complete with SQL queries, interactive charts, and explanations grounded in business reports.

This was my first end-to-end AI project, built to learn how Large Language Models, Retrieval-Augmented Generation (RAG), and modern data tools fit together in a practical analytics workflow.

---

## What It Does

You type a question like:

> "Why did East region sales drop in Q3 2017?"

And InsightBot will:

1. Convert your question into a SQL query using a Large Language Model.
2. Run that query on a SQLite database containing retail sales data.
3. Search a folder of business PDF reports for relevant context.
4. Combine both sources into a final, cited answer.
5. Show you the data table, the chart, the generated SQL, and the source paragraphs from the reports.

The idea was to build something that feels like a real data analyst — one that can both crunch numbers and explain the reasoning behind them.

---

## Architecture

The flow inside the app looks like this:
User Question (English)
|
v
Text-to-SQL using LangChain + Groq Llama 3
|
v
Run SQL on SQLite database
|
v
RAG search using ChromaDB + sentence-transformers
|
v
LLM combines the numbers and the report context
|
v
Final Answer + Chart + Data + SQL + Sources

---

## Tech Stack

| Layer            | Technology                                       |
|------------------|--------------------------------------------------|
| LLM              | Groq Llama 3.3 70B (free tier)                   |
| Framework        | LangChain                                        |
| Database         | SQLite                                           |
| Vector Store     | ChromaDB                                         |
| Embeddings       | sentence-transformers (all-MiniLM-L6-v2)         |
| Visualization    | Plotly                                           |
| Web UI           | Streamlit                                        |
| Language         | Python 3.11                                      |

---

## How to Run It Locally

**1. Clone the repository**

```bash
git clone https://github.com/shiv0369/insightbot.git
cd insightbot
```

**2. Create a virtual environment**

On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

On Mac or Linux:
```bash
python -m venv venv
source venv/bin/activate
```

**3. Install the dependencies**

```bash
pip install -r requirements.txt
```

**4. Add your Groq API key**

Create a file named `.env` in the project root and add this line:
GROQ_API_KEY=your_key_here

You can get a free Groq API key at [console.groq.com](https://console.groq.com). No credit card required.

**5. Build the data and vector store**

Run these once, in order:

```bash
python load_to_db.py
python generate_sample_pdfs.py
python rag_engine.py
```

These scripts load the Superstore sales CSV into SQLite, generate sample quarterly PDF reports, and build the embeddings used for retrieval.

**6. Run the app**

```bash
streamlit run app.py
```

This opens InsightBot in your browser at `http://localhost:8501`.

---

## Features

- Natural-language to SQL conversion using schema-aware few-shot prompting
- Automatic chart selection between bar, line, pie, and KPI based on the shape of the result
- RAG over PDF reports so the bot can explain the "why," not just the "what"
- A safety layer that blocks any non-SELECT SQL query (no DELETE, DROP, UPDATE, etc.)
- Chat history within a session
- CSV download for any result
- Source citations from the original PDF reports

---

## Project Structure

insightbot/
├── app.py                    Streamlit web UI (main entry point)
├── insightbot.py             Command-line version of the bot
├── text_to_sql.py            LLM-powered SQL generation
├── chart_generator.py        Auto chart selection and Plotly rendering
├── rag_engine.py             PDF chunking, embeddings, and retrieval
├── load_to_db.py             CSV to SQLite loader
├── generate_sample_pdfs.py   Generates sample business reports
├── requirements.txt          Python dependencies
├── .env.example              Template for the API key
└── data/
├── superstore.csv
└── reports/              PDF reports used by the RAG layer

---

## Sample Questions to Try

- What were total sales by region?
- Show me the monthly sales trend in 2017.
- What are the top 5 products by revenue?
- Why did East region sales drop in Q3 2017?
- Which sub-categories are losing money?
- Who are the top 10 customers by profit?

---

## What I Learned

Building this project taught me a lot about how modern AI applications actually work in practice:

- How to design prompts that consistently produce valid SQL, including the role of few-shot examples and schema hints.
- How embeddings turn text into searchable vectors, and how a vector database like ChromaDB makes retrieval fast.
- Why RAG is so widely used — it lets a general-purpose LLM answer questions about specific, private data without retraining.
- How to structure a multi-stage pipeline (SQL generation, execution, retrieval, final answer) so that each piece is testable on its own.
- The practical tradeoffs around prompt sensitivity, hallucination, and data inconsistency between sources.

---

## About

Built as a portfolio project to learn and demonstrate modern data analyst skills combined with Generative AI.

Author: Shiv Jariwala  
LinkedIn: linkedin.com/in/shiv-jariwala-6a5667323  
Email: jariwalashiv020303@gmail.com