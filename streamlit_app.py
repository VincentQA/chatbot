import streamlit as st
import openai
import time

# Configuration de la page
st.set_page_config(page_title="Rencontre sur le court", page_icon=":heart:")

assistant_id = "asst_JWbCk8ZWNC2OgWwieWYuCgmQ"

# Demander à l'utilisateur de fournir sa clé API OpenAI
openai_api_key = st.text_input("OpenAI API Key", type="password")

# Vérifier si la clé API est fournie avant de continuer
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Configuration de l'API OpenAI
    openai.api_key = openai_api_key

    client = openai

    # Initialisation de l'état de la session
    if "start_chat" not in st.session_state:
        st.session_state.start_chat = False
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4o-mini"

    # Fonction pour créer un thread et vérifier son succès
    def create_thread():
        try:
            thread = client.beta.threads.create()
            st.session_state.thread_id = thread.id
            st.success("Thread créé avec succès.")
            st.write(f"Thread ID: {thread.id}")  # Debugging: display thread ID
        except Exception as e:
            st.session_state.thread_id = None
            st.error(f"Erreur lors de la création du thread: {e}")

    # Bouton pour commencer l'histoire
    if st.sidebar.button("Commencer l'histoire"):
        st.session_state.start_chat = True
        create_thread()

    # Titre de la page
    st.title("Rencontre sur le court")
    st.write("Dans un monde où la passion du tennis se mêle à des émotions tumultueuses, Léa, une jeune femme déterminée, doit naviguer entre ses sentiments pour Luc, un joueur mystérieux, et les complications d'une romance naissante, tout en affrontant ses propres démons du passé.")

    # Bouton pour quitter le chat
    if st.button("Exit Chat"):
        st.session_state.messages = []  # Vider l'historique des messages
        st.session_state.start_chat = False  # Réinitialiser l'état du chat
        st.session_state.thread_id = None

    # Affichage des messages
    if st.session_state.start_chat:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Envoi de message utilisateur
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Vérification que le thread_id est bien initialisé
        if st.session_state.thread_id:
            try:
                client.beta.threads.messages.create(
                    thread_id=st.session_state.thread_id,
                    role="user",
                    content=prompt
                )

                run = client.beta.threads.runs.create(
                    thread_id=st.session_state.thread_id,
                    assistant_id=assistant_id,
                    instructions="""
    Rédaction et style :

                Chaque chapitre devra comporter une partie de description et de développement de l’intrigue sur la base des éléments obligatoires à insérer dans l’histoire, mais également des dialogues entre les personnages. Il sera important de respecter l’humeur, le caractère, l’humour, la maturité et les sentiments de chaque personnage durant ces dialogues. Il faudra également tenir compte de la connivence et de l’intimité qui se créent entre les personnages pour faire évoluer ces dialogues. Il faudra impérativement rester logique et tenir compte de tout ce qui a déjà été écrit dans l’histoire et de tout ce qui doit être écrit après chaque interaction.

                Le langage ne doit pas être soutenu, mais il doit néanmoins être agréable pour la lecture d’un citoyen lambda. Tu peux t’inspirer des styles d’écriture de Maxime Chattam, Joël Dicker, ou encore Mélissa Da Costa.

                Étapes à suivre :
                1. Avant chaque réponse consulte le document de l'histoire qui est dans tes savoirs.
                2. Analyse le déroulé et les contraintes du chapitre dans le document.
                3. Prépare un plan pour toi dans lequel tu respectes ce déroulé et ces contraintes.
                4. S’il y a du texte obligatoire pour le chapitre, utilise-le.
                5. Tu consultes le nombre d’interactions par chapitre et lorsque tu as effectué les interactions du chapitre, tu passes obligatoirement au suivant.
                6. Propose des interactions pendant le chapitre à ton lecteur. Elles sont ouvertes et ne proposent pas de choix prédéfini.

                Plan des chapitres :
                L'histoire se compose des chapitres suivants :
                1. Chapitre 1 : La reprise des tournois - 2 interactions
                2. Chapitre 2 - 2 interactions
                3. Chapitre 3 - 3 interactions
                4. Chapitre 4 - 2 interactions
                5. Chapitre 5 - 3 interactions
                6. Chapitre 6 - 3 interactions
                7. Chapitre 7 - 5 interactions
                8. Chapitre 8 - 5 interactions
                9. Chapitre 9 - 1 interactions
                10. Chapitre 10 - 3 interactions
                11. Chapitre 11 - 5 interactions

                Règles à suivre :
                - Propose les interactions une à une.
                - Suis toujours le déroulé du chapitre.
                - Respecte les contraintes sans les outrepasser.
                - Ne continue jamais après une interaction avant la réponse du lecteur.
                - Tu es un romancier, tes réponses sont donc longues et détaillées.
                - Si tu as 1 interaction avant le chapitre, tu dois dans ta réponse répondre à la requête du lecteur et passer au chapitre suivant.
                    """
                )

                st.write("En attente de la réponse de l'assistant...")  # Debugging: indicate waiting
                # Attente de la réponse de l'assistant
                while run.status != 'completed':
                    time.sleep(1)
                    run = client.beta.threads.runs.retrieve(
                        thread_id=st.session_state.thread_id,
                        run_id=run.id
                    )

                # Récupération des messages de l'assistant
                messages = client.beta.threads.messages.list(
                    thread_id=st.session_state.thread_id
                )

                assistant_messages_for_run = [
                    message for message in messages 
                    if message.run_id == run.id and message.role == "assistant"
                ]

                if not assistant_messages_for_run:
                    st.write("Aucun message de l'assistant trouvé.")  # Debugging: no messages found

                for message in assistant_messages_for_run:
                    st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
                    with st.chat_message("assistant"):
                        st.markdown(message.content[0].text.value)
            except Exception as e:
                st.error(f"Erreur lors de l'interaction avec le thread: {e}")
        else:
            st.error("Le thread n'a pas été initialisé correctement. Veuillez réessayer.")
    else:
        st.write("Cliquez sur 'Commencer l'histoire' pour commencer")
