import os
import tempfile
from pathlib import Path

import streamlit as st

# LangChain & OpenAI / HuggingFace Imports
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

# -----------------------------------------------------------------------------
# ENVIRONMENT SETTINGS
# -----------------------------------------------------------------------------
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# -----------------------------------------------------------------------------
# FILE PATH CONFIGURATION
# -----------------------------------------------------------------------------
DEFAULT_PDF_PATH = Path("/Users/vijayrc/Desktop/GenAI_Program/buildathon/tamilnadu.pdf").expanduser().resolve()

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AgriConsultant AI - Tamil Nadu",
    page_icon="🌾",
    layout="wide",
)

st.markdown(
    """
    <style>
        .main-header {
            font-size: 2.2rem;
            color: #2E7D32;
            font-weight: 700;
            margin-bottom: 0px;
        }
        .sub-header {
            font-size: 1.05rem;
            color: #4CAF50;
            margin-bottom: 20px;
        }
        .stChatMessage {
            border-radius: 10px;
            padding: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# SIDEBAR CONFIGURATION
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("🌾 AgriConsultant Config")
    st.caption("Interactive PDF RAG Assistant")
    st.divider()

    st.subheader("🤖 1. OpenAI Model Selection")
    selected_model = st.selectbox(
        "Select OpenAI Model",
        [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-3.5-turbo",
        ],
        index=0,
    )

    st.subheader("🔑 2. OpenAI API Key")
    api_key_input = st.text_input(
        "Enter OpenAI Key (sk-...)",
        type="password",
        help="Paste your API key starting with sk-...",
    )

    # Resolve API Key (Sidebar input takes priority, falls back to environment variable)
    OPENAI_API_KEY = ""

    st.subheader("📄 3. Document Source")
    use_default_pdf = st.checkbox("Use built-in Tamil Nadu PDF", value=True)
    uploaded_file = None
    if not use_default_pdf:
        uploaded_file = st.file_uploader("Upload Agricultural PDF", type=["pdf"])

    if DEFAULT_PDF_PATH.exists():
        st.caption(f"Default Source: `{DEFAULT_PDF_PATH.name}`")

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

        # Local HuggingFace embeddings
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
st.markdown('<p class="main-header">🌾 Agricultural Inputs Subsidy Assistant</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Interactive Q&A for subsidies, seed distribution, equipment, and government schemes.</p>', unsafe_allow_html=True)

# API Key Validation Check
if not OPENAI_API_KEY:
    st.error("⚠️ Please enter your **OpenAI API Key** in the sidebar.")
elif not OPENAI_API_KEY.startswith("sk-"):
    st.warning("⚠️ The entered API key does not look like a standard OpenAI key starting with `sk-`.")

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

if OPENAI_API_KEY and pdf_bytes:
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

        st.divider()

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

        # OpenAI LLM initialization
        llm = ChatOpenAI(
            model=selected_model,
            api_key=OPENAI_API_KEY,
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