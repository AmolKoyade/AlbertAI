import streamlit as st
import groq

def setup_client():
    """
    Loads the Groq API key from Streamlit Secrets and returns an authenticated client.
    Stops the app with a clear message if the key is missing or empty.
    """
    try:
        API_KEY = st.secrets["GROQ_API_KEY"]

        # FIX: An empty string won't raise a KeyError but will create a
        # broken client that fails on the first API call. Catch it early.
        if not API_KEY or not API_KEY.strip():
            raise ValueError("GROQ_API_KEY is present in secrets but is empty.")

        client = groq.Groq(api_key=API_KEY.strip())
        return client

    except KeyError:
        st.error(
            "⚠️ Setup Error: 'GROQ_API_KEY' not found in Streamlit Secrets. "
            "Go to App Settings → Secrets and add it."
        )
        st.stop()
    except Exception as e:
        st.error(f"⚠️ Setup Error: Could not initialise Groq client — {e}")
        st.stop()