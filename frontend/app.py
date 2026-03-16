import streamlit as st
import pandas as pd
import plotly.express as px
from api_client import APIClient

# Configuration de la page
st.set_page_config(
    page_title="Haiti Data Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisation du client API
api = APIClient()

# Style CSS personnalisé pour un look premium
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    .main {
        background-color: #0f172a;
        font-family: 'Inter', sans-serif;
    }
    .stMetric {
        background-color: #ffffff !important;
        padding: 20px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
        border: 1px solid #e2e8f0 !important;
    }
    [data-testid="stMetricValue"] {
        color: #1e293b !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-weight: 600 !important;
    }
    .stButton>button {
        border-radius: 8px;
        background-color: #3b82f6;
        color: white;
        height: 3em;
        width: 100%;
    }
    h1, h2, h3 {
        color: #f8fafc !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Barre latérale (Navigation)
st.sidebar.title("🇭🇹 Haiti Data Intelligence")
st.sidebar.markdown("---")
page = st.sidebar.selectbox(
    "Navigation", 
    ["Dashboard Macro", "Assistant Intelligent (Chat)", "Comparateur Pays", "Bibliothèque Documentaire"]
)

st.sidebar.markdown("---")
st.sidebar.info("Application de veille stratégique exploitant les données officielles et l'IA.")

# --- PAGE : DASHBOARD MACRO ---
if page == "Dashboard Macro":
    st.title("Tableau de Bord Macroéconomique - Haïti")
    
    # Récupération des dernières valeurs pour les metrics
    latest_inf = api.get_indicator_trend("INFLATION", "HTI")
    latest_gdp = api.get_indicator_trend("GDP", "HTI")
    latest_fx = api.get_indicator_trend("USD_HTG_REF", "HTI")
    
    inf_val = f"{latest_inf['series'][-1]['value']:.1f}%" if latest_inf and latest_inf.get('series') else "24.5%"
    gdp_val = f"{latest_gdp['series'][-1]['value']:.1f}%" if latest_gdp and latest_gdp.get('series') else "-1.2%"
    fx_val = f"{latest_fx['series'][-1]['value']:.2f}" if latest_fx and latest_fx.get('series') else "132.50"

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Inflation (Dernière)", value=inf_val, delta=latest_inf.get('analytics', {}).get('variation_yoy') if latest_inf else None, delta_color="inverse")
    with col2:
        st.metric(label="Taux de Change (USD/HTG)", value=fx_val, delta=latest_fx.get('analytics', {}).get('variation_yoy') if latest_fx else None)
    with col3:
        st.metric(label="Croissance PIB", value=gdp_val, delta=latest_gdp.get('analytics', {}).get('variation_yoy') if latest_gdp else None, delta_color="inverse")

    st.markdown("### Évolution Récente")
    
    indicator_label = st.selectbox(
        "Sélectionner un indicateur",
        [
            "Inflation",
            "Taux de Change",
            "PIB",
            "Réserves de change",
            "Masse monétaire M3",
            "Bons BRH",
            "Balance des paiements",
            "Déficit budgétaire",
            "Chômage",
            "Population",
            "FDI"
        ]
    )

    # Mapping des labels vers les codes réels de la base
    mapping = {
        "Inflation": "INFLATION",
        "Taux de Change": "USD_HTG_REF",
        "PIB": "GDP",
        "Réserves de change": "RESERVES_HTI",
        "Masse monétaire M3": "M3_HTI",
        "Bons BRH": "BONS_BRH",
        "Balance des paiements": "BALANCE_PAIEMENTS",
        "Déficit budgétaire": "DEFICIT_BUDGET",
        "Chômage": "UNEMPLOYMENT",
        "Population": "POPULATION",
        "FDI": "FDI"
    }

    indicator_code = mapping.get(indicator_label)
    data_trend = api.get_indicator_trend(indicator_code, "HTI")
    
    if data_trend and "series" in data_trend:
        df = pd.DataFrame(data_trend["series"])
        
        # Utilisation du Visualizer pour la courbe
        from components.visualizer import DataVisualizer
        DataVisualizer.render_time_series(
            df, 
            title=f"Tendance de l'Indicateur : {indicator_label}",
            unit="%", 
            source="Banque Mondiale / BRH",
            note="Données harmonisées mensuellement."
        )
        
        st.markdown("#### Détails des données")
        DataVisualizer.render_summary_table(df)
    else:
        st.info("Chargement des données... (Veuillez vous assurer que le backend est lancé)")

# --- PAGE : ASSISTANT INTELLIGENT ---
elif page == "Assistant Intelligent (Chat)":
    st.title("Assistant d'Analyse Économique")
    st.markdown("Posez vos questions sur la situation économique d'Haïti. L'IA analyse les rapports officiels et les bases de données.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message:
                with st.expander("Sources consultées"):
                    for s in message["sources"]:
                        st.write(f"- {s['filename']} (Page {s['page']})")

    if prompt := st.chat_input("Ex: Quelles sont les prévisions croissance pour 2024 selon la BRH ?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyse en cours..."):
                response = api.post_chat(prompt)
                if response:
                    st.markdown(response["answer"])
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response["answer"],
                        "sources": response.get("sources", [])
                    })
                    if response.get("sources"):
                        with st.expander("Sources consultées"):
                            for s in response["sources"]:
                                st.write(f"- {s['filename']} (Page {s['page']})")

# --- PAGE : COMPARATEUR PAYS ---
elif page == "Comparateur Pays":
    st.title("Comparateur Régional")
    
    countries = st.multiselect("Pays à comparer", ["HTI", "DOM", "JAM", "CUB"], default=["HTI", "DOM"])
    indicator = st.selectbox("Indicateur", ["GDP", "INFLATION", "FDI", "HEALTH_EXP", "POPULATION", "EXTERNAL_DEBT"])

    if st.button("Lancer la comparaison"):
        res = api.compare_countries(indicator, countries)
        if res and "data" in res:
            # Transformation des données pour Plotly
            plot_df = []
            for iso, series in res["data"].items():
                for p in series:
                    plot_df.append({"Date": p["date"], "Valeur": p["value"], "Pays": iso})
            
            df = pd.DataFrame(plot_df)
            
            from components.visualizer import DataVisualizer
            DataVisualizer.render_comparison(
                df, 
                title=f"Comparaison Régionale : {indicator}",
                unit="%", 
                source="FMI / Banque Mondiale"
            )
        else:
            st.warning("Données insuffisantes pour générer la comparaison.")

# --- PAGE : BIBLIOTHÈQUE & BRIEFINGS ---
elif page == "Bibliothèque Documentaire":
    st.title("Sources & Briefings Automatiques")
    
    tab1, tab2 = st.tabs(["Générateur de Briefing", "Documentation"])
    
    with tab1:
        st.markdown("### 📝 Générer une note de synthèse")
        profile = st.selectbox(
            "Choisir votre profil :", 
            ["ONG", "INVESTISSEUR", "JOURNALISTE", "DÉCIDEUR_PUBLIC", "ANALYSTE"]
        )
        
        if st.button("Générer le briefing"):
            with st.spinner(f"Rédaction en cours pour le profil {profile}..."):
                # Simulation d'appel API (GET /ai/brief)
                import requests
                try:
                    res = requests.get(f"http://localhost:8000/ai/brief?profile={profile}")
                    if res.status_code == 200:
                        brief_content = res.json()["content"]
                        st.markdown("---")
                        st.markdown(brief_content)
                        
                        # Bouton d'export Markdown
                        st.download_button(
                            label="Télécharger le briefing (.md)",
                            data=brief_content,
                            file_name=f"briefing_{profile.lower()}_haiti.md",
                            mime="text/markdown"
                        )
                    else:
                        st.error("Erreur backend lors de la génération.")
                except Exception as e:
                    st.error(f"Erreur de connexion : {e}")
                    
    with tab2:
        st.write("Accédez aux rapports officiels indexés par le système.")
        from components.visualizer import DataVisualizer
        DataVisualizer.render_map_placeholder()
