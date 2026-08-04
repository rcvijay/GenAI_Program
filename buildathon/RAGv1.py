import os
import tempfile
from pathlib import Path

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
# ENVIRONMENT SETTINGS
# -----------------------------------------------------------------------------
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# -----------------------------------------------------------------------------
# FILE PATH CONFIGURATION
# -----------------------------------------------------------------------------
DEFAULT_PDF_PATH = Path("/Users/vijayrc/Desktop/GenAI_Program/buildathon/Goverment_schems.pdf").expanduser().resolve()

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & MODERN STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AgriConsultant AI - Tamil Nadu",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern Dark Emerald Theme
st.markdown(
    """
    <style>
        /* Main Theme Overrides */
        .stApp {
            background-color: #0d1117;
            color: #e6edf3;
        }
        
        /* Custom Header Styling */
        .main-header-container {
            background: linear-gradient(135deg, #064e3b 0%, #022c22 100%);
            border: 1px solid #059669;
            padding: 24px 30px;
            border-radius: 16px;
            margin-bottom: 25px;
            box-shadow: 0 10px 25px -5px rgba(5, 150, 105, 0.15);
        }
        .main-title {
            font-size: 2.2rem;
            color: #ecfdf5;
            font-weight: 800;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .sub-title {
            font-size: 1.05rem;
            color: #a7f3d0;
            margin-top: 8px;
            margin-bottom: 0;
            font-weight: 400;
        }

        /* Metric Box Enhancements */
        div[data-testid="stMetric"] {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 14px 18px;
            transition: all 0.3s ease;
        }
        div[data-testid="stMetric"]:hover {
            border-color: #10b981;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.1);
        }
        div[data-testid="stMetricLabel"] {
            color: #9ca3af !important;
            font-weight: 500;
        }
        div[data-testid="stMetricValue"] {
            color: #34d399 !important;
            font-weight: 700;
        }

        /* Chat Message Styling */
        .stChatMessage {
            background-color: #161b22 !important;
            border: 1px solid #21262d !important;
            border-radius: 12px !important;
            padding: 16px !important;
            margin-bottom: 12px !important;
        }

        /* Sidebar Customizations */
        section[data-testid="stSidebar"] {
            background-color: #161b22;
            border-right: 1px solid #30363d;
        }
        
        /* Expanders styling */
        .streamlit-expanderHeader {
            background-color: #161b22 !important;
            border-radius: 8px !important;
            color: #34d399 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# SIDEBAR CONFIGURATION
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("🌾 AgriConsultant")
    st.caption("Interactive PDF RAG Assistant")
    st.divider()

    st.markdown("### 🤖 Model Selection")
    selected_model = st.selectbox(
        "Select Gemini Model",
        ["gemini-3.6-flash"],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("### 🔑 API Key Configuration")
    api_key_input = st.text_input(
        "Google API Key",
        type="password",
        placeholder="Paste AIzaSy... key here",
        help="Paste your API key starting with AIzaSy...",
    )
    
    # Priority given to user sidebar input for safety
    GOOGLE_API_KEY = api_key_input or os.environ.get("GOOGLE_API_KEY", "")

    st.markdown("### 📄 Document Source")
    use_default_pdf = st.checkbox("Use built-in Tamil Nadu PDF", value=True)
    uploaded_file = None
    if not use_default_pdf:
        uploaded_file = st.file_uploader("Upload Agricultural PDF", type=["pdf"])

    if DEFAULT_PDF_PATH.exists():
        st.caption(f"📁 **Default Source:** `{DEFAULT_PDF_PATH.name}`")

    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# -----------------------------------------------------------------------------
# HELPER & PROCESSING FUNCTIONS
# -----------------------------------------------------------------------------
def format_docs(docs):
    return "\n\n".join(
        f"[Page {doc.metadata.get('page', 'N/A')}]: {doc.page_content}" for doc in docs
    )


@st.cache_resource(show_spinner="🌱 Indexing PDF with local vector embeddings...")
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

# -----------------------------------------------------------------------------
# MAIN INTERACTIVE APP INTERFACE
# -----------------------------------------------------------------------------
# Custom Styled Banner Header
st.markdown(
    """
    <div class="main-header-container">
        <div class="main-title">🌾 Agricultural Inputs Subsidy Assistant</div>
        <div class="sub-title">Interactive AI Q&A for subsidies, seed distribution, equipment, and govt schemes in Tamil Nadu</div>
    </div>
    """,
    unsafe_allow_html=True
)

# API Key Validation Check
if not GOOGLE_API_KEY:
    st.info("👈 Please enter your **Google API Key** in the sidebar to start asking questions.")
elif not GOOGLE_API_KEY.startswith("AIzaSy"):
    st.warning("⚠️ The entered API key does not start with `AIzaSy`. Make sure you are using a key generated from Google AI Studio.")

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

if GOOGLE_API_KEY and pdf_bytes:
    try:
        # Vectorize Document
        vectorstore, total_pages, total_chunks = process_pdf_from_bytes(pdf_bytes, document_name)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

        # Dashboard Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Loaded Document", document_name)
        with col2:
            st.metric("Total Pages", total_pages)
        with col3:
            st.metric("Indexed Chunks", total_chunks)

        st.markdown("<br>", unsafe_allow_html=True)

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

        # Gemini LLM initialization
        llm = ChatGoogleGenerativeAI(
            model=selected_model,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.2,
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

        # Render Previous Conversation
        for message in st.session_state.messages:
            avatar = "🧑‍🌾" if message["role"] == "user" else "🤖"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

        # Interactive User Input Bar
        if user_query := st.chat_input("Ask about seed subsidies, tractor hiring rates, pump sets..."):
            
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

            # Streaming Response to Streamlit UI
            with st.chat_message("assistant", avatar="🤖"):
                stream_response = rag_chain.stream(
                    {
                        "question": user_query,
                        "retrieved_docs": retrieved_docs,
                        "chat_history": chat_history,
                    }
                )
                full_answer = st.write_stream(stream_response)

                # Expandable Context Inspector
                with st.expander("🔍 View Retrieved Context Sources"):
                    for idx, doc in enumerate(retrieved_docs):
                        page_num = doc.metadata.get("page", "N/A")
                        st.markdown(
                            f"**Source Chunk {idx + 1} (Page {page_num + 1 if isinstance(page_num, int) else page_num}):**"
                        )
                        st.caption(doc.page_content)
                        st.divider()

            # Store Turn in Memory
            st.session_state.messages.append({"role": "user", "content": user_query})
            st.session_state.messages.append({"role": "assistant", "content": full_answer})

    except Exception as e:
        st.error(f"An error occurred while running the app: {str(e)}")
elif not uploaded_file and not use_default_pdf:
    st.info("👈 Please upload an Agricultural PDF document in the sidebar.")