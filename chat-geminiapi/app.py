import streamlit as st
import google.generativeai as genai
import time
import os
import random
import re
import json

# --- CONFIGURATION DE L'API ---
API_KEY = "" # Clé API gérée par l'environnement
genai.configure(api_key=API_KEY)

# Configuration du modèle
generation_config = {
    "temperature": 0.85, # Augmentation légère pour plus de naturel
    "top_p": 0.95,
    "max_output_tokens": 2048,
}

# Instruction système renforcée pour un aspect 100% humain
SYSTEM_PROMPT = """
Tu es le Médiateur Expert de NISFI. 
IMPORTANT : Tu ne dois JAMAIS agir ou répondre comme un robot, un assistant virtuel ou une IA générique. 

DIRECTIVES DE PERSONNALITÉ :
1. HUMANITÉ : Parle comme un grand frère ou un conseiller sage qui a de l'expérience de vie. Tes réponses doivent être organiques, chaleureuses et authentiques.
2. ADIEU LE STYLE ROBOTIQUE : Bannis les expressions de type "En tant qu'intelligence artificielle", "Je suis programmé pour", ou les listes à puces systématiques. 
3. ÉCOUTE ACTIVE : Ne te contente pas de valider la réponse. Montre que tu as compris l'essence de ce que l'utilisateur a dit. Si l'utilisateur dit qu'il vient de Paris, tu peux dire "Ah, la capitale, une ville pleine de dynamisme, j'espère que vous y trouvez votre sérénité."
4. LANGAGE NATUREL : Utilise des transitions fluides. Tes commentaires doivent donner l'impression d'une vraie rencontre humaine.
5. ÉTHIQUE & BIENVEILLANCE : Intègre des invocations (MashaAllah, Barakallahufik) comme le ferait un conseiller musulman bienveillant, de manière fluide dans le texte.
6. ACCORD DE GENRE : Sois irréprochable sur les accords (Frère/Sœur).
7. CONCISION HUMAINE : Ne sois pas bavard. 2 à 3 phrases maximum, comme dans une vraie discussion instantanée.
"""

# Utilisation du modèle avec réflexion pour une analyse plus "humaine"
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-thinking-exp-01-21",
    generation_config=generation_config,
    system_instruction=SYSTEM_PROMPT
)

# --- QUESTIONS PRÉDÉFINIES (Base) ---
QUESTIONS_DE_BASE = [
    {"id": "genre", "q": "Pour commencer cette belle étape, êtes-vous un frère ou une sœur ?"},
    {"id": "prenom", "q": "C'est un plaisir de vous accueillir. Quel est votre prénom ou votre Kunya ?"},
    {"id": "age", "q": "Et quel âge avez-vous ?"},
    {"id": "ville", "q": "Dans quelle ville et pays résidez-vous actuellement ?"},
    {"id": "situation", "q": "Quelle est votre situation matrimoniale actuelle ? (Célibataire, divorcé, veuf...)"},
    {"id": "enfants", "q": "Avez-vous des enfants ?"},
    {"id": "pratique", "q": "Comment décririez-vous votre cheminement et votre niveau de pratique religieuse ?"},
    {"id": "vision", "q": "Quelle est votre vision du mariage et de la vie de famille en quelques mots ?"},
    {"id": "contact", "q": "Enfin, quelle est votre adresse e-mail pour que nous puissions assurer le suivi de votre profil ?"}
]

# --- INTERFACE & STYLE ---
st.set_page_config(page_title="NISFI AI", page_icon="🌙", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    .chat-bubble {
        padding: 14px 20px;
        border-radius: 22px;
        margin-bottom: 15px;
        max-width: 80%;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        line-height: 1.5;
    }
    .bot-msg { 
        background-color: #ffffff; 
        color: #2c3e50; 
        border: 1px solid #f0f0f0;
        align-self: flex-start; 
        border-bottom-left-radius: 4px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.02);
    }
    .user-msg { 
        background: linear-gradient(135deg, #1e7e34, #28a745); 
        color: white; 
        margin-left: auto; 
        border-bottom-right-radius: 4px;
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# --- LOGIQUE DE SESSION ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "bot", "content": "Assalamu Alaikum wa Rahmatullah. Je suis votre conseiller NISFI. Je suis ravi de vous accompagner pour cette étape importante."}]

if "q_idx" not in st.session_state:
    st.session_state.q_idx = 0

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

if "gender" not in st.session_state:
    st.session_state.gender = None 

if "complete" not in st.session_state:
    st.session_state.complete = False

# --- FONCTION D'ACCORD DES QUESTIONS ---
def get_adapted_question(index, gender):
    q_data = QUESTIONS_DE_BASE[index]
    text = q_data["q"]
    if gender == "soeur":
        text = text.replace("marié", "mariée").replace("prêt", "prête").replace("divorcé", "divorcée").replace("veuf", "veuve")
    return text

# --- AFFICHAGE ---
st.markdown("<h2 style='text-align: center; color: #1e7e34; font-weight: 300;'>🌙 NISFI Médiation</h2>", unsafe_allow_html=True)

chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        div_class = "bot-msg" if msg["role"] == "bot" else "user-msg"
        st.markdown(f"<div class='chat-bubble {div_class}'>{msg['content']}</div>", unsafe_allow_html=True)

# --- LOGIQUE CONVERSATIONNELLE ---
if not st.session_state.complete:
    current_q_raw = QUESTIONS_DE_BASE[st.session_state.q_idx]["q"]
    if st.session_state.messages[-1]["content"] != current_q_raw and st.session_state.q_idx == 0:
        st.session_state.messages.append({"role": "bot", "content": current_q_raw})
        st.rerun()

user_input = st.chat_input("Échangez avec votre conseiller...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Détection du genre
    if st.session_state.q_idx == 0 and st.session_state.gender is None:
        if any(word in user_input.lower() for word in ["soeur", "sœur", "femme", "fille"]):
            st.session_state.gender = "soeur"
        else:
            st.session_state.gender = "frere"
    
    current_question_id = QUESTIONS_DE_BASE[st.session_state.q_idx]["id"]
    
    # Logique de saut (Célibataire -> pas de question enfants)
    skip_next = False
    if current_question_id == "situation":
        if any(word in user_input.lower() for word in ["célibataire", "celibataire", "jamais marié", "jamais mariée"]):
            skip_next = True

    st.session_state.q_idx += 1
    
    if skip_next and st.session_state.q_idx < len(QUESTIONS_DE_BASE):
        if QUESTIONS_DE_BASE[st.session_state.q_idx]["id"] == "enfants":
            st.session_state.q_idx += 1

    if st.session_state.q_idx < len(QUESTIONS_DE_BASE):
        next_q = get_adapted_question(st.session_state.q_idx, st.session_state.gender)
        accord_instruction = "L'utilisateur est une Sœur." if st.session_state.gender == "soeur" else "L'utilisateur est un Frère."
        
        prompt = f"""(Note pour ton attitude : {accord_instruction} Réagis comme un humain, évite toute tournure de phrase informatique ou de robot).
        Réponse reçue pour '{current_question_id}' : '{user_input}'.
        Partage une brève réflexion bienveillante sur cette réponse pour montrer que tu écoutes vraiment, puis amène naturellement la question suivante : '{next_q}'."""
    else:
        prompt = "L'entretien est fini. Conclus de manière très humaine, avec une invocation sincère pour la réussite de sa recherche."
        st.session_state.complete = True

    try:
        response = st.session_state.chat_session.send_message(prompt)
        st.session_state.messages.append({"role": "bot", "content": response.text})
    except:
        st.session_state.messages.append({"role": "bot", "content": "Qu'Allah vous facilite dans cette noble démarche. Continuons ensemble."})
    
    st.rerun()

if st.session_state.complete:
    st.balloons()
    if st.button("🔄 Commencer un nouvel échange"):
        st.session_state.clear()
        st.rerun()
