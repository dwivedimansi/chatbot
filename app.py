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
        {"role": "system", "content": "You are an AI chatbot that provides helpful responses, remembers context, and asks follow-up questions to keep the conversation engaging."}
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

    # Prepare the API payload with full conversation history
    data = {
        "model": "llama-3.3-70b-versatile",  # Specify the model
        "messages": st.session_state.messages,  # Send full conversation for memory
        "temperature": 0.7,  # Controls randomness
        "max_tokens": 200  # Adjust response length
    }

    # Send the request to the Groq API
    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            # Handle the response
            response_data = response.json()
            assistant_response = response_data['choices'][0]['message']['content']

            # Generate a follow-up question for engagement
            follow_up_data = {
                "model": "llama-3.3-70b-versatile",
                "messages": st.session_state.messages + [
                    {"role": "assistant", "content": assistant_response},
                    {"role": "system", "content": "Now, ask a relevant follow-up question to keep the conversation going."}
                ],
                "temperature": 0.7,
                "max_tokens": 100
            }
            
            follow_up_response = requests.post(url, headers=headers, json=follow_up_data)
            if follow_up_response.status_code == 200:
                follow_up_text = follow_up_response.json()['choices'][0]['message']['content']
            else:
                follow_up_text = "Would you like to ask something else?"

            # Display assistant's response in the chat
            st.chat_message("assistant").write(assistant_response)
            st.chat_message("assistant").write(follow_up_text)  # Show follow-up question

            # Save assistant response and follow-up to session state
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            st.session_state.messages.append({"role": "assistant", "content": follow_up_text})

        else:
            st.error(f"Error: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
