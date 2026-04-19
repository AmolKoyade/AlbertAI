import streamlit as st
import urllib.parse
import hashlib


def handle_image_generation(prompt, client):
    status_box = st.status("🎨 Albert is creating art...", expanded=True)

    # Step 1: Enhance prompt with Groq
    # FIX: Added temperature=0 for consistent prompt rewriting every time
    enhance_cmd = (
        f"Rewrite as a vivid 4k art prompt for exactly this subject: '{prompt}'. "
        f"Style: cinematic, photorealistic. UNDER 20 WORDS. "
        f"Only the prompt, no preamble, no extra text, no quotes."
    )
    try:
        enh_resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": enhance_cmd}],
            temperature=0  # FIX: Always gives same rewritten prompt for same input
        )
        art_prompt = enh_resp.choices[0].message.content.strip()
    except Exception:
        art_prompt = prompt  # fallback to original prompt

    # Step 2: FIX - Generate a FIXED seed from the prompt text using hash
    # Same prompt = same seed = same image EVERY TIME
    seed = int(hashlib.md5(art_prompt.lower().encode()).hexdigest(), 16) % 999999

    # Step 3: Build Pollinations URL with fixed seed and enhance=false
    encoded_prompt = urllib.parse.quote(art_prompt, safe="")
    image_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1024&height=1024&nologo=true&enhance=false&seed={seed}&model=flux"
    )

    # Step 4: Render image in browser via <img> tag
    status_box.update(label="✅ Sending to your browser...", state="complete")

    st.markdown(
        f"""
        <img src="{image_url}" 
             width="100%" 
             style="border-radius: 12px; margin-top: 8px;"
             alt="Generated image: {art_prompt}" />
        """,
        unsafe_allow_html=True
    )

    st.markdown(f"📝 **Prompt:** *{art_prompt}*")
    st.markdown(f"**[💾 Download High-Res]({image_url})**")

    # Save image URL to history so it reappears on scroll
    full_response = f"__IMAGE__{image_url}"
    return full_response
