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
            SELECT 
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
            LEFT JOIN sectors s ON t.sector_id = s.id
            LEFT JOIN responsibles r ON t.default_responsible_id = r.id
            LEFT JOIN project_tasks pt ON t.id = pt.task_id AND pt.project_id = :pid
            ORDER BY NULLIF(regexp_replace(t.item_number, '[^0-9.]', '', 'g'), '')::numeric
        """)
        with self._engine.connect() as conn:
            return pd.read_sql(query, conn, params={"pid": project_id})

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
    
