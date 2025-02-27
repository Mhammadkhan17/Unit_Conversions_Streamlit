import streamlit as st
import google.generativeai as genai
import os

api_key = st.secrets["GOOGLE_API_KEY"]

genai.configure(api_key=api_key)


def list_models():
    """Lists available Gemini models."""
    available_models = []
    for model in genai.list_models():
        print(model)
        if 'generateContent' in model.supported_generation_methods:
            print(f"Model {model.name} supports generateContent")
            available_models.append(model.name)  # Store available models
    return available_models


st.title("Unit Conversion Chatbot")

available_models = list_models()

if not available_models:
    st.error("No available models found that support generateContent. Check your API key and region.")
else:
    selected_model_name = available_models[24]
    model = genai.GenerativeModel(selected_model_name)

    # Initialize chat history in Streamlit session state with specific instructions for unit conversion
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "model", "parts": ["You are a chatbot exclusively designed for unit conversions.  Only answer questions related to unit conversions. If a question is not about unit conversions, please respond with: 'I am designed only for unit conversions.'"]}
        ]

    # Display existing chat messages from history, skip the first one (initial message)
    for i, message in enumerate(st.session_state.chat_history): # Use chat_history here
        if i > 0: # Skip the first message (index 0) which is our initial system message
            with st.chat_message(message["role"]):
                st.markdown(message["parts"][0]) # Gemini expects 'parts' format

    if prompt := st.chat_input("Enter units to convert (e.g., 'convert 100 meters to feet'):"): # Updated chat input prompt
        st.chat_message("user").markdown(prompt)
        # Append user message to chat history in the expected format
        st.session_state.chat_history.append({"role": "user", "parts": [prompt]}) # Use chat_history and 'parts'

        try:
            # Get response from Gemini, passing the entire chat history
            response = model.generate_content(st.session_state.chat_history) # Pass chat_history for context
            bot_response = response.text
            # Check if the response is empty or doesn't seem like a unit conversion, if so, provide specific message
            if not bot_response.strip() or "I am designed only for unit conversions." in bot_response:
                bot_response = "I am designed only for unit conversions. Please ask a question related to unit conversion."
        except Exception as e:
            bot_response = f"An error occurred: {e}"

        st.chat_message("assistant").markdown(bot_response)
        # Append bot response to chat history
        st.session_state.chat_history.append({"role": "model", "parts": [bot_response]}) # Use chat_history and 'parts'
