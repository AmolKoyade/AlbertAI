import streamlit as st
from config import setup_client
from image_handler import handle_image_generation
from chat_handler import handle_text_chat

st.set_page_config(
    page_title="Albert AI",
    page_icon="⊞",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
* { overscroll-behavior-y: none !important; }

html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"] {
    background: #0f0f0f !important;
    color: #c8c8c8 !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}

/* ── MAIN BLOCK ── */
[data-testid="stMain"],
.block-container,
[data-testid="block-container"] {
    background: #0f0f0f !important;
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #141414 !important;
    border-right: 1px solid #1e1e1e !important;
    min-width: 210px !important;
    max-width: 240px !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] > div {
    padding: 20px 14px 16px !important;
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
}
[data-testid="stSidebar"] * {
    color: #888 !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── SIDEBAR CLEAR BUTTON ── */
[data-testid="stSidebar"] .stButton button {
    width: 100% !important;
    background: #161616 !important;
    color: #666 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 8px !important;
    font-size: 12px !important;
    font-weight: 400 !important;
    padding: 8px 0 !important;
    transition: all 0.15s ease !important;
    letter-spacing: 0.01em !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: #1a1a1a !important;
    color: #888 !important;
    border-color: #252525 !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
    background: transparent !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: #161616 !important;
    border: 1px dashed #252525 !important;
    border-radius: 9px !important;
    padding: 10px !important;
    transition: border-color 0.15s !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #333 !important;
}
[data-testid="stFileUploaderDropzone"] * {
    color: #444 !important;
    font-size: 11px !important;
}
[data-testid="stFileUploaderDropzone"] button {
    background: #1e1e1e !important;
    border: 1px solid #252525 !important;
    color: #666 !important;
    border-radius: 6px !important;
    font-size: 11px !important;
}
[data-testid="stFileUploaderDeleteBtn"] button,
[data-testid="stFileUploaderDropzone"] small {
    color: #3a3a3a !important;
    font-size: 10px !important;
}

/* ── HIDE STREAMLIT HEADER & FOOTER ── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {
    display: none !important;
}

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"] {
    background: #161616 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    margin-bottom: 6px !important;
    max-width: 78% !important;
}

/* user messages — right aligned */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: #1a1a1a !important;
    border-color: #222 !important;
    margin-left: auto !important;
    border-radius: 10px 2px 10px 10px !important;
}

/* AI messages — left aligned */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    margin-right: auto !important;
    border-radius: 2px 10px 10px 10px !important;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] li {
    color: #c8c8c8 !important;
    font-size: 13.5px !important;
    line-height: 1.65 !important;
}

/* ── CHAT AVATARS ── */
[data-testid="stChatMessageAvatarUser"] {
    background: #222 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 7px !important;
    color: #999 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    width: 26px !important;
    height: 26px !important;
}
[data-testid="stChatMessageAvatarAssistant"] {
    background: #1e1e1e !important;
    border: 1px solid #252525 !important;
    border-radius: 7px !important;
    color: #888 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    width: 26px !important;
    height: 26px !important;
}

/* ── CHAT INPUT ── */
[data-testid="stBottom"],
[data-testid="stChatInput"] {
    background: #0f0f0f !important;
    border-top: 1px solid #1a1a1a !important;
    padding: 10px 16px !important;
}
[data-testid="stChatInput"] textarea {
    background: #141414 !important;
    color: #c8c8c8 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 9px !important;
    font-size: 13px !important;
    font-family: 'Inter', sans-serif !important;
    caret-color: #f0f0f0 !important;
    padding: 10px 14px !important;
    line-height: 1.5 !important;
    resize: none !important;
    transition: border-color 0.15s !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #3a3a3a !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #2a2a2a !important;
    outline: none !important;
    box-shadow: none !important;
}
[data-testid="stChatInputSubmitButton"] button {
    background: #f0f0f0 !important;
    border: none !important;
    border-radius: 8px !important;
    width: 34px !important;
    height: 34px !important;
    transition: background 0.15s !important;
}
[data-testid="stChatInputSubmitButton"] button:hover {
    background: #fff !important;
}
[data-testid="stChatInputSubmitButton"] svg path {
    stroke: #111 !important;
    fill: none !important;
}

/* ── STATUS BOX ── */
[data-testid="stStatus"],
[data-testid="stStatusContainer"] {
    background: #141414 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 9px !important;
}
[data-testid="stStatus"] *,
[data-testid="stStatusContainer"] * {
    color: #555 !important;
    font-size: 12px !important;
}

/* ── ALERTS ── */
[data-testid="stAlert"] {
    background: #161616 !important;
    border: 1px solid #222 !important;
    border-radius: 9px !important;
    color: #888 !important;
    font-size: 12px !important;
}

/* ── TOAST / WARNING ── */
[data-testid="stNotification"] {
    background: #161616 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 9px !important;
    color: #888 !important;
}

/* ── IMAGES ── */
[data-testid="stImage"] img {
    border-radius: 10px !important;
    border: 1px solid #1e1e1e !important;
}

/* ── DOWNLOAD BUTTON ── */
[data-testid="stDownloadButton"] button {
    background: #161616 !important;
    color: #888 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 8px !important;
    font-size: 12px !important;
    font-weight: 400 !important;
    padding: 8px 14px !important;
    width: 100% !important;
    transition: all 0.15s !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: #1a1a1a !important;
    color: #aaa !important;
}

/* ── MARKDOWN ── */
[data-testid="stMarkdownContainer"] p { color: #c8c8c8 !important; font-size: 13.5px !important; line-height: 1.65 !important; }
[data-testid="stMarkdownContainer"] h1 { color: #f0f0f0 !important; font-size: 18px !important; font-weight: 600 !important; margin-bottom: 8px !important; }
[data-testid="stMarkdownContainer"] h2 { color: #e0e0e0 !important; font-size: 15px !important; font-weight: 500 !important; margin-bottom: 6px !important; }
[data-testid="stMarkdownContainer"] h3 { color: #d0d0d0 !important; font-size: 13px !important; font-weight: 500 !important; }
[data-testid="stMarkdownContainer"] code {
    background: #1a1a1a !important;
    color: #a8a8a8 !important;
    border: 1px solid #222 !important;
    border-radius: 4px !important;
    padding: 1px 6px !important;
    font-size: 12px !important;
}
[data-testid="stMarkdownContainer"] pre {
    background: #141414 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 9px !important;
    padding: 14px !important;
}
[data-testid="stMarkdownContainer"] a { color: #888 !important; text-decoration: underline; text-underline-offset: 3px; }
[data-testid="stMarkdownContainer"] li { color: #c8c8c8 !important; font-size: 13.5px !important; margin-bottom: 3px !important; }
[data-testid="stMarkdownContainer"] strong { color: #e0e0e0 !important; font-weight: 500 !important; }
[data-testid="stMarkdownContainer"] hr { border-color: #1e1e1e !important; margin: 10px 0 !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #222; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #2a2a2a; }

/* ── CAPTION ── */
[data-testid="stCaptionContainer"] p { color: #444 !important; font-size: 11px !important; }
</style>
""", unsafe_allow_html=True)

client = setup_client()

# ── SIDEBAR ──────────────────────────────────────────────────────
with st.sidebar:

    # Logo
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:24px;">
        <div style="width:28px;height:28px;background:#f0f0f0;border-radius:7px;
                    display:flex;align-items:center;justify-content:center;flex-shrink:0;">
            <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                <rect x="1" y="1" width="5" height="5" rx="1" fill="#111"/>
                <rect x="7" y="1" width="5" height="5" rx="1" fill="#111"/>
                <rect x="1" y="7" width="5" height="5" rx="1" fill="#111"/>
                <rect x="7" y="7" width="5" height="5" rx="1" fill="#111" opacity="0.3"/>
            </svg>
        </div>
        <span style="font-size:14px;font-weight:600;color:#f0f0f0;letter-spacing:-0.01em;">Albert AI</span>
    </div>
    """, unsafe_allow_html=True)

    # Nav label
    st.markdown('<div style="font-size:10px;color:#333;letter-spacing:0.08em;text-transform:uppercase;font-weight:500;margin-bottom:6px;">Menu</div>', unsafe_allow_html=True)

    # Active nav item — Chat (only functional one)
    st.markdown("""
    <div style="display:flex;align-items:center;gap:9px;padding:7px 9px;
                background:#1e1e1e;border-radius:7px;margin-bottom:10px;
                border:1px solid #252525;">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <rect x="1" y="1" width="5" height="5" rx="1" fill="#f0f0f0"/>
            <rect x="8" y="1" width="5" height="5" rx="1" fill="#f0f0f0"/>
            <rect x="1" y="8" width="5" height="5" rx="1" fill="#f0f0f0"/>
            <rect x="8" y="8" width="5" height="5" rx="1" fill="#f0f0f0" opacity="0.3"/>
        </svg>
        <span style="font-size:13px;color:#f0f0f0;font-weight:500;">Chat</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:#1a1a1a;margin:4px 0 14px;"></div>', unsafe_allow_html=True)

    # Upload label
    st.markdown('<div style="font-size:10px;color:#333;letter-spacing:0.08em;text-transform:uppercase;font-weight:500;margin-bottom:8px;">Upload source</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "file",
        type=["pdf", "docx", "jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )

    # Show uploaded file card
    if uploaded_file:
        ext = uploaded_file.name.split(".")[-1].upper()
        st.markdown(f"""
        <div style="background:#161616;border:1px solid #1e1e1e;border-radius:8px;
                    padding:9px 11px;margin-top:8px;">
            <div style="font-size:11px;font-weight:500;color:#888;
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
                        margin-bottom:2px;">{uploaded_file.name}</div>
            <div style="font-size:10px;color:#333;">Ready · {ext}</div>
        </div>
        """, unsafe_allow_html=True)

    # Spacer pushes model badge + clear button to bottom
    st.markdown('<div style="flex:1;min-height:20px;"></div>', unsafe_allow_html=True)

    # Model badge
    st.markdown("""
    <div style="background:#161616;border:1px solid #1e1e1e;border-radius:8px;
                padding:9px 11px;margin-bottom:10px;">
        <div style="font-size:10px;color:#333;margin-bottom:2px;">Model</div>
        <div style="font-size:11px;font-weight:500;color:#666;">Llama 3.3 · 70B</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ── TOP BAR ──────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;justify-content:space-between;
            padding:10px 20px 10px;border-bottom:1px solid #1a1a1a;
            background:#0f0f0f;margin-bottom:0;">
    <span style="font-size:13px;font-weight:500;color:#f0f0f0;letter-spacing:-0.01em;">Chat</span>
    <div style="display:flex;align-items:center;gap:7px;">
        <div style="background:#141414;border:1px solid #1e1e1e;border-radius:20px;
                    padding:4px 11px;font-size:11px;color:#555;
                    display:flex;align-items:center;gap:5px;">
            <div style="width:5px;height:5px;border-radius:50%;background:#22c55e;"></div>
            Online
        </div>
        <div style="background:#141414;border:1px solid #1e1e1e;border-radius:20px;
                    padding:4px 11px;font-size:11px;color:#555;">
            Web search on
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── SESSION STATE ─────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []


# ── EMPTY STATE ───────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;
                justify-content:center;padding:60px 20px 40px;text-align:center;">
        <div style="width:40px;height:40px;background:#161616;border:1px solid #1e1e1e;
                    border-radius:10px;display:flex;align-items:center;justify-content:center;
                    margin-bottom:16px;">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <rect x="1" y="1" width="7" height="7" rx="1.5" fill="#333"/>
                <rect x="10" y="1" width="7" height="7" rx="1.5" fill="#333"/>
                <rect x="1" y="10" width="7" height="7" rx="1.5" fill="#333"/>
                <rect x="10" y="10" width="7" height="7" rx="1.5" fill="#333" opacity="0.4"/>
            </svg>
        </div>
        <div style="font-size:17px;font-weight:500;color:#e0e0e0;margin-bottom:6px;letter-spacing:-0.02em;">
            How can I help you today?
        </div>
        <div style="font-size:12px;color:#3a3a3a;margin-bottom:28px;line-height:1.6;">
            Ask anything · Upload a document · Describe an image to create
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;justify-content:center;">
            <div style="background:#141414;border:1px solid #1e1e1e;border-radius:8px;
                        padding:9px 14px;font-size:12px;color:#555;">
                Summarise a document
            </div>
            <div style="background:#141414;border:1px solid #1e1e1e;border-radius:8px;
                        padding:9px 14px;font-size:12px;color:#555;">
                Research a topic
            </div>
            <div style="background:#141414;border:1px solid #1e1e1e;border-radius:8px;
                        padding:9px 14px;font-size:12px;color:#555;">
                Generate an image
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── RENDER HISTORY ────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], str) and msg["content"].startswith("__IMAGE__"):
            image_url = msg["content"].replace("__IMAGE__", "")
            st.markdown(
                f'<img src="{image_url}" width="100%"'
                f' style="border-radius:10px;border:1px solid #1e1e1e;" />',
                unsafe_allow_html=True
            )
        else:
            st.markdown(msg["content"])


# ── INTENT CLASSIFIER ─────────────────────────────────────────────
def is_image_request(prompt: str, client) -> bool:
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content":
                f'Does this message ask to generate, draw, create, or show an image or artwork?\n'
                f'Message: "{prompt}"\n'
                f'Reply with one word only: IMAGE or TEXT'}],
            temperature=0,
            max_tokens=5
        )
        return resp.choices[0].message.content.strip().upper() == "IMAGE"
    except Exception:
        fallback = ["draw", "generate image", "create image",
                    "paint", "make an image", "show me a picture"]
        return any(t in prompt.lower() for t in fallback)


# ── CHAT INPUT ────────────────────────────────────────────────────
if prompt := st.chat_input("Ask Albert anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if is_image_request(prompt, client):
            full_response = handle_image_generation(prompt, client)
        else:
            full_response = handle_text_chat(
                prompt, client, uploaded_file, st.session_state.messages
            )

    st.session_state.messages.append({"role": "assistant", "content": full_response})