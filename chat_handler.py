import streamlit as st
from utils import extract_text, encode_image, get_web_context

# Cap conversation history to prevent context window overflow
MAX_HISTORY = 10

def handle_text_chat(prompt, client, uploaded_file, messages):
    file_txt, is_img, b64_img = "", False, None

    # --- Safe file processing ---
    if uploaded_file is not None:
        if uploaded_file.type.startswith("image"):
            is_img = True
            b64_img = encode_image(uploaded_file)
        else:
            file_txt = extract_text(uploaded_file)

    with st.status("🔍 Researching...", expanded=False):
        web_info = get_web_context(prompt)

    # FIX 1: Filter out __IMAGE__ entries and any non-string content
    # (e.g. list-type content from previous vision turns) before sending
    # to the API — these corrupt the payload and cause crashes.
    # FIX 2: Cap to last MAX_HISTORY messages to avoid context overflow
    # on long conversations.
    clean_history = [
        {"role": m["role"], "content": m["content"]}
        for m in messages[:-1]
        if isinstance(m["content"], str) and not m["content"].startswith("__IMAGE__")
    ][-MAX_HISTORY:]

    if is_img and b64_img:
        # FIX 3: Use the correct Groq base64 image format.
        # The previous "image_url" format is OpenAI-specific and
        # is NOT supported by Groq — it causes a silent API failure.
        clean_history.append({
            "role": "user",
            "content": [
                {"type": "text", "text": f"Web context: {web_info}\n\nQuestion: {prompt}"},
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": b64_img
                    }
                }
            ]
        })
        model = "meta-llama/llama-4-scout-17b-16e-instruct"
    else:
        # Build a clean user message, only including file/web context if present
        user_message = f"Question: {prompt}"
        if file_txt:
            user_message = f"File content:\n{file_txt}\n\n{user_message}"
        if web_info:
            user_message = f"Web context:\n{web_info}\n\n{user_message}"
        clean_history.append({"role": "user", "content": user_message})
        model = "llama-3.3-70b-versatile"

    resp_placeholder = st.empty()
    # Default fallback so history never stores an empty string
    full_response = "Sorry, I ran into an issue. Please try again."

    try:
        stream = client.chat.completions.create(
            model=model,
            messages=clean_history,
            stream=True,
            max_tokens=2048  # FIX 4: Cap tokens to prevent runaway/slow responses
        )
        full_response = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                full_response += delta
                resp_placeholder.markdown(full_response + "▌")
        resp_placeholder.markdown(full_response)

    except Exception as e:
        resp_placeholder.markdown(full_response)
        st.error(f"Error: {str(e)}")

    return full_response