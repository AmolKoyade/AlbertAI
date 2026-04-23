import streamlit as st
from config import setup_client
from image_handler import handle_image_generation
from chat_handler import handle_text_chat
import html

# ─────────────────────────────────────
# CONFIG
# ─────────────────────────────────────
st.set_page_config(
    page_title="Albert AI",
    page_icon="⊞",
    layout="wide"
)

client = setup_client()

# ─────────────────────────────────────
# SESSION STATE (FIXED)
# ─────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ─────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────
with st.sidebar:
    st.markdown("### ⊞ Albert AI")

    uploaded_file = st.file_uploader(
        "Upload file",
        type=["pdf", "docx", "jpg", "png"]
    )

    if uploaded_file:
        safe_name = html.escape(uploaded_file.name)
        st.caption(f"📄 {safe_name}")

    st.divider()

    if st.button("🧹 Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ─────────────────────────────────────
# HEADER
# ─────────────────────────────────────
st.markdown("## 💬 Chat")

# ─────────────────────────────────────
# INTENT DETECTION (OPTIMIZED)
# ─────────────────────────────────────
def is_image_request(prompt: str) -> bool:
    keywords = ["draw", "image", "picture", "generate", "art", "paint"]
    if any(k in prompt.lower() for k in keywords):
        return True

    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"Is this an image request? {prompt}. Answer IMAGE or TEXT."
            }],
            max_tokens=3,
            temperature=0
        )
        return "IMAGE" in resp.choices[0].message.content.upper()
    except:
        return False

# ─────────────────────────────────────
# CHAT HISTORY (FIXED STRUCTURE)
# ─────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image":
            st.image(msg["content"], use_container_width=True)
        else:
            st.markdown(msg["content"])

# ─────────────────────────────────────
# INPUT
# ─────────────────────────────────────
if prompt := st.chat_input("Ask anything..."):

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "type": "text"
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            if is_image_request(prompt):
                response = handle_image_generation(prompt, client)

                st.image(response, use_container_width=True)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "type": "image"
                })

            else:
                response = handle_text_chat(
                    prompt,
                    client,
                    uploaded_file,
                    st.session_state.messages
                )

                st.markdown(response)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "type": "text"
                })