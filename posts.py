import streamlit as st
from openai import OpenAI

# --- Setup ---
st.set_page_config(page_title="Social Post Generator", layout="wide")
client = OpenAI(api_key=st.sidebar.text_input("🔐 OpenAI API Key", type="password"))

if not client.api_key:
    st.sidebar.warning("Enter your API key to use the app")
    st.stop()

# --- Platform Meta ---
platform_data = {
    "WhatsApp": {
        "icon": "https://cdn-icons-png.flaticon.com/512/124/124034.png",
        "color": "#25D366",
        "preview_bg": "#E5FFF0",
    },
    "LinkedIn": {
        "icon": "https://cdn-icons-png.flaticon.com/512/174/174857.png",
        "color": "#0077B5",
        "preview_bg": "#F3F6F9",
    },
    "Twitter": {
        "icon": "https://cdn-icons-png.flaticon.com/512/733/733579.png",
        "color": "#1DA1F2",
        "preview_bg": "#E8F5FD",
    }
}

st.title("📣 Social Media Post Generator")
st.markdown("Create platform-specific posts for **WhatsApp**, **LinkedIn**, and **Twitter** from your content.")

# --- User Input ---
user_input = st.text_area("✏️ Your content (event, product, announcement, etc.):", height=180)
tone = st.selectbox("🎭 Choose tone", ["Default", "Formal", "Casual", "Witty", "Inspirational"])

# --- Session Init ---
for platform in platform_data:
    st.session_state.setdefault(f"{platform}_post", "")

# --- Prompt ---
def build_prompt(platform, text, tone):
    prompt = f"""Generate a social media post for {platform}.
Input: "{text}"
Tone: {tone if tone != "Default" else "natural"}.
"""
    if platform == "Twitter":
        prompt += "Keep it under 280 characters. Use hashtags and emojis if appropriate."
    elif platform == "LinkedIn":
        prompt += "Professional, insightful. Up to 700 characters. Hashtags okay."
    elif platform == "WhatsApp":
        prompt += "Conversational and emoji-rich. Max 500 characters."
    prompt += "\nInclude a relevant call-to-action."
    return prompt

# --- Model Selector ---
def choose_model(text):
    return "gpt-4" if len(text) > 300 else "gpt-3.5-turbo"

# --- Generator ---
def generate_post(platform, text, tone):
    try:
        response = client.chat.completions.create(
            model=choose_model(text),
            messages=[{"role": "user", "content": build_prompt(platform, text, tone)}],
            temperature=0.8,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error: {e}"

# --- Generate All Posts ---
if st.button("▶️ Generate Posts"):
    for platform in platform_data:
        st.session_state[f"{platform}_post"] = generate_post(platform, user_input, tone)

st.markdown("---")

# --- Display Section ---
cols = st.columns(3)
for i, (platform, data) in enumerate(platform_data.items()):
    with cols[i]:
        # Platform Heading with Icon
        st.markdown(
            f"""
            <div style="text-align: center;">
                <img src="{data['icon']}" width="40" style="margin-bottom:8px;" />
                <h4 style="color:{data['color']}; margin:0;">{platform}</h4>
            </div>
            """, unsafe_allow_html=True
        )

        # Text area to edit
        updated = st.text_area(
            label="",
            value=st.session_state[f"{platform}_post"],
            height=250,
            key=f"text_{platform}"
        )
        st.session_state[f"{platform}_post"] = updated

        # Copy Button
        st.download_button(
            label=f"📋 Copy {platform} Post",
            data=updated,
            file_name=f"{platform.lower()}_post.txt",
            mime="text/plain",
            use_container_width=True
        )

        # Regenerate Button (below Copy)
        if st.button(f"🔄 Regenerate {platform}", key=f"regen_{platform}"):
            st.session_state[f"{platform}_post"] = generate_post(platform, user_input, tone)

        # Preview
        st.markdown("###### 🔍 Preview")
        st.markdown(
            f"""
            <div style="
                background-color: {data['preview_bg']};
                padding: 15px;
                border-radius: 10px;
                min-height: 120px;
                font-size: 15px;
                line-height: 1.6;
                border: 1px solid #ccc;
                color: #000;
            ">
            {st.session_state[f"{platform}_post"]}
            </div>
            """, unsafe_allow_html=True
        )

