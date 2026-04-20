import os
import streamlit as st
import groq

def setup_client():
    """
    Loads the Groq API key from environment variables (Railway)
    or Streamlit Secrets (Streamlit Cloud) — works on both platforms.

    Priority:
      1. OS environment variable  → works on Railway, Render, any server
      2. Streamlit secrets        → works on Streamlit Cloud
    """
    API_KEY = None

    # --- Try environment variable first (Railway) ---
    API_KEY = os.environ.get("GROQ_API_KEY")

    # --- Fall back to Streamlit secrets (Streamlit Cloud) ---
    if not API_KEY:
        try:
            API_KEY = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass

    # --- If still not found, show clear error ---
    if not API_KEY or not API_KEY.strip():
        st.error(
            "⚠️ GROQ_API_KEY not found. \n\n"
            "**On Railway:** Go to your service → Variables → add GROQ_API_KEY \n\n"
            "**On Streamlit Cloud:** Go to App Settings → Secrets → add GROQ_API_KEY"
        )
        st.stop()

    try:
        client = groq.Groq(api_key=API_KEY.strip())
        return client
    except Exception as e:
        st.error(f"⚠️ Could not initialise Groq client: {e}")
        st.stop()