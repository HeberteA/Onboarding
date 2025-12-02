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
    /* Variáveis */
    :root { --primary: #8B5CF6; --bg-dark: #0F172A; }
    
    /* Global App */
    .stApp { 
        background: radial-gradient(circle at 10% 20%, #3b3b3b 0%, #000000 100%);
        font-family: 'Inter', sans-serif;
        color: #ffffff;
    }
    .block-container { padding-top: 1.5rem; }

    /* SIDEBAR STYLING - REMOVENDO O PADRÃO */
    section[data-testid="stSidebar"] {
        background-color: #020617; /* Slate-950 (Mais escuro que o fundo) */
        border-right: 1px solid rgba(255,255,255,0.05);
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

    /* Option Menu Customization */
    .nav-link {
        border-radius: 8px !important;
        margin-bottom: 5px !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
    }
    .nav-link:hover {
        background: radial-gradient(circle at 10% 20%, #3b3b3b 0%, #000000 100%);
        font-family: 'Inter', sans-serif;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

def main():
    dm = DataManager()

    with st.sidebar:
        if os.path.exists("logo.png"):
            st.image("Lavie.png", width=120)
        else:
            st.markdown("""
                <div class="sidebar-logo-container">
                    <div class="sidebar-logo-text">LAVIE</div>
                    <div class="sidebar-logo-sub">CONSTRUÇÕES</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        projects = dm.get_projects()
        if projects.empty:
            st.error("Sem projetos. Rode o script de importação.")
            return

        proj_dict = dict(zip(projects['id'], projects['name']))
        
        if 'selected_project_id' not in st.session_state:
            st.session_state['selected_project_id'] = projects['id'].iloc[0]
        
        if st.session_state['selected_project_id'] not in proj_dict:
            st.session_state['selected_project_id'] = projects['id'].iloc[0]

        st.caption("OBRA ATIVA")
        pid = st.selectbox(
            "Selecione a Obra",
            options=list(proj_dict.keys()),
            format_func=lambda x: proj_dict[x],
            index=list(proj_dict.keys()).index(st.session_state['selected_project_id']),
            label_visibility="collapsed"
        )
        st.session_state['selected_project_id'] = pid
        
        st.markdown("---")
        
        menu = option_menu(
            menu_title=None,
            options=["Dashboard", "Gestão", "Configurações"],
            icons=["grid-fill", "kanban", "gear-fill"], 
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#94a3b8", "font-size": "18px"}, 
                "nav-link": {"color": "#cbd5e1", "text-align": "left", "margin":"5px"},
                "nav-link-selected": {"background-color": "var(--primary)", "color": "white", "box-shadow": "0 4px 6px -1px rgba(0,0,0,0.1)"},
            }
        )
        
        st.markdown("""
            <div style="position: fixed; bottom: 20px; width: 100%; text-align: center; color: #475569; font-size: 0.7rem;">
                Onboarding • Lavie System
            </div>
        """, unsafe_allow_html=True)

    project_name = proj_dict[pid]

    if menu == "Dashboard":
        render_dashboard(dm, pid, project_name)
    elif menu == "Gestão":
        render_management(dm, pid, project_name)
    elif menu == "Configurações":
        render_settings(dm)

if __name__ == "__main__":
    main()