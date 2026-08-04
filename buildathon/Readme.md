\# AgriConsultant AI \- Tamil Nadu

An interactive, AI-powered Retrieval-Augmented Generation (RAG) assistant designed to help farmers, researchers, and government officials query official agricultural documents, subsidy schemes, seed distribution details, and tractor hiring rates in Tamil Nadu.

Powered by Streamlit, LangChain, Google Gemini, and FAISS.

\#\# Overview

The AgriConsultant AI application simplifies complex agricultural documentation by processing uploaded or built-in PDF documents into a local vector database. Users can ask questions in natural language and receive accurate answers sourced directly from government schemes and policy papers, complete with page citations and source chunk context.

\#\# Features

\- Modern Dark Emerald UI: Custom-styled glassmorphic interface tailored for modern agricultural tech tools.  
\- Local Embeddings: Fast, privacy-preserving document chunking using all-MiniLM-L6-v2 via HuggingFace on CPU.  
\- Vector Search with FAISS: Instant contextual retrieval using local FAISS vector store.  
\- Gemini Models: Seamless integration with Google Gemini LLMs for reasoning and natural language answer generation.  
\- Context-Aware Memory: Conversational chat history enabling multi-turn Q\&A.  
\- Multi-Source Ingestion: Load local default PDFs (tamilnadu.pdf) or upload custom PDF documents on the fly.  
\- Source Citation: Interactive context inspector showing exact document chunks and page numbers used to formulate each answer.

\#\# Architecture & Workflow

1\. Ingestion & Processing: \- PDFs are loaded via PyPDFLoader and split into chunks of 800 characters with a 150-character overlap. \- Embeddings are generated using HuggingFace's all-MiniLM-L6-v2. 2\. Retrieval: \- FAISS retrieves the top 4 most relevant chunks for every query. 3\. Generation: \- Retrieved context and session memory are injected into a specialized agricultural domain prompt and streamed to the user via Gemini. \--- 

\#\# Getting Started \#\#\# 

Prerequisites \-

 Python 3.9 or higher \- A Google Gemini API Key (obtained from Google AI Studio) 

pip install streamlit langchain langchain-community langchain-core langchain-google-genai langchain-huggingface faiss-cpu pypdf sentence-transformers

DEFAULT\_PDF\_PATH \= Path("/Users/vijayrc/Desktop/GenAI\_Program/buildathon/tamilnadu.pdf").expanduser().resolve()

export GOOGLE\_API\_KEY="AIzaSyYourKeyHere..."

streamlit run app.py  
