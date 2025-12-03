import streamlit as st
from streamlit_option_menu import option_menu
from services.data_manager import DataManager
import os

from views.dashboard import render_dashboard
from views.management import render_management
from views.settings import render_settings

st.set_page_config(page_title="Lavie Onboarding", layout="wide", initial_sidebar_state="expanded", page_icon="Lavie1.png")

st.markdown("""
<style>
    /* 1. SEU ESTILO PADRÃO (BACKGROUND E INPUTS) */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 10% 20%, #3b3b3b 0%, #000000 100%);
        font-family: 'Inter', sans-serif;
        color: #ffffff;
    }

     /* Logo Area */
    .sidebar-logo-container {
        text-align: center;
        padding: 20px 0;
        margin-bottom: 20px;
    }
    .sidebar-logo-text {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.5rem;
        color: white;
        letter-spacing: 2px;
    }
    .sidebar-logo-sub {
        font-size: 0.7rem;
        color: var(--primary);
        text-transform: uppercase;
        letter-spacing: 3px;
    }
            
    /* Ajustes de Inputs para contraste (Seu código) */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }
    div[data-testid="stNumberInput"] input, div[data-testid="stTextInput"] input {
        color: white !important;
    }

    /* 2. CUSTOMIZAÇÃO DA SIDEBAR PARA HARMONIZAR */
    section[data-testid="stSidebar"] {
        background-color: #000000; /* Preto absoluto para contraste com o radial */
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Headers */
    h1, h2, h3 { color: #ffffff !important; font-weight: 600; letter-spacing: -0.5px; }
    
    /* Remove padding excessivo do topo */
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

def main():
    dm = DataManager()

    with st.sidebar:
        st.image("Lavie.png")
        st.markdown("""
            <div class="sidebar-logo-container">
                <div class="sidebar-logo-text">ONBOARDING</div>
                <div class="sidebar-logo-sub">Gestão de Obras</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        menu = option_menu(
            menu_title=None,
            options=["Gestão",  "Configurações", "Dashboard"],
            icons=["grid", "gear", "kanban"], 
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background": "transparent"},
                "nav-link": {"color": "#aaa", "font-size": "0.9rem", "margin":"6px", "text-align": "left"},
                "nav-link-selected": {
                    "background-color": "rgba(227, 112, 38, 0.15)", 
                    "color": "#E37026", 
                    "border-left": "3px solid #E37026"
                },
                "icon": {"font-size": "1.1rem"}
            }
        )


        selected_pid = None
        
        if menu == "Gestão":
            st.markdown("---")
            projects = dm.get_projects()
            if not projects.empty:
                proj_dict = dict(zip(projects['id'], projects['name']))
                
                if 'selected_project_id' not in st.session_state:
                    st.session_state['selected_project_id'] = projects['id'].iloc[0]
                
                st.caption("OBRA ATIVA")
                selected_pid = st.selectbox(
                    "Selecione a Obra",
                    options=list(proj_dict.keys()),
                    format_func=lambda x: proj_dict[x],
                    index=list(proj_dict.keys()).index(st.session_state['selected_project_id']),
                    label_visibility="collapsed"
                )
                st.session_state['selected_project_id'] = selected_pid
                
            else:
                st.warning("Sem obras cadastradas.")
        
        st.markdown("---")
        
        st.markdown("""
            <div style="position: fixed; bottom: 20px; width: 100%; text-align: center; color: #475569; font-size: 0.7rem;">
                Onboarding • Lavie System
            </div>
        """, unsafe_allow_html=True)

    if menu == "Dashboard":
        render_dashboard(dm)
    
    elif menu == "Gestão":
        if selected_pid:
            project_name = proj_dict[selected_pid]
            render_management(dm, selected_pid, project_name)
    
    elif menu == "Configurações":
        render_settings(dm)

if __name__ == "__main__":
    main()
