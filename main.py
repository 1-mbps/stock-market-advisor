import streamlit as st
from chat import StockAdvisorChat
import dotenv

dotenv.load_dotenv()

st.title("Stock Market Advisor")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state:
    chat = StockAdvisorChat(st.session_state)
    st.session_state.chat = chat
else:
    chat = st.session_state.chat


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
    
if prompt := st.chat_input("What is up?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    stream = chat.reply(prompt)
    response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})

