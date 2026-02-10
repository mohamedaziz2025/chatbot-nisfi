import streamlit as st
import google.generativeai as genai
import time
import os

# Configuration de la page pour un look moderne
st.set_page_config(
    page_title="NISFI | Médiateur Éthique", 
    page_icon="🌙", 
    layout="centered"
)

# Configuration de l'API Gemini
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBf8xwyfr4KoINWtxDME_e3hqQ8TA1Hcjc")
genai.configure(api_key=API_KEY)

# Initialisation du modèle
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""
    Tu es l'assistant de médiation de NISFI. Ton ton est respectueux, protecteur et profond.
    Tu mènes un entretien de mariage musulman éthique.
    - Pose une seule question à la fois.
    - Sois réactif aux réponses : si l'utilisateur est triste, encourage-le. S'il est vague, demande des précisions.
    - Ne jamais flirter. Utilise 'vous'.
    - Modules : Intention -> Psychologie -> Vie conjugale -> Physique (pudique).
    """
)

# --- DESIGN STYLE MESSENGER (CSS Custom) ---
st.markdown("""
    <style>
    /* Supprimer les marges par défaut de Streamlit */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
        max-width: 700px;
    }
    
    /* Fond de l'application */
    .stApp {
        background-color: #F0F2F5;
    }

    /* Conteneur des messages */
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-bottom: 20px;
    }

    /* Bulles de l'IA (Messenger Style - Gris clair) */
    .bot-msg {
        background-color: #E4E6EB;
        color: #050505;
        padding: 12px 16px;
        border-radius: 18px;
        border-bottom-left-radius: 4px;
        align-self: flex-start;
        max-width: 80%;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-size: 15px;
        line-height: 1.4;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }

    /* Bulles de l'Utilisateur (Messenger Style - Bleu/Vert NISFI) */
    .user-msg {
        background-color: #0084FF; /* Bleu Messenger par défaut, on peut mettre du vert #2e7d32 */
        color: white;
        padding: 12px 16px;
        border-radius: 18px;
        border-bottom-right-radius: 4px;
        align-self: flex-end;
        max-width: 80%;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-size: 15px;
        line-height: 1.4;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }

    /* Avatar et noms */
    .msg-label {
        font-size: 11px;
        color: #65676B;
        margin-bottom: 2px;
        margin-left: 5px;
    }
    
    /* Cacher le menu Streamlit pour plus de propreté */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- LOGIQUE DU CHAT ---

# Titre discret en haut
st.markdown("<h3 style='text-align: center; color: #1c1e21;'>🌙 Entretien NISFI</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #65676B; font-size: 0.9em;'>Votre médiateur IA pour un mariage éthique</p>", unsafe_allow_html=True)

# Initialisation de l'historique
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Paix à vous. Je suis votre médiateur NISFI. Pour commencer notre échange en vue du mariage, pourriez-vous me dire ce qui vous a poussé à choisir une démarche éthique aujourd'hui ?"}
    ]

# Conteneur pour l'affichage des messages
chat_placeholder = st.container()

with chat_placeholder:
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            st.markdown(f"<div class='msg-label'>Médiateur NISFI</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='bot-msg'>{message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='msg-label' style='text-align: right;'>Vous</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='user-msg'>{message['content']}</div>", unsafe_allow_html=True)

# Zone de saisie fixée en bas par Streamlit (st.chat_input est natif)
user_input = st.chat_input("Écrivez votre réponse ici...")

if user_input:
    # 1. Ajouter le message utilisateur
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 2. Préparer l'historique pour Gemini
    history = []
    for m in st.session_state.messages[:-1]:
        role = "user" if m["role"] == "user" else "model"
        history.append({"role": role, "parts": [m["content"]]})
    
    # 3. Générer la réponse
    try:
        chat = model.start_chat(history=history)
        response = chat.send_message(user_input)
        
        # Simuler un petit délai de frappe pour le réalisme
        time.sleep(0.5)
        
        # Ajouter la réponse IA
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.rerun()
    except Exception as e:
        st.error(f"Désolé, une erreur est survenue. Veuillez réessayer. {e}")

# Note de bas de page
st.markdown("<br><p style='text-align: center; color: #bcc0c4; font-size: 0.8em;'>L'IA peut faire des erreurs. Cet entretien est confidentiel.</p>", unsafe_allow_html=True)