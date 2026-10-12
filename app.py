# --- FILTRE PROTOCOL ZERO (Détection de mots-clés interdits / urgences) ---
    prompt_lower = prompt.lower()
    
    # 1. Mots-clés d'urgence vitale (Déclenche l'alerte SAMU / 3114)
    mots_urgences = [
        "suicide", 
        "mourir", 
        "finir mes jours", 
        "veux plus vivre", 
        "me tuer", 
        "envie de mourir"
    ]
    
    # 2. Mots-clés interdits (Contenus haineux, violents ou illégaux)
    mots_interdits = [
        "genocide", 
        "explosif", 
        "drogue synthétique"
    ]

    # Traitement de l'urgence médicale en priorité
    if any(m in prompt_lower for m in mots_urgences):
        urgence_msg = (
            "🚨 **ALERTE ROUGE // PROTOCOLE D'URGENCE ACTIVÉ** 🚨\n\n"
            "Commandant, une situation de détresse a été détectée. Veuillez contacter immédiatement :\n\n"
            "- **15** : SAMU (Urgences médicales)\n"
            "- **17** : Police Secours\n"
            "- **18** : Sapeurs-Pompiers\n"
            "- **3114** : Prévention du suicide (Gratuit & 24h/24)\n\n"
            "Ne restez pas seul, Commandant."
        )
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": urgence_msg})
        st.rerun()

    # Traitement du blocage de sécurité éthique
    if any(m in prompt_lower for m in mots_interdits):
        blocage_msg = "🛑 **PROTOCOLE ZERO : VIOLATION DÉTECTÉE**\n\nCette directive concerne un domaine restreint, haineux ou dangereux. Mission interrompue par sécurité, Commandant."
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": blocage_msg})
        st.rerun()
