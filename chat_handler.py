import streamlit as st
from utils import extract_text, encode_image, get_web_context

# ---------------------------------------------------------------------------
# st.session_state.messages  → stores ALL messages, never trimmed (full UI history)
# api_history                → only last API_CONTEXT_LIMIT clean messages sent to Groq
# ---------------------------------------------------------------------------
API_CONTEXT_LIMIT = 10


def handle_text_chat(prompt, client, uploaded_file, messages):
    file_txt, is_img, b64_img = "", False, None

    # --- File processing ---
    if uploaded_file is not None:
        if uploaded_file.type.startswith("image"):
            is_img = True
            b64_img = encode_image(uploaded_file)
        else:
            file_txt = extract_text(uploaded_file)

    with st.status("🔍 Researching...", expanded=False):
        web_info = get_web_context(prompt)

    # Build clean API history — skip __IMAGE__ entries and non-string content
    api_history = [
        {"role": m["role"], "content": m["content"]}
        for m in messages[:-1]
        if isinstance(m["content"], str)
        and not m["content"].startswith("__IMAGE__")
    ][-API_CONTEXT_LIMIT:]

    # --- Append current user message ---
    if is_img and b64_img:
        # FIX: Groq uses OpenAI-compatible format for images — NOT Anthropic format
        # Groq accepts: image_url with base64 data URI
        # Groq does NOT accept: "type": "image" with "source" key (that's Claude/Anthropic)
        api_history.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Web context: {web_info}\n\nQuestion: {prompt}" if web_info
                            else f"Question: {prompt}"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{b64_img}"
                    }
                }
            ]
        })
        # llama-4-scout supports vision on Groq
        model = "meta-llama/llama-4-scout-17b-16e-instruct"
    else:
        user_message = f"Question: {prompt}"
        if file_txt:
            user_message = f"File content:\n{file_txt}\n\n{user_message}"
        if web_info:
            user_message = f"Web context:\n{web_info}\n\n{user_message}"
        api_history.append({"role": "user", "content": user_message})
        model = "llama-3.3-70b-versatile"

    # --- Stream response ---
    resp_placeholder = st.empty()
    full_response = "Sorry, I ran into an issue. Please try again."

    try:
        stream = client.chat.completions.create(
            model=model,
            messages=api_history,
            stream=True,
            max_tokens=2048
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