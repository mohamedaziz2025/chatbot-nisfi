import streamlit as st
import google.generativeai as genai
import time

# --- CONFIGURATION DE L'API ---
# Note : La clé API est gérée automatiquement par l'environnement
API_KEY = "" 
genai.configure(api_key=API_KEY)

# Configuration du modèle pour un ton plus naturel et humain
generation_config = {
    "temperature": 0.9,
    "top_p": 0.95,
    "max_output_tokens": 1024,
}

SYSTEM_PROMPT = """
Tu es le Médiateur Expert de NISFI, un conseiller matrimonial musulman sage et bienveillant.
TON BUT : Mener un entretien fluide pour apprendre à connaître l'utilisateur.

RÈGLES D'OR :
1. NE JAMAIS se répéter. Si tu n'as pas de nouvelle instruction, encourage l'utilisateur à répondre à la question posée.
2. TON HUMAIN : Pas de listes, pas de "En tant qu'IA". Parle comme un grand frère.
3. ÉCOUTE ACTIVE : Rebondis brièvement sur ce que l'utilisateur dit (ex: "MashaAllah, 30 ans est un bel âge pour construire un foyer") avant de passer à la suite.
4. ISLAM : Utilise des formules comme 'Barakallahou fik', 'Qu'Allah vous facilite' de façon naturelle.
5. CONCISION : 2-3 phrases maximum par réponse.
"""

# Utilisation du modèle flash pour la rapidité et éviter les blocages
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-thinking-exp-01-21",
    generation_config=generation_config,
    system_instruction=SYSTEM_PROMPT
)

# --- QUESTIONS ---
QUESTIONS = [
    {"id": "genre", "q": "Pour commencer cette belle étape, êtes-vous un frère ou une sœur ?"},
    {"id": "prenom", "q": "C'est un plaisir de vous accueillir. Quel est votre prénom ou votre Kunya ?"},
    {"id": "age", "q": "Et quel âge avez-vous ?"},
    {"id": "ville", "q": "Dans quelle ville et pays résidez-vous actuellement ?"},
    {"id": "situation", "q": "Quelle est votre situation matrimoniale actuelle ? (Célibataire, divorcé, veuf...)"},
    {"id": "enfants", "q": "Avez-vous des enfants ?"},
    {"id": "pratique", "q": "Comment décririez-vous votre cheminement et votre niveau de pratique religieuse ?"},
    {"id": "vision", "q": "Quelle est votre vision du mariage et de la vie de famille en quelques mots ?"},
    {"id": "contact", "q": "Enfin, quelle est votre adresse e-mail pour le suivi ?"}
]

# --- INTERFACE ---
st.set_page_config(page_title="NISFI AI", page_icon="🌙")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .chat-bubble { padding: 15px; border-radius: 15px; margin-bottom: 10px; font-family: sans-serif; }
    .bot-msg { background-color: white; border: 1px solid #ddd; align-self: flex-start; }
    .user-msg { background-color: #1e7e34; color: white; align-self: flex-end; text-align: right; margin-left: 20%; }
    </style>
""", unsafe_allow_html=True)

# --- INITIALISATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "q_idx" not in st.session_state:
    st.session_state.q_idx = 0
if "gender" not in st.session_state:
    st.session_state.gender = None
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# --- LOGIQUE ---
st.markdown("<h2 style='text-align: center; color: #1e7e34;'>🌙 Médiation NISFI</h2>", unsafe_allow_html=True)

# Affichage des messages
for msg in st.session_state.messages:
    cl = "user-msg" if msg["role"] == "user" else "bot-msg"
    st.markdown(f"<div class='chat-bubble {cl}'>{msg['content']}</div>", unsafe_allow_html=True)

# Première question automatique
if st.session_state.q_idx == 0 and not st.session_state.messages:
    welcome = "Assalamu Alaikum wa Rahmatullah. Je suis votre conseiller NISFI. " + QUESTIONS[0]["q"]
    st.session_state.messages.append({"role": "bot", "content": welcome})
    st.rerun()

# Entrée utilisateur
user_input = st.chat_input("Votre réponse...")

if user_input:
    # Ajouter le message utilisateur à l'écran
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Identification du genre à la première question
    if st.session_state.q_idx == 0:
        if any(x in user_input.lower() for x in ["soeur", "sœur", "femme"]):
            st.session_state.gender = "soeur"
        else:
            st.session_state.gender = "frere"

    # Préparation de la suite
    current_id = QUESTIONS[st.session_state.q_idx]["id"]
    st.session_state.q_idx += 1
    
    # Gestion de la fin ou de la question suivante
    if st.session_state.q_idx < len(QUESTIONS):
        next_q = QUESTIONS[st.session_state.q_idx]["q"]
        # Adaptation du genre
        if st.session_state.gender == "soeur":
            next_q = next_q.replace("marié", "mariée").replace("divorcé", "divorcée")
            
        prompt = f"L'utilisateur (un {st.session_state.gender}) a répondu '{user_input}' à la question sur son {current_id}. Commente brièvement avec empathie et pose la question suivante : {next_q}"
    else:
        prompt = f"L'entretien est terminé. L'utilisateur a fini de répondre. Remercie-le chaleureusement et conclus avec une dou'a."

    # Appel API avec gestion d'erreur améliorée
    with st.spinner("Réflexion de votre conseiller..."):
        try:
            response = st.session_state.chat_session.send_message(prompt)
            bot_text = response.text
        except Exception as e:
            # Fallback intelligent si l'API échoue au lieu de boucler
            bot_text = "Barakallahou fik pour votre réponse. Continuons notre échange, c'est très enrichissant. "
            if st.session_state.q_idx < len(QUESTIONS):
                bot_text += QUESTIONS[st.session_state.q_idx]["q"]

        st.session_state.messages.append({"role": "bot", "content": bot_text})
    
    st.rerun()
