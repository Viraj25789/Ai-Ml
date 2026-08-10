from utils.extract_vid_id import extract_video_id
from utils.transcript import get_youtube_transcript
from rag_engine import build_vector_store, create_rag_chain

import streamlit as st
import os
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"

# Import our custom modules
from utils.extract_vid_id import extract_video_id
from utils.transcript import get_youtube_transcript
from rag_engine import build_vector_store, create_rag_chain

# --- Page Configuration ---
st.set_page_config(page_title="VidBrain - YouTube RAG", layout="centered")
st.title("VidBrain: YouTube Transcript Analyzer")
st.markdown("Turn any YouTube tutorial into an interactive, searchable knowledge base.")

# --- Load API Key ---
try:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error("Missing API Key. Please add GROQ_API_KEY to your Streamlit secrets.")
    st.stop()

# --- Session State Initialization ---
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "current_video_id" not in st.session_state:
    st.session_state.current_video_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- UI: Video Input ---
video_url = st.text_input("Paste a YouTube Video URL here:")

if video_url:
    # Use our utils file to get the ID
    video_id = extract_video_id(video_url)

    if not video_id:
        st.error("Invalid URL format. Please use a standard YouTube link.")
    
    # Process New Video
    elif video_id != st.session_state.current_video_id:
        st.session_state.chat_history = [] # Clear history for new video
        
        with st.spinner("Downloading transcript and building vector index..."):
            # Use our data file to get the text
            text = get_youtube_transcript(video_id)
            
            if text:
                # Use our rag_engine to build the database
                st.session_state.vector_store = build_vector_store(text)
                st.session_state.current_video_id = video_id
                
                st.success("Video processed successfully! Ask your questions below.")
            else:
                st.error("Could not fetch transcript. Ensure closed captions are enabled on this video.")
                st.session_state.vector_store = None
                st.session_state.current_video_id = None

    # --- UI: Chat Interface ---
    if st.session_state.vector_store is not None:
        st.divider()
        st.subheader("Chat with the Video")
        
        # Display chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        # Chat input
        user_question = st.chat_input("What do you want to know about this video?")
        
        if user_question:
            # Show user message
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            with st.chat_message("user"):
                st.markdown(user_question)
                
            # Generate AI response
            with st.chat_message("assistant"):
                with st.spinner("Analyzing transcript..."):
                    
                    # Use our rag_engine to create the response chain
                    rag_chain = create_rag_chain(st.session_state.vector_store)
                    
                    response = rag_chain.invoke({"input": user_question})
                    answer = response["answer"]
                    
                    st.markdown(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})