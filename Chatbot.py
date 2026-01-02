from openai import OpenAI
import streamlit as st
import base64
import os
import json
import uuid
import glob

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    
    # Model Selection
    model_option = st.selectbox(
        "Select Model",
        options=[
            "o1-preview", 
            "o1-mini", 
            "gpt-4o", 
            "gpt-4.5-preview",
            "gpt-5-preview", 
            "gpt-4-turbo", 
            "gpt-3.5-turbo", 
            "Other (Custom)"
        ],
        index=0
    )
    custom_model = ""
    if model_option == "Other (Custom)":
        custom_model = st.text_input("Enter Model Name", "gpt-4.5-preview")

    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by OpenAI")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    if isinstance(msg["content"], str):
        st.chat_message(msg["role"]).write(msg["content"])
    elif isinstance(msg["content"], list):
        with st.chat_message(msg["role"]):
            for item in msg["content"]:
                if item["type"] == "text":
                    st.write(item["text"])
                elif item["type"] == "image_url":
                    st.image(item["image_url"]["url"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    client = OpenAI(api_key=openai_api_key)
    
    # Process input (handle text and potential image)
    if uploaded_file:
        # Encode image to base64
        base64_image = base64.b64encode(uploaded_file.read()).decode("utf-8")
        image_url = f"data:image/jpeg;base64,{base64_image}"
        
        # Create message with image
        message_content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]
        # Display image locally
        st.session_state.messages.append({"role": "user", "content": message_content})
        with st.chat_message("user"):
            st.write(prompt)
            st.image(uploaded_file)
    else:
        # Text only
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
    
    # Check if a specific model is selected, otherwise default to the selection
    if model_option == "Other (Custom)":
        model_name = custom_model
    else:
        model_name = model_option

    with st.spinner(f"Generating response using {model_name}..."):
        try:
            response = client.chat.completions.create(model=model_name, messages=st.session_state.messages)
            msg = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.chat_message("assistant").write(msg)
            
            # Auto-save after response
            save_chat_history()
            
        except Exception as e:
            st.error(f"Error calling OpenAI API with model '{model_name}': {e}")
