# -*- coding: utf-8 -*-
"""
Streamlit App pour la prédiction de la qualité de l'air
"""
import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# Configuration de la page
st.set_page_config(
    page_title="Air Quality Prediction",
    page_icon="globe",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
    <style>
    .main { padding: 2rem; }
    .metric-card { background-color: #f0f2f6; padding: 1.5rem; border-radius: 0.5rem; margin: 1rem 0; }
    </style>
    """, unsafe_allow_html=True)

# Configuration de l'API
API_URL = "http://127.0.0.1:8000"

# Titre
st.title("Air Quality Prediction System")
st.markdown("Prediction de NO2 basee sur les donnees de capteurs")

# Sidebar pour la navigation
with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Selectionnez une page:",
        ["Prediction", "Donnees de test", "Infos Modele", "Historique"]
    )

# ============= PAGE 1: PRÉDICTION =============
if page == "Prediction":
    st.header("Predicteur de NO2")
    
    # Vérifier la connexion à l'API
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            st.success("API connectee")
        else:
            st.error("API indisponible")
    except:
        st.error("Impossible de se connecter a l'API")
        st.info("Assurez-vous que l'API est lancee: python -m uvicorn src.api:app --reload")
    
    # Créer deux colonnes
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Parametres de gaz")
        CO_GT = st.number_input("CO (mg/m³)", value=2.6, step=0.1)
        PT08_S1_CO = st.number_input("Capteur PT08.S1(CO)", value=1360.0, step=10.0)
        NMHC_GT = st.number_input("NMHC (µg/m³)", value=150.0, step=5.0)
        C6H6_GT = st.number_input("Benzene (µg/m³)", value=11.9, step=0.1)
        PT08_S2_NMHC = st.number_input("Capteur PT08.S2(NMHC)", value=1046.0, step=10.0)
    
    with col2:
        st.subheader("Parametres additionnels")
        NOx_GT = st.number_input("NOx (ppb)", value=166.0, step=5.0)
        PT08_S3_NOx = st.number_input("Capteur PT08.S3(NOx)", value=1056.0, step=10.0)
        PT08_S4_NO2 = st.number_input("Capteur PT08.S4(NO2)", value=1692.0, step=10.0)
        PT08_S5_O3 = st.number_input("Capteur PT08.S5(O3)", value=1268.0, step=10.0)
        T = st.number_input("Temperature (°C)", value=13.6, step=0.1)
        RH = st.number_input("Humidite relative (%)", value=48.9, step=0.1)
        AH = st.number_input("Humidite absolue", value=0.7578, step=0.01)
    
    # Bouton de prédiction
    col1, col2, col3 = st.columns(3)
    with col2:
        if st.button("Predire NO2", use_container_width=True, type="primary"):
            with st.spinner("Prediction en cours..."):
                try:
                    payload = {
                        "CO_GT": CO_GT,
                        "PT08_S1_CO": PT08_S1_CO,
                        "NMHC_GT": NMHC_GT,
                        "C6H6_GT": C6H6_GT,
                        "PT08_S2_NMHC": PT08_S2_NMHC,
                        "NOx_GT": NOx_GT,
                        "PT08_S3_NOx": PT08_S3_NOx,
                        "PT08_S4_NO2": PT08_S4_NO2,
                        "PT08_S5_O3": PT08_S5_O3,
                        "T": T,
                        "RH": RH,
                        "AH": AH
                    }
                    
                    response = requests.post(
                        f"{API_URL}/predict",
                        json=payload,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success("Prediction reussie!")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("NO2 Predit (µg/m³)", f"{data['prediction']:.2f}")
                        with col2:
                            st.metric("Version", data['model_version'])
                        with col3:
                            st.metric("Confiance", f"{data['confidence_metrics'].get('confidence', 'N/A')}")
                        
                        if 'history' not in st.session_state:
                            st.session_state.history = []
                        
                        st.session_state.history.append({
                            'timestamp': datetime.now(),
                            'prediction': data['prediction'],
                            'CO_GT': CO_GT,
                            'NOx_GT': NOx_GT,
                            'T': T,
                            'RH': RH
                        })
                    else:
                        st.error(f"Erreur: {response.status_code}")
                
                except requests.exceptions.ConnectionError:
                    st.error("Impossible de se connecter a l'API")
                except Exception as e:
                    st.error(f"Erreur: {str(e)}")

# ============= PAGE 2: DONNEES DE TEST =============
elif page == "Donnees de test":
    st.header("Donnees de test predefinies")
    
    test_cases = {
        "Cas Normal": {"CO_GT": 2.6, "PT08_S1_CO": 1360.0, "NMHC_GT": 150.0, "C6H6_GT": 11.9, 
                       "PT08_S2_NMHC": 1046.0, "NOx_GT": 166.0, "PT08_S3_NOx": 1056.0, 
                       "PT08_S4_NO2": 1692.0, "PT08_S5_O3": 1268.0, "T": 13.6, "RH": 48.9, "AH": 0.7578},
        "Pollution elevee": {"CO_GT": 5.0, "PT08_S1_CO": 2000.0, "NMHC_GT": 300.0, "C6H6_GT": 25.0,
                             "PT08_S2_NMHC": 2000.0, "NOx_GT": 300.0, "PT08_S3_NOx": 2000.0,
                             "PT08_S4_NO2": 3000.0, "PT08_S5_O3": 2000.0, "T": 25.0, "RH": 60.0, "AH": 1.2},
        "Pollution faible": {"CO_GT": 1.0, "PT08_S1_CO": 800.0, "NMHC_GT": 50.0, "C6H6_GT": 5.0,
                             "PT08_S2_NMHC": 500.0, "NOx_GT": 80.0, "PT08_S3_NOx": 600.0,
                             "PT08_S4_NO2": 900.0, "PT08_S5_O3": 700.0, "T": 10.0, "RH": 40.0, "AH": 0.5}
    }
    
    selected_case = st.selectbox("Selectionnez un cas de test:", list(test_cases.keys()))
    data = test_cases[selected_case]
    st.write(pd.DataFrame(list(data.items()), columns=["Parametre", "Valeur"]).set_index("Parametre").T)
    
    if st.button("Tester ce cas", use_container_width=True, type="primary"):
        with st.spinner("Prediction en cours..."):
            try:
                response = requests.post(f"{API_URL}/predict", json=data, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    st.success("Prediction reussie!")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("NO2 Predit", f"{result['prediction']:.2f} µg/m³")
                    with col2:
                        st.metric("Modele", result['model_version'])
                    st.json(result)
                else:
                    st.error(f"Erreur: {response.status_code}")
            except Exception as e:
                st.error(f"Erreur: {str(e)}")

# ============= PAGE 3: INFOS MODELE =============
elif page == "Infos Modele":
    st.header("Informations du modele")
    
    try:
        response = requests.get(f"{API_URL}/model-info", timeout=5)
        if response.status_code == 200:
            info = response.json()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Modele", info.get("model_name", "N/A"))
            with col2:
                st.metric("Version", info.get("model_version", "N/A"))
            with col3:
                st.metric("Stage", info.get("model_stage", "N/A"))
            
            if "metrics" in info:
                st.subheader("Metriques")
                st.dataframe(pd.DataFrame([info["metrics"]]), use_container_width=True)
            
            if "feature_importance" in info:
                st.subheader("Importance des features (Top 10)")
                features = info["feature_importance"]
                top_features = sorted(features.items(), key=lambda x: x[1], reverse=True)[:10]
                fig = go.Figure(data=[go.Bar(y=[f[0] for f in top_features], x=[f[1] for f in top_features], orientation='h')])
                fig.update_layout(title="Importance des features", height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Donnees completes")
            st.json(info)
        else:
            st.error(f"Erreur: {response.status_code}")
    except Exception as e:
        st.error(f"Impossible de recuperer les infos: {str(e)}")

# ============= PAGE 4: HISTORIQUE =============
elif page == "Historique":
    st.header("Historique des predictions")
    
    if 'history' in st.session_state and len(st.session_state.history) > 0:
        df_history = pd.DataFrame(st.session_state.history)
        st.subheader("Predictions recentes")
        st.dataframe(df_history, use_container_width=True)
        
        st.subheader("Evolution des predictions")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_history['timestamp'], y=df_history['prediction'],
                                 mode='lines+markers', name='NO2 Predit'))
        fig.update_layout(title="NO2 au fil du temps", height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Nombre", len(df_history))
        with col2:
            st.metric("Moyenne", f"{df_history['prediction'].mean():.2f}")
        with col3:
            st.metric("Max", f"{df_history['prediction'].max():.2f}")
        with col4:
            st.metric("Min", f"{df_history['prediction'].min():.2f}")
    else:
        st.info("Aucune prediction. Allez a la page Prediction pour commencer!")

st.markdown("---")
st.markdown("Application Streamlit - Systeme de prediction de qualite de l'air")
