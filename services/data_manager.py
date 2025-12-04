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
        """Busca dados para a tela de Gestão (Incluindo Nome da Fase)"""
        if not self._engine: return pd.DataFrame()
        query = text("""
            SELECT 
                p.title as phase_title, -- Nome real da fase (Ex: CONTRATOS)
                t.id as task_id, 
                t.item_number, 
                t.title, 
                t.description, 
                t.area, 
                t.stage,
                s.name as sector, 
                r.name as responsible, 
                COALESCE(pt.status, 'NÃO INICIADO') as status
            FROM tasks t
            JOIN phases p ON t.phase_id = p.id
            LEFT JOIN sectors s ON t.sector_id = s.id
            LEFT JOIN responsibles r ON t.default_responsible_id = r.id
            LEFT JOIN project_tasks pt ON t.id = pt.task_id AND pt.project_id = :pid
            ORDER BY NULLIF(regexp_replace(t.item_number, '[^0-9.]', '', 'g'), '')::numeric
        """)
        with self._engine.connect() as conn:
            return pd.read_sql(query, conn, params={"pid": project_id})

    def get_global_dashboard_data(self):
        """Busca dados para o Dashboard Global"""
        if not self._engine: return pd.DataFrame()
        query = text("""
            SELECT 
                pr.name as project_name,
                ph.title as phase_title,
                t.item_number,
                t.stage,
                s.name as sector,
                r.name as responsible,
                COALESCE(pt.status, 'NÃO INICIADO') as status
            FROM tasks t
            CROSS JOIN projects pr
            JOIN phases ph ON t.phase_id = ph.id
            LEFT JOIN project_tasks pt ON t.id = pt.task_id AND pt.project_id = pr.id
            LEFT JOIN sectors s ON t.sector_id = s.id
            LEFT JOIN responsibles r ON t.default_responsible_id = r.id
        """)
        with self._engine.connect() as conn:
            return pd.read_sql(query, conn)

    def get_all_tasks_admin(self):
        if not self._engine: return pd.DataFrame()
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

    def get_aux_list(self, table):
        if not self._engine or table not in ['sectors', 'responsibles']: return pd.DataFrame()
        with self._engine.connect() as conn:
            return pd.read_sql(f"SELECT id, name FROM {table} ORDER BY name", conn)

    def update_single_status(self, project_id, task_id, status):
        stmt = text("""
            INSERT INTO project_tasks (project_id, task_id, status, updated_at)
            VALUES (:pid, :tid, :st, NOW())
            ON CONFLICT (project_id, task_id) DO UPDATE SET status = EXCLUDED.status, updated_at = NOW()
        """)
        try:
            with self._engine.begin() as conn:
                conn.execute(stmt, {"pid": project_id, "tid": task_id, "st": status})
            return True
        except: return False

    def save_task_changes(self, df_edited):
        if not self._engine: return
        with self._engine.begin() as conn:
            sec_map = {name: id for id, name in conn.execute(text("SELECT id, name FROM sectors")).fetchall()}
            resp_map = {name: id for id, name in conn.execute(text("SELECT id, name FROM responsibles")).fetchall()}
            for index, row in df_edited.iterrows():
                sid = sec_map.get(row['sector_name'])
                rid = resp_map.get(row['resp_name'])
                conn.execute(text("""
                    UPDATE tasks SET description=:d, area=:a, stage=:stg, sector_id=:sid, default_responsible_id=:rid
                    WHERE id=:id
                """), {"d": row['description'], "a": row['area'], "stg": row['stage'], "sid": sid, "rid": rid, "id": row['id']})

    def update_aux_list(self, table, df_changes):
        if not self._engine or table not in ['sectors', 'responsibles']: return
        with self._engine.begin() as conn:
            for index, row in df_changes.iterrows():
                name = str(row['name']).strip().upper()
                if not name: continue
                if pd.notna(row.get('id')):
                    conn.execute(text(f"UPDATE {table} SET name=:n WHERE id=:id"), {"n": name, "id": int(row['id'])})
                else:
                    exists = conn.execute(text(f"SELECT 1 FROM {table} WHERE name=:n"), {"n": name}).scalar()
                    if not exists:
                        conn.execute(text(f"INSERT INTO {table} (name) VALUES (:n)"), {"n": name})
