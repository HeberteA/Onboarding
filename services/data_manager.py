import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

@st.cache_resource(ttl=600) 
def get_db_connection():
    try:
        db_url = st.secrets["database"]["url"]
        engine = create_engine(db_url, pool_pre_ping=True)
        return engine
    except Exception as e:
        st.error(f"Erro crítico ao conectar no banco: {e}")
        return None

class DataManager:
    
    def __init__(self):
        self.engine = get_db_connection()
        self.project_map = {}
        self.task_map = {}
        
        self.LISTAS_VALIDACAO = {
            "ETAPA": ["PRÉ-OBRA", "EXECUÇÃO", "PÓS-OBRA"],
            "STATUS_PROJETO": ["NÃO INICIADO", "ANDAMENTO", "PENDENTE", "ENTRADA", "SIM", "NÃO SE APLICA"],
            "SETOR": ["ADMINISTRATIVO", "ENGENHARIA", "DIRETORIA"], 
            "RESPONSÁVEL": ["DIRETORIA"] 
        }
        self._load_aux_lists()

    def _load_aux_lists(self):
        """Carrega Setores e Responsáveis direto do Postgres para os Dropdowns"""
        if not self.engine: return
        try:
            with self.engine.connect() as conn:
                df_sec = pd.read_sql("SELECT name FROM sectors ORDER BY name", conn)
                if not df_sec.empty:
                    self.LISTAS_VALIDACAO["SETOR"] = df_sec["name"].tolist()
                
                df_resp = pd.read_sql("SELECT name FROM responsibles ORDER BY name", conn)
                if not df_resp.empty:
                    self.LISTAS_VALIDACAO["RESPONSÁVEL"] = df_resp["name"].tolist()
        except Exception as e:
            print(f"Aviso: Não foi possível carregar listas auxiliares: {e}")

    def get_data(self, category_filter=None):
        if not self.engine: return pd.DataFrame()

        try:
            with self.engine.connect() as conn:
                query_tasks = "SELECT id, item_number, title, description, stage FROM tasks ORDER BY item_number"
                df_tasks = pd.read_sql(query_tasks, conn)
                
                if df_tasks.empty: return pd.DataFrame()

                df_tasks["ATIVIDADE"] = df_tasks["item_number"].astype(str) + " - " + df_tasks["title"]
                self.task_map = dict(zip(df_tasks["ATIVIDADE"], df_tasks["id"]))

                params_proj = {}
                query_proj = "SELECT id, name FROM projects"
                
                if category_filter and category_filter != "GERAL":
                    query_proj += " WHERE category = :cat"
                    params_proj = {"cat": category_filter}
                
                df_projects = pd.read_sql(text(query_proj), conn, params=params_proj)
                
                if df_projects.empty:
                    return df_tasks[["item_number", "ATIVIDADE", "description", "stage"]].rename(
                        columns={"description": "DESCRIÇÃO", "stage": "ETAPA", "item_number": "ITEM"}
                    )

                self.project_map = dict(zip(df_projects["name"], df_projects["id"]))
                project_ids = tuple(df_projects["id"].tolist())

                if len(project_ids) == 1:
                    ids_sql = f"({project_ids[0]})"
                else:
                    ids_sql = str(project_ids)

                query_status = f"SELECT task_id, project_id, status FROM project_tasks WHERE project_id IN {ids_sql}"
                df_status = pd.read_sql(query_status, conn)

                df_final = df_tasks[["id", "item_number", "ATIVIDADE", "description", "stage"]].copy()
                df_final.rename(columns={"description": "DESCRIÇÃO", "stage": "ETAPA", "item_number": "ITEM"}, inplace=True)

                if not df_status.empty:
                    df_status = df_status.merge(df_projects, left_on="project_id", right_on="id")
                    pivot = df_status.pivot(index="task_id", columns="name", values="status")
                    df_final = df_final.merge(pivot, left_on="id", right_index=True, how="left")

                for col in df_projects["name"]:
                    if col not in df_final.columns:
                        df_final[col] = "NÃO INICIADO"
                    else:
                        df_final[col] = df_final[col].fillna("NÃO INICIADO")

                return df_final.drop(columns=["id"], errors="ignore")

        except Exception as e:
            st.error(f"Erro ao buscar dados: {e}")
            return pd.DataFrame()

    def save_data(self, df_edited, category_filter=None):
        if not self.engine: return False, "Sem conexão DB"

        try:
            cols_meta = ["ITEM", "ATIVIDADE", "DESCRIÇÃO", "ETAPA", "SETOR", "RESPONSÁVEL"]
            cols_projetos = [c for c in df_edited.columns if c not in cols_meta]
            
            upsert_values = []
            
            for _, row in df_edited.iterrows():
                task_id = self.task_map.get(row["ATIVIDADE"])
                if not task_id: continue

                for proj_name in cols_projetos:
                    proj_id = self.project_map.get(proj_name)
                    status_val = row[proj_name]
                    
                    if proj_id and status_val:
                        upsert_values.append({
                            "p_id": int(proj_id),
                            "t_id": int(task_id),
                            "st": status_val
                        })
            
            if not upsert_values:
                return True, "Nenhuma alteração detectada."

            sql_upsert = text("""
                INSERT INTO project_tasks (project_id, task_id, status, updated_at)
                VALUES (:p_id, :t_id, :st, NOW())
                ON CONFLICT (project_id, task_id) 
                DO UPDATE SET 
                    status = EXCLUDED.status,
                    updated_at = NOW();
            """)

            with self.engine.begin() as conn:
                conn.execute(sql_upsert, upsert_values)
                
            return True, "✅ Dados salvos no Postgres com sucesso!"

        except Exception as e:
            return False, f"Erro grave ao salvar SQL: {str(e)}"

data_manager = DataManager()