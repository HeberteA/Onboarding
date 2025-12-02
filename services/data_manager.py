import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

class DataManager:
    def __init__(self):
        self._db_url = st.secrets["database"]["url"]
        self._engine = None
        self._init_connection()

    def _init_connection(self):
        try:
            self._engine = create_engine(self._db_url, pool_pre_ping=True)
        except Exception as e:
            st.error(f"Erro de conexão: {e}")

    def get_projects(self):
        if not self._engine: return pd.DataFrame()
        with self._engine.connect() as conn:
            return pd.read_sql("SELECT id, name FROM projects ORDER BY name", conn)

    def get_project_data(self, project_id):
        if not self._engine: return pd.DataFrame()
        query = text("""
            SELECT t.id as task_id, t.item_number, t.title, t.description, t.area,
                   s.name as sector, r.name as responsible, COALESCE(pt.status, 'NÃO INICIADO') as status
            FROM tasks t
            LEFT JOIN sectors s ON t.sector_id = s.id
            LEFT JOIN responsibles r ON t.default_responsible_id = r.id
            LEFT JOIN project_tasks pt ON t.id = pt.task_id AND pt.project_id = :pid
            ORDER BY NULLIF(regexp_replace(t.item_number, '[^0-9.]', '', 'g'), '')::numeric
        """)
        with self._engine.connect() as conn:
            return pd.read_sql(query, conn, params={"pid": project_id})

    def get_kpis(self, project_id):
        if not self._engine: return 0, 0, 0
        query = text("""
            SELECT COUNT(*) FILTER (WHERE status = 'SIM'),
                   COUNT(*) FILTER (WHERE status IN ('PENDENTE', 'ENTRADA')),
                   COUNT(*) 
            FROM project_tasks WHERE project_id = :pid
        """)
        with self._engine.connect() as conn:
            res = conn.execute(query, {"pid": project_id}).fetchone()
            return (res[0], res[1], res[2]) if res and res[2] > 0 else (0, 0, 0)

    def update_single_status(self, project_id, task_id, status):
        stmt = text("""
            INSERT INTO project_tasks (project_id, task_id, status, updated_at)
            VALUES (:pid, :tid, :st, NOW())
            ON CONFLICT (project_id, task_id) DO UPDATE SET status = EXCLUDED.status, updated_at = NOW()
        """)
        with self._engine.begin() as conn:
            conn.execute(stmt, {"pid": project_id, "tid": task_id, "st": status})

    
    def get_all_tasks_raw(self):
        """Busca todas as tarefas com os nomes de setor e responsável para edição"""
        query = text("""
            SELECT t.id, t.item_number, t.title, t.description, t.area, t.stage,
                   s.name as sector_name, r.name as resp_name
            FROM tasks t
            LEFT JOIN sectors s ON t.sector_id = s.id
            LEFT JOIN responsibles r ON t.default_responsible_id = r.id
            ORDER BY NULLIF(regexp_replace(t.item_number, '[^0-9.]', '', 'g'), '')::numeric
        """)
        with self._engine.connect() as conn:
            return pd.read_sql(query, conn)

    def get_aux_list(self, table_name):
        """Busca lista de setores ou responsáveis"""
        if table_name not in ['sectors', 'responsibles']: return pd.DataFrame()
        with self._engine.connect() as conn:
            return pd.read_sql(f"SELECT id, name FROM {table_name} ORDER BY name", conn)

    def update_aux_list(self, table_name, df_changes):
        """Atualiza listas auxiliares (Adiciona/Remove/Edita)"""
        if table_name not in ['sectors', 'responsibles']: return
        
        with self._engine.begin() as conn:
            for index, row in df_changes.iterrows():
                if pd.notna(row.get('id')):
                    conn.execute(text(f"UPDATE {table_name} SET name=:n WHERE id=:id"), {"n": row['name'].strip().upper(), "id": row['id']})
                else:
                    if row['name']:
                        conn.execute(text(f"INSERT INTO {table_name} (name) VALUES (:n)"), {"n": row['name'].strip().upper()})
            


    def save_bulk_tasks(self, df_edited):
        """Salva edições em massa nas tarefas"""
        with self._engine.begin() as conn:
            sec_map = {name: id for id, name in conn.execute(text("SELECT id, name FROM sectors")).fetchall()}
            resp_map = {name: id for id, name in conn.execute(text("SELECT id, name FROM responsibles")).fetchall()}
            
            for index, row in df_edited.iterrows():
                sid = sec_map.get(row['sector_name'])
                rid = resp_map.get(row['resp_name'])
                
                
                stmt = text("""
                    UPDATE tasks 
                    SET description = :desc, area = :area, stage = :stg, 
                        sector_id = :sid, default_responsible_id = :rid
                    WHERE id = :tid
                """)
                conn.execute(stmt, {
                    "desc": row['description'],
                    "area": row['area'],
                    "stg": row['stage'],
                    "sid": sid,
                    "rid": rid,
                    "tid": row['id']
                })
        return True