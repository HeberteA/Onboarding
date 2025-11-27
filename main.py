import streamlit as st
from streamlit_option_menu import option_menu
from utils.styles import apply_custom_styles, card_component
from services.data_manager import data_manager
from views import dashboard, editor, reports

# Setup Inicial
st.set_page_config(page_title="Command Center", page_icon="🏢", layout="wide")
apply_custom_styles()

def main():
    # --- SIDEBAR (App-Like Navigation) ---
    with st.sidebar:
        # LOGO AREA - Atualizado para Laranja
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; padding-bottom: 20px;">
            <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #E37026 0%, #ca5a15 100%); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; box-shadow: 0 4px 10px rgba(227, 112, 38, 0.3);">CC</div>
            <div>
                <div style="font-weight: 700; color: white; font-size: 16px;">Command Center</div>
                <div style="font-size: 11px; color: rgba(255,255,255,0.5);">PostgreSQL Edition</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # MENU - Atualizado para Laranja (#E37026)
        selected = option_menu(
            menu_title=None,
            options=["Visão Geral", "Lançamentos", "Relatórios"],
            icons=["grid-fill", "pencil-square", "file-earmark-bar-graph"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background": "transparent"},
                "icon": {"color": "#E37026", "font-size": "14px"}, 
                "nav-link": {
                    "font-size": "14px", 
                    "text-align": "left", 
                    "margin": "0px 0px 5px 0px", 
                    "padding": "10px 15px",
                    "border-radius": "8px",
                    "color": "rgba(255,255,255,0.7)"
                },
                "nav-link-selected": {
                    "background-color": "rgba(255,255,255,0.1)", 
                    "color": "white", 
                    "font-weight": "600", 
                    "border-left": "3px solid #E37026"
                },
            }
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:11px; font-weight:600; color:rgba(255,255,255,0.4); margin-bottom:10px; padding-left:10px; letter-spacing:1px;'>FILTROS</div>", unsafe_allow_html=True)
        
        cat = st.selectbox(
            "Categoria", 
            ["GERAL", "MULTIFAMILIAR", "COMERCIAL", "USO MISTO", "UNIFAMILIAR"],
            label_visibility="collapsed"
        )
        
        # Footer
        st.markdown("<div style='flex-grow:1'></div>", unsafe_allow_html=True)
        # Check engine instead of supabase client
        status_color = "#10b981" if data_manager.engine else "#ef4444"
        status_txt = "POSTGRES ONLINE" if data_manager.engine else "DB ERROR"
        
        st.markdown(f"""
        <div style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); margin-top: 50px;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <span style="font-size: 11px; color: rgba(255,255,255,0.5);">Status do Banco</span>
                <span style="font-size: 10px; font-weight: bold; color: {status_color}; background: {status_color}20; padding: 2px 6px; border-radius: 4px;">{status_txt}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- MAIN CONTENT ---
    # Título com detalhe Laranja
    st.markdown(f"""
    <div style="margin-bottom: 25px;">
        <h1 style="font-size: 28px; font-weight: 700; color: white; margin: 0;">{selected}</h1>
        <p style="color: rgba(255,255,255,0.5); font-size: 14px; margin-top: 5px;">Visualizando dados de obras: <span style="color:#E37026; font-weight:600">{cat}</span></p>
    </div>
    """, unsafe_allow_html=True)

    filtro = None if cat == "GERAL" else cat
    df = data_manager.get_data(filtro)

    if selected == "Visão Geral":
        dashboard.render_view(df, cat)
    elif selected == "Lançamentos":
        editor.render_view(df, cat)
    elif selected == "Relatórios":
        reports.render_view(df, cat)

if __name__ == "__main__":
    main()