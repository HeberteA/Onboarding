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
            st.error(f"Erro: {e}")

    def get_projects(self):
        if not self._engine: return pd.DataFrame()
        with self._engine.connect() as conn:
            return pd.read_sql("SELECT id, name FROM projects ORDER BY name", conn)

    def get_project_data_hierarchical(self, project_id):
        if not self._engine: return pd.DataFrame()
        query = text("""
            SELECT 
                p.title as phase_title,
                p.number as phase_number,
                t.id as task_id,
                t.item_number,
                t.title as task_title,
                t.description,
                t.area,  -- Campo Area recuperado corretamente
                t.stage,
                s.name as sector,
                r.name as responsible,
                COALESCE(pt.status, 'NÃO INICIADO') as status
            FROM tasks t
            JOIN phases p ON t.phase_id = p.id
            LEFT JOIN sectors s ON t.sector_id = s.id
            LEFT JOIN responsibles r ON t.default_responsible_id = r.id
            LEFT JOIN project_tasks pt ON t.id = pt.task_id AND pt.project_id = :pid
            ORDER BY p.number, NULLIF(regexp_replace(t.item_number, '[^0-9.]', '', 'g'), '')::numeric
        """)
        with self._engine.connect() as conn:
            return pd.read_sql(query, conn, params={"pid": project_id})

    def get_global_dashboard_data(self):
        """Dados globais atualizados com Fases"""
        if not self._engine: return pd.DataFrame()
        query = text("""
            SELECT 
                pr.name as project_name,
                ph.title as phase_title,
                t.item_number,
                t.stage,
                s.name as sector,
                COALESCE(pt.status, 'NÃO INICIADO') as status
            FROM tasks t
            CROSS JOIN projects pr
            JOIN phases ph ON t.phase_id = ph.id
            LEFT JOIN project_tasks pt ON t.id = pt.task_id AND pt.project_id = pr.id
            LEFT JOIN sectors s ON t.sector_id = s.id
        """)
        with self._engine.connect() as conn:
            return pd.read_sql(query, conn)

    def update_single_status(self, project_id, task_id, status):
        stmt = text("""
            INSERT INTO project_tasks (project_id, task_id, status, updated_at)
            VALUES (:pid, :tid, :st, NOW())
            ON CONFLICT (project_id, task_id) DO UPDATE SET status = EXCLUDED.status, updated_at = NOW()
        """)
        with self._engine.begin() as conn:
            conn.execute(stmt, {"pid": project_id, "tid": task_id, "st": status})
