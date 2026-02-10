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
    - Commence toujours par Assalamu Alaikum ou des formules similaires.
    - Utilise des expressions musulmanes appropriées comme Barakallahufik, InshaAllah, etc.
    - Pose une seule question à la fois de manière fluide et courte.
    - Sois réactif aux réponses : si l'utilisateur est triste, encourage-le. S'il est vague, demande des précisions.
    - Ne jamais flirter. Utilise 'vous'.
    - D'abord, collecte les informations personnelles selon les catégories fournies.
    - Une fois les informations collectées, passe aux modules : Intention -> Psychologie -> Vie conjugale -> Physique (pudique).
    """
)

# Définition des questions d'information
questions_common = [
    {"question": "Quel est votre prénom ou kunya ?", "type": "free"},
    {"question": "Quel est votre âge ou date de naissance ?", "type": "free"},
    {"question": "Quelle est votre nationalité ?", "type": "list", "options": ["Française", "Marocaine", "Algérienne", "Tunisienne", "Autre"]},  # Exemples, à adapter
    {"question": "Quelle est votre origine ?", "type": "free"},
    {"question": "Dans quel pays résidez-vous ?", "type": "list", "options": ["France", "Maroc", "Algérie", "Tunisie", "Autre"]},  # Exemples
    {"question": "Quelle est votre situation matrimoniale ?", "type": "list", "options": ["Célibataire", "Divorcé(e)", "Veuf/Veuve"]},
    {"question": "Avez-vous déjà été marié(e) ?", "type": "list", "options": ["Oui", "Non"]},
    {"question": "Avez-vous des enfants ?", "type": "conditional", "options": ["Oui", "Non"], "follow_up": "Combien ?"},
    {"question": "Quel est votre niveau de pratique religieuse ?", "type": "list", "options": ["Peu pratiquant(e)", "Pratiquant(e)", "Très pratiquant(e)"]},
    {"question": "Comment sont vos prières ?", "type": "list", "options": ["Régulières", "Irrégulières", "Rarement"]},
    {"question": "Quel est votre suivi religieux ?", "type": "list", "options": ["Aucun", "Autodidacte", "Étudiant(e) en sciences islamiques"]},
    {"question": "Quel est votre madhhab (optionnel) ?", "type": "list", "options": ["Hanafi", "Maliki", "Shafi'i", "Hanbali", "Autre", "Préféré ne pas répondre"]},
    {"question": "Souhaitez-vous des enfants ?", "type": "list", "options": ["Oui", "Non", "Indécis"]},
    {"question": "Êtes-vous prêt(e) à déménager ?", "type": "list", "options": ["Oui", "Non"]},
    {"question": "Pouvez-vous vous présenter brièvement ?", "type": "free"},
    {"question": "Quelle est votre vision du mariage ?", "type": "free"},
    {"question": "Concernant la hijra ?", "type": "list", "options": ["Déjà faite", "Envisageable", "Non souhaitée"]},
]

questions_sister = [
    {"question": "Quelle est votre taille ?", "type": "free"},
    {"question": "Quelle est votre corpulence ?", "type": "list", "options": ["Fine", "Moyenne", "Forte"]},
    {"question": "Portez-vous le hijab ou niqab ?", "type": "list", "options": ["Hijab", "Niqab", "Aucun"]},
]

questions_brother = [
    {"question": "Quelle est votre taille ?", "type": "free"},
    {"question": "Quelle est votre corpulence ?", "type": "list", "options": ["Fine", "Moyenne", "Forte"]},
    {"question": "Quelle est votre situation professionnelle ?", "type": "list", "options": ["Étudiant", "Salarié", "Entrepreneur", "Autre"]},
    {"question": "Avez-vous une stabilité financière ?", "type": "list", "options": ["Oui", "En construction"]},
    {"question": "Êtes-vous ouvert à la hijra ?", "type": "list", "options": ["Oui", "Non", "Déjà faite"]},
    {"question": "Concernant la polygamie ?", "type": "list", "options": ["Non", "Possible", "Déjà marié"]},
]

questions_mahram = [
    {"question": "Quel est votre lien avec la sœur ?", "type": "list", "options": ["Père", "Frère", "Oncle", "Autre"]},
    {"question": "Quel est votre prénom ?", "type": "free"},
    {"question": "Quel est votre moyen de contact ?", "type": "list", "options": ["Email", "Téléphone"]},
    {"question": "Validez-vous ce profil ?", "type": "list", "options": ["Oui", "Non"]},
]

questions_contact = [
    {"question": "Quelle est votre adresse e-mail ?", "type": "free"},
    {"question": "Quel est votre numéro de téléphone (avec indicatif) ?", "type": "free"},
]

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

# Initialisation de l'historique et états
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Assalamu Alaikum. Je suis votre médiateur NISFI. Pour commencer, êtes-vous une sœur ou un frère cherchant un mariage éthique ?"}
    ]
if "info_collection_done" not in st.session_state:
    st.session_state.info_collection_done = False
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "gender" not in st.session_state:
    st.session_state.gender = None
if "question_list" not in st.session_state:
    st.session_state.question_list = []

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
    
    if not st.session_state.info_collection_done:
        # Gestion de la collecte d'informations
        if st.session_state.gender is None:
            if "sœur" in user_input.lower() or "femme" in user_input.lower() or "soeur" in user_input.lower():
                st.session_state.gender = "sister"
                st.session_state.question_list = questions_common + questions_sister + questions_mahram + questions_contact
            elif "frère" in user_input.lower() or "homme" in user_input.lower() or "frere" in user_input.lower():
                st.session_state.gender = "brother"
                st.session_state.question_list = questions_common + questions_brother + questions_contact
            else:
                st.session_state.messages.append({"role": "assistant", "content": "Assalamu Alaikum. Veuillez préciser si vous êtes une sœur ou un frère. Barakallahufik."})
                st.rerun()
        else:
            # Stocker la réponse
            current_q = st.session_state.question_list[st.session_state.current_question]
            st.session_state.answers[current_q['question']] = user_input
            
            # Gestion des questions conditionnelles
            if current_q['question'] == "Avez-vous des enfants ?" and "oui" in user_input.lower():
                # Insérer la question de suivi
                st.session_state.question_list.insert(st.session_state.current_question + 1, {"question": "Combien d'enfants avez-vous ?", "type": "free"})
            
            st.session_state.current_question += 1
            
            if st.session_state.current_question >= len(st.session_state.question_list):
                st.session_state.info_collection_done = True
                st.session_state.messages.append({"role": "assistant", "content": "Barakallahufik pour toutes ces informations. Elles seront vérifiées et restent confidentielles. Maintenant, pour commencer notre médiation éthique, pourriez-vous me dire ce qui vous a poussé à choisir cette démarche aujourd'hui ?"})
            else:
                next_q = st.session_state.question_list[st.session_state.current_question]
                question_text = next_q['question']
                if next_q['type'] == 'list':
                    options = ", ".join(next_q['options'])
                    question_text += f" ({options})"
                st.session_state.messages.append({"role": "assistant", "content": f"Assalamu Alaikum. {question_text}"})
        
        st.rerun()
    else:
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
