import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>
    

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #ffffff;
        }

        /* --- 0. FUNDO COM GRADIENTE (Identidade Visual) --- */
        .stApp {
            /* Gradiente sutil Dark + Toque do Laranja no topo */
            background: linear-gradient(180deg, rgba(227, 112, 38, 0.15) 0%, rgba(0, 0, 0, 0) 30%), 
                        linear-gradient(135deg, #111111 0%, #000000 100%);
            background-attachment: fixed;
        }

        /* --- 1. LIMPEZA VISUAL --- */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 1rem !important;
            max-width: 95% !important;
        }

        /* --- 2. SIDEBAR DARK --- */
        [data-testid="stSidebar"] {
            background-color: #000000;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* --- 3. CARDS FLUTUANTES --- */
        .metric-card {
            background: rgba(255, 255, 255, 0.03); /* Efeito Glass fraco */
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 24px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            border-color: #E37026; /* LARANJA PRIMARY */
            box-shadow: 0 4px 20px rgba(227, 112, 38, 0.2); /* Glow Laranja */
            transform: translateY(-2px);
        }
        
        .metric-label {
            color: rgba(255, 255, 255, 0.6);
            font-size: 0.875rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .metric-value {
            color: #ffffff;
            font-size: 2.25rem;
            font-weight: 700;
            margin-top: 8px;
            line-height: 1;
        }

        .metric-delta {
            display: inline-flex;
            align-items: center;
            padding: 2px 8px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-top: 12px;
        }
        /* Cores de Status mantidas funcionais, mas adaptadas ao Dark Mode */
        .delta-positive { background-color: rgba(16, 185, 129, 0.2); color: #34d399; }
        .delta-negative { background-color: rgba(239, 68, 68, 0.2); color: #f87171; }
        .delta-neutral { background-color: rgba(59, 130, 246, 0.2); color: #60a5fa; }

        /* Inputs Modernos com Borda Laranja no Focus */
        .stSelectbox > div > div {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: white !important;
            border-radius: 8px !important;
        }
        .stSelectbox > div > div:focus-within {
             border-color: #E37026 !important;
        }
        
        /* Tabs Customizadas */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 6px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            border-radius: 8px;
            border: none !important;
            color: rgba(255, 255, 255, 0.6);
        }
        .stTabs [aria-selected="true"] {
            background-color: #E37026 !important; /* LARANJA */
            color: white !important;
            font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)

def card_component(label, value, delta=None, delta_color="neutral"):
    delta_html = ""
    if delta:
        delta_class = f"delta-{delta_color}"
        delta_html = f'<div class="metric-delta {delta_class}">{delta}</div>'
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """