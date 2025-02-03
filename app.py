import os
import requests
import streamlit as st
import json  # Import the json module

# Securely retrieve your API key
api_key = os.getenv("GROQ_API_KEY")  # Ensure your environment variable is set
url = "https://api.groq.com/openai/v1/chat/completions"  # Endpoint for chat completions

# Set up the headers for authentication
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Streamlit UI setup
st.set_page_config(page_title="AI Chatbot", layout="wide")
st.title("🤖 Groq Llama AI Chatbot")

# Initialize session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are an AI chatbot that provides helpful responses."}
    ]

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).write(msg["content"])

# User input
user_input = st.chat_input("Ask me anything...")

if user_input:
    # Add user message to conversation history
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # Prepare the API payload with the user input
    data = {
        "model": "llama-3.3-70b-versatile",  # Specify the model you want to use
        "messages": [{"role": "system", "content": "You are an AI chatbot."},
                     {"role": "user", "content": user_input}],
        "temperature": 0.7,  # Controls randomness in the response
        "max_tokens": 150  # Adjust response length
    }

    # Send the request to the Groq API
    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            # Handle the response
            response_data = response.json()
            assistant_response = response_data['choices'][0]['message']['content']

            # Display assistant's response in the chat
            st.chat_message("assistant").write(assistant_response)

            # Save assistant response to session state
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})

        else:
            st.error(f"Error: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
