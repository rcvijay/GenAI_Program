import os
import tempfile
import warnings
from pathlib import Path

# -----------------------------------------------------------------------------
# WARNING SUPPRESSIONS & ENVIRONMENT SETTINGS
# -----------------------------------------------------------------------------
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import streamlit as st

# LangChain & Gemini / HuggingFace Imports
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# -----------------------------------------------------------------------------
# FILE PATH CONFIGURATION
# -----------------------------------------------------------------------------
DEFAULT_PDF_PATH = Path("/Users/vijayrc/Desktop/GenAI_Program/buildathon/tamilnadu.pdf").expanduser().resolve()

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AgriConsultant AI - Tamil Nadu",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# ADVANCED CUSTOM STYLING (CSS)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        /* Hero Header Styling */
        .hero-banner {
            background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 50%, #40916c 100%);
            padding: 2.2rem 2rem;
            border-radius: 16px;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0px 8px 24px rgba(45, 106, 79, 0.15);
        }
        .hero-title {
            font-size: 2.3rem;
            font-weight: 700;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 12px;
            color: #ffffff;
        }
        .hero-subtitle {
            font-size: 1.05rem;
            color: #d8f3dc;
            margin-top: 8px;
            margin-bottom: 0px;
        }

        /* Metric Cards */
        .metric-card {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-left: 5px solid #2d6a4f;
            padding: 1rem 1.2rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }
        .metric-label {
            font-size: 0.85rem;
            color: #6c757d;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .metric-value {
            font-size: 1.3rem;
            font-weight: 700;
            color: #1b4332;
            margin-top: 4px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        /* Chat Styling */
        .stChatMessage {
            border-radius: 12px;
            padding: 12px 16px;
            margin-bottom: 8px;
        }
        
        /* Context Inspector Card */
        .stExpander {
            border: 1px solid #e0e0e0 !important;
            border-radius: 10px !important;
            background-color: #fdfdfd;
        }

        /* Sidebar Cleanup */
        section[data-testid="stSidebar"] {
            background-color: #f4f7f5;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# SIDEBAR CONFIGURATION
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🌾 AgriConsultant")
    st.caption("AI-Powered RAG Portal for TN Agriculture")
    st.divider()

    st.markdown("### ⚙️ Engine Settings")
    selected_model = st.selectbox(
        "Gemini Model",
        [
            "gemini-3.6-flash",
        ],
        index=0,
        help="Active model configured for this application."
    )

    st.markdown("### 🔑 API Key")
    # SAFE SECRET CHECK: Prevents StreamlitSecretNotFoundError
    secret_key = ""
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            secret_key = st.secrets["GOOGLE_API_KEY"]
    except Exception:
        pass

    if not secret_key:
        secret_key = os.environ.get("GOOGLE_API_KEY", "")

    api_key_input = st.text_input(
        "Google AI Studio Key",
        value=secret_key,
        type="password",
        help="Paste your API key starting with AIzaSy...",
    )
    
    GOOGLE_API_KEY = api_key_input

    st.markdown("### 📄 Knowledge Source")
    use_default_pdf = st.checkbox("Use TN Schemes PDF (Default)", value=True)
    uploaded_file = None
    if not use_default_pdf:
        uploaded_file = st.file_uploader("Upload Agricultural PDF", type=["pdf"])

    if use_default_pdf and DEFAULT_PDF_PATH.exists():
        st.success(f"Loaded: `{DEFAULT_PDF_PATH.name}`", icon="✅")

    st.divider()
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# -----------------------------------------------------------------------------
# HELPER & PROCESSING FUNCTIONS
# -----------------------------------------------------------------------------
def format_docs(docs):
    return "\n\n".join(
        f"[Page {doc.metadata.get('page', 'N/A')}]: {doc.page_content}" for doc in docs
    )

@st.cache_resource(show_spinner="🌱 Indexing PDF knowledge base...")
def process_pdf_from_bytes(pdf_bytes: bytes, file_name: str):
    """Processes PDF bytes safely into FAISS vector database."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(pdf_bytes)
        temp_path = tmp_file.name

    try:
        loader = PyPDFLoader(temp_path)
        docs = loader.load()

        if not docs:
            raise ValueError("The PDF file appears to be empty or unreadable.")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
        splits = text_splitter.split_documents(docs)

        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
        )

        vectorstore = FAISS.from_documents(splits, embeddings)
        return vectorstore, len(docs), len(splits)

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

# Safe Stream Helper to avoid socket/generator crashes in Python 3.14
def generate_stream_response(chain, inputs):
    try:
        for chunk in chain.stream(inputs):
            yield chunk
    except Exception as err:
        yield f"\n\n*(Stream error occurred: {str(err)})*"

# -----------------------------------------------------------------------------
# HERO HEADER & DASHBOARD
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-title">🌾 Agricultural Inputs Subsidy Assistant</div>
        <div class="hero-subtitle">Get instant answers on subsidies, seed distribution, equipment, and government schemes in Tamil Nadu.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# API Key Check
if not GOOGLE_API_KEY:
    st.info("💡 Please enter your **Google API Key** in the sidebar to get started.")
    st.stop()

pdf_bytes = None
document_name = ""

# Source Selection Logic
if uploaded_file is not None:
    pdf_bytes = uploaded_file.getvalue()
    document_name = uploaded_file.name
elif use_default_pdf and DEFAULT_PDF_PATH.exists():
    with open(DEFAULT_PDF_PATH, "rb") as f:
        pdf_bytes = f.read()
    document_name = DEFAULT_PDF_PATH.name
elif use_default_pdf and not DEFAULT_PDF_PATH.exists():
    st.error(f"⚠️ Built-in PDF file not found at path: `{DEFAULT_PDF_PATH}`")
    st.stop()

if GOOGLE_API_KEY and pdf_bytes:
    try:
        # Vectorize Document
        vectorstore, total_pages, total_chunks = process_pdf_from_bytes(pdf_bytes, document_name)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

        # Dashboard KPI Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f"""<div class="metric-card">
                    <div class="metric-label">Active Document</div>
                    <div class="metric-value" title="{document_name}">{document_name}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"""<div class="metric-card">
                    <div class="metric-label">Document Depth</div>
                    <div class="metric-value">{total_pages} Pages</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f"""<div class="metric-card">
                    <div class="metric-label">Knowledge Base</div>
                    <div class="metric-value">{total_chunks} Chunks Indexed</div>
                </div>""",
                unsafe_allow_html=True,
            )

        st.write("")
        st.write("")

        # RAG System Prompt
        system_prompt = (
            "You are an expert advisor for agricultural schemes and subsidies in Tamil Nadu. "
            "Use the provided document context to answer questions clearly, accurately, and thoroughly. "
            "Where applicable, state exact subsidy amounts, application steps, eligible beneficiary criteria, "
            "and contact officials (like Assistant Agricultural Officer at Village Level).\n\n"
            "If the information is not present in the document, state that clearly.\n\n"
            "Context:\n{context}"
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{question}"),
            ]
        )

        # Temperature parameter omitted to stop gemini-3.6-flash warnings
        llm = ChatGoogleGenerativeAI(
            model=selected_model,
            google_api_key=GOOGLE_API_KEY,
        )

        rag_chain = (
            {
                "context": lambda x: format_docs(x["retrieved_docs"]),
                "chat_history": lambda x: x["chat_history"],
                "question": lambda x: x["question"],
            }
            | prompt
            | llm
            | StrOutputParser()
        )

        # Initialize Session Chat Memory
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Render Quick Question Prompt Chips if conversation hasn't started
        selected_prompt = None
        if len(st.session_state.messages) == 0:
            st.markdown("**💡 Common Questions:**")
            chip_col1, chip_col2, chip_col3 = st.columns(3)
            with chip_col1:
                if st.button("🌱 What seed subsidies are available?", use_container_width=True):
                    selected_prompt = "What seed subsidies are available?"
            with chip_col2:
                if st.button("🚜 What are the tractor hiring charges?", use_container_width=True):
                    selected_prompt = "What are the tractor hiring charges?"
            with chip_col3:
                if st.button("💦 How to apply for micro-irrigation?", use_container_width=True):
                    selected_prompt = "How to apply for micro-irrigation subsidy?"

        # Render History
        for message in st.session_state.messages:
            avatar = "🧑‍🌾" if message["role"] == "user" else "🤖"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

        # Capture User Input from standard chat bar or prompt chip
        user_query = st.chat_input("Ask about seed subsidies, tractor hiring, pump sets...")
        if selected_prompt:
            user_query = selected_prompt

        if user_query:
            # Render Human Query
            with st.chat_message("user", avatar="🧑‍🌾"):
                st.markdown(user_query)

            # Vector retrieval
            retrieved_docs = retriever.invoke(user_query)

            # Format Memory
            chat_history = [
                HumanMessage(content=msg["content"])
                if msg["role"] == "user"
                else AIMessage(content=msg["content"])
                for msg in st.session_state.messages
            ]

            # Streaming Response using the safe generator wrapper
            with st.chat_message("assistant", avatar="🤖"):
                inputs = {
                    "question": user_query,
                    "retrieved_docs": retrieved_docs,
                    "chat_history": chat_history,
                }
                full_answer = st.write_stream(generate_stream_response(rag_chain, inputs))

                # Context Inspector
                with st.expander("🔍 View Referenced Sources"):
                    for idx, doc in enumerate(retrieved_docs):
                        page_num = doc.metadata.get("page", "N/A")
                        page_display = page_num + 1 if isinstance(page_num, int) else page_num
                        st.markdown(f"**Source Chunk {idx + 1} (Page {page_display}):**")
                        st.caption(doc.page_content)
                        if idx < len(retrieved_docs) - 1:
                            st.divider()

            # Save to Memory
            st.session_state.messages.append({"role": "user", "content": user_query})
            st.session_state.messages.append({"role": "assistant", "content": full_answer})

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
elif not uploaded_file and not use_default_pdf:
    st.info("👈 Please upload an Agricultural PDF document in the sidebar to begin.")