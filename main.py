import streamlit as st
from streamlit_option_menu import option_menu
from services.data_manager import DataManager
import os
import base64

from views.dashboard import render_dashboard
from views.management import render_management
from views.settings import render_settings
from views.projects import render_projects

def get_base64_image(image_path):
    if not os.path.exists(image_path):
        return None
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

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

    /* Login Style */
    .login-container {
        background-color: transparent; 
        background-image: linear-gradient(160deg, #1e1e1f 0%, #0a0a0c 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 50px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    div.stButton > button {
        background-color: #E37026 !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
    }
    
    .minha-imagem {
        width: 160px; 
        margin-bottom: 20px; 
        display: block; 
        margin-left: auto; 
        margin-right: auto;
    }
</style>
""", unsafe_allow_html=True)

def login_screen():
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
        
        logo_file = "Lavie.png" if os.path.exists("Lavie.png") else "Lavie.jpg"
        img_b64 = get_base64_image(logo_file)
        
        if img_b64:
            mime_type = "image/png" if logo_file.endswith(".png") else "image/jpeg"
            header_html = f'<img src="data:{mime_type};base64,{img_b64}" style="width: 300px; height: auto; display: block; margin: 0 auto 20px auto;">'
        else:
            header_html = "<h2 style='color:#E37026; margin-bottom: 10px;'>LAVIE</h2>"

        st.markdown(f"""
        <div class="login-container">
            {header_html}
            <h2 style='color:#E37026; margin-bottom: 0px;'>ONBOARDING</h2>
            <p style='color:#E37026; font-size: 0.8rem; letter-spacing: 2px;'>Gestão de Obras</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_simple"):
            password = st.text_input("Senha de Acesso", type="password", placeholder="••••••")
            
            if st.form_submit_button("Entrar", use_container_width=True):
                if "passwords" in st.secrets:
                    found_user = None
                    for user, secret_pass in st.secrets["passwords"].items():
                        if secret_pass == password:
                            found_user = user
                            break
                    
                    if found_user:
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = found_user.capitalize()
                        st.toast(f"Bem-vindo, {found_user.capitalize()}!", icon="🔓")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Senha incorreta.")
                else:
                    st.error("Erro: Arquivo de senhas não configurado.")
                    
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
            options=["Gestão", "Obras", "Configurações", "Dashboard"],
            icons=["grid", "building", "gear", "kanban"], 
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

    elif menu == "Obras": 
        render_projects(dm)
    
    elif menu == "Configurações":
        render_settings(dm)

if __name__ == "__main__":
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        login_screen()
    else:
        main_app()
