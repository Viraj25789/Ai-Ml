
import os

import streamlit as st

from rag_engine import build_vector_store, create_rag_chain
from utils.extract_vid_id import extract_video_id
from utils.transcript import get_youtube_transcript


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"

st.set_page_config(
    page_title="VidBrain - YouTube RAG",
    page_icon="🧠",
    layout="centered",
)

st.title("🧠 VidBrain")
st.caption("Turn YouTube tutorials into searchable learning assistants.")

# --------------------------------------------------
# Session state
# --------------------------------------------------

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "current_video_id" not in st.session_state:
    st.session_state.current_video_id = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "video_error" not in st.session_state:
    st.session_state.video_error = None


# --------------------------------------------------
# API key helper
# --------------------------------------------------

def get_groq_api_key():
    """Read the Groq key from Streamlit secrets or environment."""

    try:
        key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        key = ""

    return key or os.getenv("GROQ_API_KEY", "")


# --------------------------------------------------
# YouTube video processing
# --------------------------------------------------

video_url = st.text_input(
    "YouTube video URL",
    placeholder="https://www.youtube.com/watch?v=...",
)

# Clear the previous video's data as soon as the URL field is emptied.
# Otherwise, the old vector store remains active and the old chat is still usable.
if not video_url.strip():
    st.session_state.vector_store = None
    st.session_state.current_video_id = None
    st.session_state.chat_history = []
    st.session_state.video_error = None

if video_url.strip():
    video_id = extract_video_id(video_url.strip())

    if not video_id:
        st.session_state.vector_store = None
        st.session_state.current_video_id = None
        st.session_state.chat_history = []
        st.session_state.video_error = "Please enter a valid YouTube video URL."
        st.error(st.session_state.video_error)

    elif video_id != st.session_state.current_video_id:
        # Clear previous video's data before processing a new video.
        st.session_state.vector_store = None
        st.session_state.current_video_id = None
        st.session_state.chat_history = []
        st.session_state.video_error = None

        try:
            with st.spinner("Fetching transcript and building search index..."):
                transcript = get_youtube_transcript(video_id)

                if not transcript:
                    raise ValueError(
                        "No usable transcript was found. "
                        "This video may not have captions enabled."
                    )

                vector_store = build_vector_store(transcript)

                st.session_state.vector_store = vector_store
                st.session_state.current_video_id = video_id

            st.success("Video processed successfully. You can now ask questions.")

        except Exception as error:
            st.session_state.vector_store = None
            st.session_state.current_video_id = None
            st.session_state.video_error = str(error)
            st.error(f"Could not process this video: {error}")


# --------------------------------------------------
# Chat interface
# --------------------------------------------------

if st.session_state.vector_store is not None:
    st.divider()
    st.subheader("Ask questions about this video")

    # Show previous messages.
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_question = st.chat_input(
        "Ask something explained in the video..."
    )

    if user_question:
        st.session_state.chat_history.append(
            {"role": "user", "content": user_question}
        )

        with st.chat_message("user"):
            st.markdown(user_question)

        with st.chat_message("assistant"):
            api_key = get_groq_api_key()

            if not api_key:
                answer = (
                    "Groq API key is missing. Add `GROQ_API_KEY` "
                    "to your Streamlit secrets or environment variables."
                )
                st.error(answer)

            else:
                os.environ["GROQ_API_KEY"] = api_key

                try:
                    with st.spinner("Searching the transcript..."):
                        rag_chain = create_rag_chain(
                            st.session_state.vector_store
                        )

                        response = rag_chain.invoke(
                            {"input": user_question}
                        )

                        answer = response.get(
                            "answer",
                            "I could not generate an answer. Please try again.",
                        )

                    st.markdown(answer)

                except Exception as error:
                    answer = (
                        "I encountered a problem while generating the answer. "
                        "Please try again."
                    )
                    st.error(answer)
                    st.caption(f"Technical detail: {error}")

            st.session_state.chat_history.append(
                {"role": "assistant", "content": answer}
            )

else:
    # Clear the previous video's session data when the URL is removed.
    st.session_state.vector_store = None
    st.session_state.current_video_id = None
    st.session_state.chat_history = []
    st.session_state.video_error = None
    st.info("Paste a YouTube URL above to start learning from a video.")
