import streamlit as st
from openai import OpenAI
from openai.types.beta.assistant_stream_event import ThreadMessageDelta
from openai.types.beta.threads.text_delta_block import TextDeltaBlock

# Initialisation du client OpenAI
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)

# Identifiants des assistants depuis les secrets
ASSISTANT_IDS = {
 "Steve Jobs": st.secrets["ASSISTANT_ID_1"],
 "Jeff Bezos": st.secrets["ASSISTANT_ID_2"],
 "Elon Musk": st.secrets["ASSISTANT_ID_3"],
 "Mark Zuck": st.secrets["ASSISTANT_ID_4"],
}

# Initialisation de l'état de la session pour stocker l'historique des conversations et les threads
if "chat_history" not in st.session_state:
 st.session_state.chat_history = []
if "thread_ids" not in st.session_state:
 st.session_state.thread_ids = {}

# Fonction pour créer un nouveau thread pour un assistant s'il n'existe pas encore
def initialize_thread(assistant_name):
 if assistant_name not in st.session_state.thread_ids:
 thread = client.beta.threads.create()
 st.session_state.thread_ids[assistant_name] = thread.id

# Fonction pour envoyer un message et diffuser la réponse en continu
def send_message_and_stream(assistant_name, user_input):
 # Initialiser le thread si nécessaire
 initialize_thread(assistant_name)
 thread_id = st.session_state.thread_ids[assistant_name]
 assistant_id = ASSISTANT_IDS[assistant_name]
 # Ajouter le message utilisateur au thread
 client.beta.threads.messages.create(
 thread_id=thread_id,
 role="user",
 content=user_input
 )
 # Créer le run et streamer la réponse de l'assistant
 assistant_reply = ""
 with st.chat_message("assistant"):
 st.markdown(f"**{assistant_name}:**")
 stream = client.beta.threads.runs.create(
 thread_id=thread_id,
 assistant_id=assistant_id,
 stream=True
 )
 # Boîte vide pour afficher la réponse
 assistant_reply_box = st.empty()
 # Itération à travers le stream pour récupérer la réponse au fur et à mesure
 for event in stream:
 if isinstance(event, ThreadMessageDelta):
 if event.data.delta.content and isinstance(event.data.delta.content[0], TextDeltaBlock):
 assistant_reply += event.data.delta.content[0].text.value
 assistant_reply_box.markdown(assistant_reply)
 # Ajouter la réponse finale à l'historique de la conversation
 st.session_state.chat_history.append({"role": "assistant", "content": f"**{assistant_name}:**\n{assistant_reply}"})
 # Retourner la réponse complète de l'assistant
 return assistant_reply

# Titre de l'application
st.title("Les rêves de Ouss")
st.subheader("Invoquez les boss du game en temps réel")

# Affichage de l'historique des messages dans le chat
for message in st.session_state.chat_history:
 with st.chat_message(message["role"]):
 st.markdown(message["content"])

# Sélection des assistants avec qui vous souhaitez parler
assistant_names = st.multiselect(
 "Choisissez les assistants avec qui discuter :",
 list(ASSISTANT_IDS.keys()),
 default=list(ASSISTANT_IDS.keys())
)

# Entrée de l'utilisateur pour envoyer un message
user_query = st.chat_input("Tapez votre message :")
if user_query is not None and user_query.strip() != '':
 with st.chat_message("user"):
 st.markdown(user_query)
 # Stocker la réponse du lecteur dans l'historique de conversation
 st.session_state.chat_history.append({"role": "user", "content": user_query})
 # Envoyer le message aux assistants sélectionnés
 for assistant_name in assistant_names:
 send_message_and_stream(assistant_name, user_query)
