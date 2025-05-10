import os
import openai
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template
from langchain.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# Directory setup
VECTORSTORE_DIR = "pdf_vectorstore"
PDF_UPLOAD_DIR = "uploaded_pdfs"
PRETRAINED_PDF_DIR = "pretrained_pdfs"
os.makedirs(PDF_UPLOAD_DIR, exist_ok=True)
os.makedirs(PRETRAINED_PDF_DIR, exist_ok=True)

# Load FLAN-T5 base model
def load_small_pipeline():
    model_id = "google/flan-t5-base"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_id)

    pipe = pipeline(
        "text2text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=256,
        temperature=0.5,
        top_p=0.9,
    )

    return HuggingFacePipeline(pipeline=pipe)

# Load vectorstore if exists
def load_vectorstore():
    if os.path.exists(VECTORSTORE_DIR):
        return FAISS.load_local(VECTORSTORE_DIR, HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"))
    return None

# Save vectorstore
def save_vectorstore(vectorstore):
    vectorstore.save_local(VECTORSTORE_DIR)

# Load and split PDF text
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return text_splitter.split_text(text)

def get_vectorstore(text_chunks):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vectorstore):
    llm = load_small_pipeline()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )

def get_answer_from_openai(question):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=question,
        max_tokens=150,
        temperature=0.7
    )
    return response.choices[0].text.strip()

# Main app
def main():
    load_dotenv()
    st.set_page_config(page_title="Chat with PDFs", page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    vectorstore = load_vectorstore()

    st.header("Chat with Pre-trained Knowledge Base :books:")
    user_question = st.text_input("Ask a question:")

    if user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})

        if vectorstore:
            if not st.session_state.conversation:
                st.session_state.conversation = get_conversation_chain(vectorstore)

            response = st.session_state.conversation({'question': user_question})
            answer = response.get('answer', '').strip()
        else:
            answer = get_answer_from_openai(user_question)

        st.session_state.chat_history.append({"role": "bot", "content": answer})

    # Display full conversation
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.write(user_template.replace("{{MSG}}", message["content"]), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace("{{MSG}}", message["content"]), unsafe_allow_html=True)

    # PDF Upload
    with st.sidebar:
        st.subheader("Upload New Documents")
        pdf_docs = st.file_uploader("Upload PDFs here:", accept_multiple_files=True)

        if st.button("Process New PDFs") and pdf_docs:
            with st.spinner("Processing PDFs..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)

                if vectorstore is None:
                    vectorstore = get_vectorstore(text_chunks)
                else:
                    new_vectorstore = get_vectorstore(text_chunks)
                    vectorstore.merge_from(new_vectorstore)

                save_vectorstore(vectorstore)
                st.session_state.conversation = get_conversation_chain(vectorstore)
                st.success("New PDFs processed successfully!")

if __name__ == '__main__':
    main()
