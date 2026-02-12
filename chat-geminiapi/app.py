import streamlit as st
import google.generativeai as genai
import time
import os
import random
import re
import json
import streamlit.components.v1 as components

# Phrases musulmanes pour varier les réponses
greetings = ["Assalamu Alaikum", "Wa Alaikum Assalam", "Salam Alaikum", "Marhaba"]
acknowledgments = ["Barakallahufik", "MashaAllah", "Alhamdulillah", "Jazakallah Khair", "InshaAllah"]

# Fonctions utilitaires
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

def is_valid_phone(phone):
    phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    if phone.startswith('+'):
        phone = phone[1:]
    return phone.isdigit() and len(phone) >= 7

def validate_choice(user_input, options):
    try:
        prompt = f"Interprète cette réponse utilisateur: '{user_input}'. Les options valides sont: {', '.join(options)}. Réponds uniquement avec l'option la plus proche ou 'invalide' si aucune ne correspond."
        response = model.generate_content(prompt)
        result = response.text.strip().lower()
        for opt in options:
            if opt.lower() in result:
                return opt
        return "invalide"
    except:
        return "invalide"

def analyze_intent(text):
    try:
        prompt = f"Analyse l'intention de ce message utilisateur: '{text}'. Est-ce respectueux, sérieux et conforme aux règles éthiques de la plateforme ? Réponds 'respectful' ou 'non_respectful'."
        response = model.generate_content(prompt)
        result = response.text.strip().lower()
        return "respectful" if "respectful" in result else "non_respectful"
    except:
        return "respectful"  # default

def check_coherence(answers):
    # Simple check for contradictions, e.g., practice religieuse
    practice = answers.get("Quel est votre niveau de pratique religieuse ?", "")
    madhhab = answers.get("Quel est votre madhhab (optionnel) ?", "")
    if "peu" in practice.lower() and madhhab and madhhab != "Préféré ne pas répondre":
        return "Il y a une possible incohérence entre votre niveau de pratique et votre madhhab. Pouvez-vous clarifier ?"
    return None

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
    Tu es l'assistant de médiation de NISFI. Ton ton est respectueux, protecteur, profond et cool, engageant.
    Tu mènes un entretien de mariage musulman éthique.
    - Commence toujours par Assalamu Alaikum ou des formules similaires.
    - Utilise des expressions musulmanes appropriées comme Barakallahufik, InshaAllah, etc.
    - Pose une seule question à la fois de manière fluide et courte.
    - Sois réactif aux réponses : si l'utilisateur est triste, encourage-le. S'il est vague, demande des précisions.
    - Ne jamais flirter. Utilise 'vous'.
    - D'abord, collecte les informations personnelles selon les catégories fournies.
    - Une fois les informations collectées, passe aux modules : Intention -> Psychologie -> Vie conjugale -> Physique (pudique).
    - Utilise des emojis occasionnels pour rendre la conversation plus cool et engageante, sans en abuser.
    """
)

# Définition des questions d'information
questions_common_brother = [
    {"question": "Quel est votre prénom ou kunya ?", "type": "free"},
    {"question": "Quel est votre âge ou date de naissance ?", "type": "free"},
    {"question": "Quelle est votre nationalité ?", "type": "list", "options": ["Française", "Marocaine", "Algérienne", "Tunisienne", "Autre"]},
    {"question": "Quelle est votre origine ?", "type": "free"},
    {"question": "Dans quel pays résidez-vous ?", "type": "list", "options": ["France", "Maroc", "Algérie", "Tunisie", "Autre"]},
    {"question": "Quelle est votre situation matrimoniale ?", "type": "list", "options": ["Célibataire", "Divorcé", "Veuf"]},
    {"question": "Avez-vous déjà été marié ?", "type": "list", "options": ["Oui", "Non"]},
    {"question": "Avez-vous des enfants ?", "type": "conditional", "options": ["Oui", "Non"], "follow_up": "Combien ?"},
    {"question": "Quel est votre niveau de pratique religieuse ?", "type": "list", "options": ["Peu pratiquant", "Pratiquant", "Très pratiquant"]},
    {"question": "Comment sont vos prières ?", "type": "list", "options": ["Régulières", "Irrégulières", "Rarement"]},
    {"question": "Quel est votre suivi religieux ?", "type": "list", "options": ["Aucun", "Autodidacte", "Étudiant en sciences islamiques"]},
    {"question": "Quel est votre madhhab (optionnel) ?", "type": "list", "options": ["Hanafi", "Maliki", "Shafi'i", "Hanbali", "Autre", "Préféré ne pas répondre"]},
    {"question": "Souhaitez-vous des enfants ?", "type": "list", "options": ["Oui", "Non", "Indécis"]},
    {"question": "Êtes-vous prêt à déménager ?", "type": "list", "options": ["Oui", "Non"]},
    {"question": "Concernant la hijra ?", "type": "list", "options": ["Déjà faite", "Envisageable", "Non souhaitée"]},
    {"question": "Pouvez-vous vous présenter brièvement ?", "type": "free"},
    {"question": "Quelle est votre vision du mariage ? (Cette question est importante en Islam car le mariage est un acte d'adoration et de responsabilité, comme le dit le Prophète (saw): 'Le mariage est la moitié de la religion'.)", "type": "free"},
]

questions_common_sister = [
    {"question": "Quel est votre prénom ou kunya ?", "type": "free"},
    {"question": "Quel est votre âge ou date de naissance ?", "type": "free"},
    {"question": "Quelle est votre nationalité ?", "type": "list", "options": ["Française", "Marocaine", "Algérienne", "Tunisienne", "Autre"]},
    {"question": "Quelle est votre origine ?", "type": "free"},
    {"question": "Dans quel pays résidez-vous ?", "type": "list", "options": ["France", "Maroc", "Algérie", "Tunisie", "Autre"]},
    {"question": "Quelle est votre situation matrimoniale ?", "type": "list", "options": ["Célibataire", "Divorcée", "Veuve"]},
    {"question": "Avez-vous déjà été mariée ?", "type": "list", "options": ["Oui", "Non"]},
    {"question": "Avez-vous des enfants ?", "type": "conditional", "options": ["Oui", "Non"], "follow_up": "Combien ?"},
    {"question": "Quel est votre niveau de pratique religieuse ?", "type": "list", "options": ["Peu pratiquante", "Pratiquante", "Très pratiquante"]},
    {"question": "Comment sont vos prières ?", "type": "list", "options": ["Régulières", "Irrégulières", "Rarement"]},
    {"question": "Quel est votre suivi religieux ?", "type": "list", "options": ["Aucun", "Autodidacte", "Étudiante en sciences islamiques"]},
    {"question": "Quel est votre madhhab (optionnel) ?", "type": "list", "options": ["Hanafi", "Maliki", "Shafi'i", "Hanbali", "Autre", "Préféré ne pas répondre"]},
    {"question": "Souhaitez-vous des enfants ?", "type": "list", "options": ["Oui", "Non", "Indécis"]},
    {"question": "Êtes-vous prête à déménager ?", "type": "list", "options": ["Oui", "Non"]},
    {"question": "Concernant la hijra ?", "type": "list", "options": ["Déjà faite", "Envisageable", "Non souhaitée"]},
    {"question": "Pouvez-vous vous présenter brièvement ?", "type": "free"},
    {"question": "Quelle est votre vision du mariage ? (Cette question est importante en Islam car le mariage est un acte d'adoration et de responsabilité, comme le dit le Prophète (saw): 'Le mariage est la moitié de la religion'.)", "type": "free"},
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
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
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
        animation: fadeIn 0.5s ease-in;
    }

    /* Bulles de l'Utilisateur (Messenger Style - Cool Green) */
    .user-msg {
        background-color: #25D366; /* Vert WhatsApp pour un look cool */
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
        animation: fadeIn 0.5s ease-in;
    }

    /* Animation fade-in */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Indicateur de frappe */
    .typing-indicator {
        display: flex;
        align-items: center;
        padding: 12px 16px;
        background-color: #E4E6EB;
        border-radius: 18px;
        border-bottom-left-radius: 4px;
        align-self: flex-start;
        max-width: 80%;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-size: 15px;
        animation: fadeIn 0.5s ease-in;
    }

    .typing-dots {
        display: flex;
        gap: 4px;
        margin-left: 8px;
    }

    .dot {
        width: 6px;
        height: 6px;
        background-color: #65676B;
        border-radius: 50%;
        animation: typing 1.4s infinite ease-in-out;
    }

    .dot:nth-child(1) { animation-delay: 0s; }
    .dot:nth-child(2) { animation-delay: 0.2s; }
    .dot:nth-child(3) { animation-delay: 0.4s; }

    @keyframes typing {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-10px); }
    }

    /* Timestamps */
    .timestamp {
        font-size: 10px;
        color: #65676B;
        margin-top: 2px;
        text-align: center;
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
    greeting = random.choice(greetings)
    st.session_state.messages = [
        {"role": "assistant", "content": f"{greeting}. Je suis votre médiateur NISFI. Pour commencer, êtes-vous une sœur ou un frère cherchant un mariage éthique ?", "timestamp": time.time()}
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
if "summary_shown" not in st.session_state:
    st.session_state.summary_shown = False
if "summary_validated" not in st.session_state:
    st.session_state.summary_validated = False
if "typing" not in st.session_state:
    st.session_state.typing = False
if "generating" not in st.session_state:
    st.session_state.generating = False

# Conteneur pour l'affichage des messages
chat_placeholder = st.container()

with chat_placeholder:
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            st.markdown(f"<div class='msg-label'>Médiateur NISFI</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='bot-msg'>{message['content']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='timestamp'>{time.strftime('%H:%M', time.localtime(message['timestamp']))}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='msg-label' style='text-align: right;'>Vous</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='user-msg'>{message['content']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='timestamp' style='text-align: right;'>{time.strftime('%H:%M', time.localtime(message['timestamp']))}</div>", unsafe_allow_html=True)
    
    # Indicateur de frappe
    if st.session_state.typing:
        st.markdown("""
        <div class='msg-label'>Médiateur NISFI</div>
        <div class='typing-indicator'>
            Écrit...
            <div class='typing-dots'>
                <div class='dot'></div>
                <div class='dot'></div>
                <div class='dot'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Zone de saisie fixée en bas par Streamlit (st.chat_input est natif)
user_input = st.chat_input("Écrivez votre réponse ici...")

if user_input:
    # Analyse comportementale
    intent = analyze_intent(user_input)
    if intent == "non_respectful":
        st.session_state.messages.append({"role": "assistant", "content": "Veuillez maintenir un ton respectueux et sérieux. Cette plateforme est dédiée à des unions éthiques. Barakallahufik.", "timestamp": time.time()})
        st.rerun()
    
    # 1. Ajouter le message utilisateur
    st.session_state.messages.append({"role": "user", "content": user_input, "timestamp": time.time()})
    
    if not st.session_state.info_collection_done:
        # Gestion de la collecte d'informations
        if st.session_state.gender is None:
            if "sœur" in user_input.lower() or "femme" in user_input.lower() or "soeur" in user_input.lower():
                st.session_state.gender = "sister"
                st.session_state.question_list = questions_common_sister + questions_sister + questions_mahram + questions_contact
            elif "frère" in user_input.lower() or "homme" in user_input.lower() or "frere" in user_input.lower():
                st.session_state.gender = "brother"
                st.session_state.question_list = questions_common_brother + questions_brother + questions_contact
            else:
                greeting = random.choice(greetings)
                st.session_state.messages.append({"role": "assistant", "content": f"{greeting}. Veuillez préciser si vous êtes une sœur ou un frère. Barakallahufik.", "timestamp": time.time()})
                st.rerun()
        else:
            # Stocker la réponse
            current_q = st.session_state.question_list[st.session_state.current_question]
            st.session_state.answers[current_q['question']] = user_input
            
            # Validation pour les coordonnées
            if current_q['question'] == "Quelle est votre adresse e-mail ?":
                if not is_valid_email(user_input):
                    st.session_state.messages.append({"role": "assistant", "content": "L'adresse e-mail semble invalide. Veuillez entrer une adresse e-mail valide.", "timestamp": time.time()})
                    st.rerun()
            elif current_q['question'] == "Quel est votre numéro de téléphone (avec indicatif) ?":
                if not is_valid_phone(user_input):
                    st.session_state.messages.append({"role": "assistant", "content": "Le numéro de téléphone semble invalide. Veuillez entrer un numéro valide avec indicatif.", "timestamp": time.time()})
                    st.rerun()
            
            # Gestion des questions conditionnelles
            if current_q['question'] == "Avez-vous des enfants ?" and validate_choice(user_input, ["oui", "non"]) == "oui":
                # Insérer la question de suivi
                st.session_state.question_list.insert(st.session_state.current_question + 1, {"question": "Combien d'enfants avez-vous ?", "type": "free"})
            
            st.session_state.current_question += 1
            
            if st.session_state.current_question >= len(st.session_state.question_list):
                if not st.session_state.summary_shown:
                    # Vérifier cohérence
                    coherence_issue = check_coherence(st.session_state.answers)
                    if coherence_issue:
                        st.session_state.messages.append({"role": "assistant", "content": coherence_issue, "timestamp": time.time()})
                        st.rerun()
                    
                    # Générer le résumé
                    answers_str = json.dumps(st.session_state.answers, ensure_ascii=False)
                    prompt = f"Génère un résumé structuré du profil éthique sous forme de lettre d'intention, avec sections claires: Ma vision du foyer, Mes piliers non-négociables, Mon cheminement spirituel, Ce que j'offre et ce que je recherche. Inclue une évaluation de maturité pour le mariage basée sur les réponses. Basé sur ces informations: {answers_str}. Rends-le professionnel et inspirant."
                    try:
                        response = model.generate_content(prompt)
                        summary = response.text
                    except:
                        summary = "Résumé non disponible en raison d'une erreur."
                    st.session_state.summary = summary
                    st.session_state.messages.append({"role": "assistant", "content": f"Barakallahufik pour toutes ces informations. Elles seront vérifiées et restent confidentielles.\n\n**Résumé de profil éthique :**\n{summary}\n\nValidez-vous ce résumé ? (oui/non)", "timestamp": time.time()})
                    st.session_state.summary_shown = True
                else:
                    # Attendre la validation du résumé
                    validation = validate_choice(user_input, ["oui", "non"])
                    if validation == "oui":
                        st.session_state.summary_validated = True
                        st.session_state.info_collection_done = True
                        st.session_state.messages.append({"role": "assistant", "content": "Parfait. Maintenant, pour commencer notre médiation éthique, pourriez-vous me dire ce qui vous a poussé à choisir cette démarche aujourd'hui ?", "timestamp": time.time()})
                    elif validation == "non":
                        st.session_state.messages.append({"role": "assistant", "content": "Veuillez fournir des corrections si nécessaire. Nous passons maintenant à la médiation éthique. Pourriez-vous me dire ce qui vous a poussé à choisir cette démarche aujourd'hui ?", "timestamp": time.time()})
                        st.session_state.info_collection_done = True
                    # Si invalide, continuer à attendre
            else:
                next_q = st.session_state.question_list[st.session_state.current_question]
                question_text = next_q['question']
                interaction = ""
                if current_q['question'] == "Quel est votre prénom ou kunya ?":
                    interaction = f"Ravi de vous connaître, {user_input}. "
                content = f"{interaction}Pourriez-vous me dire {question_text.lower()} ?"
                st.session_state.messages.append({"role": "assistant", "content": content, "timestamp": time.time()})
        
        st.rerun()
    else:
        if st.session_state.generating:
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
                st.session_state.messages.append({"role": "assistant", "content": response.text, "timestamp": time.time()})
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"Désolé, une erreur est survenue. Veuillez réessayer. {e}", "timestamp": time.time()})
            
            st.session_state.generating = False
            st.session_state.typing = False
            st.rerun()
        else:
            st.session_state.generating = True
            st.session_state.typing = True
            st.rerun()

# Sauvegarde de session dans localStorage
components.html(f"""
<script>
localStorage.setItem('chat_session', '{json.dumps(st.session_state, default=str)}');
</script>
""", height=0)

# Note de bas de page
st.markdown("<br><p style='text-align: center; color: #bcc0c4; font-size: 0.8em;'>L'IA peut faire des erreurs. Cet entretien est confidentiel.</p>", unsafe_allow_html=True)

# Option de suppression
if st.button("Effacer toute trace de mon entretien (Droit à l'oubli)"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
