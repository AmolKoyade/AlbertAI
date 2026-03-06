import streamlit as st
import urllib.parse
import random
import requests
import io


def fetch_image_bytes(url, timeout=90):
    """
    Downloads image bytes from Pollinations with proper headers and retries.
    Returns raw bytes on success, or None on failure.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://pollinations.ai/",
    }
    for attempt in range(3):
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            content_type = r.headers.get("Content-Type", "")
            if r.status_code == 200 and "image" in content_type:
                return r.content
            else:
                st.warning(f"Attempt {attempt+1}: Status {r.status_code} | Content-Type: {content_type}")
        except requests.exceptions.Timeout:
            st.warning(f"Attempt {attempt+1}: Timed out after {timeout}s")
        except Exception as ex:
            st.warning(f"Attempt {attempt+1}: Error — {ex}")
    return None


def handle_image_generation(prompt, client):
    status_box = st.status("🎨 Albert is creating art...", expanded=True)

    # Step 1: Enhance prompt with Groq
    enhance_cmd = (
        f"Rewrite as a vivid 4k art prompt: '{prompt}'. "
        f"Style: cinematic. UNDER 20 WORDS. Only the prompt, no preamble."
    )
    try:
        enh_resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": enhance_cmd}]
        )
        art_prompt = enh_resp.choices[0].message.content.strip()
    except Exception:
        art_prompt = prompt

    # Step 2: Build URL — keep it simple, avoid over-encoding
    seed = random.randint(1, 999999)
    encoded_prompt = urllib.parse.quote(art_prompt, safe="")
    image_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1024&height=1024&nologo=true&seed={seed}&model=flux"
    )

    # Show the URL so you can debug manually if needed
    status_box.update(label=f"🖌️ Generating... (up to 90s)", state="running")
    with st.expander("🔗 Debug: Image URL (click to copy)", expanded=False):
        st.code(image_url)

    # Step 3: Fetch with retries
    image_bytes = fetch_image_bytes(image_url, timeout=90)

    # Step 4: Show result or fallback
    if image_bytes:
        status_box.update(label="✅ Masterpiece Complete!", state="complete")
        st.image(io.BytesIO(image_bytes), caption=f"Prompt: {art_prompt}")
        st.markdown(f"**[💾 Download High-Res]({image_url})**")
        full_response = f"I've painted that for you! Prompt used: *{art_prompt}*"
    else:
        # Fallback: simpler prompt, turbo model
        status_box.update(label="⚠️ Retrying with simplified prompt...", state="running")
        fallback_encoded = urllib.parse.quote(prompt, safe="")
        fallback_url = (
            f"https://image.pollinations.ai/prompt/{fallback_encoded}"
            f"?width=512&height=512&nologo=true&seed={seed}&model=turbo"
        )
        with st.expander("🔗 Debug: Fallback URL", expanded=False):
            st.code(fallback_url)

        fallback_bytes = fetch_image_bytes(fallback_url, timeout=60)

        if fallback_bytes:
            st.image(io.BytesIO(fallback_bytes), caption="Albert's Quick Sketch")
            status_box.update(label="✅ Quick Sketch Complete", state="complete")
            full_response = "Here's a quick sketch — the HD version timed out."
        else:
            status_box.update(label="❌ Image generation failed", state="error")
            st.error("Pollinations.ai did not respond. Try opening the debug URL above in your browser to test it manually.")
            full_response = "Image generation failed. Check the debug URLs above to diagnose."

    return full_response