import pandas as pd
import toml
from sqlalchemy import create_engine, text

def main():
    try:
        secrets = toml.load(".streamlit/secrets.toml")
        engine = create_engine(secrets["database"]["url"])
        print("✅ Conectado ao banco.")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return

    # Limpar tabelas antigas para evitar sujeira
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE project_tasks, tasks, projects, responsibles, sectors CASCADE;"))
        # Garantir que a coluna 'area' existe (para a Atividade1)
        conn.execute(text("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS area TEXT;"))
    
    file_path = "ONBOARDING - ONBOARDING.csv"

    # Ler o CSV encontrando o cabeçalho correto
    try:
        df_raw = pd.read_csv(file_path, header=None, nrows=15)
        header_idx = None
        for i, row in df_raw.iterrows():
            if "ITENS" in row.astype(str).str.upper().values:
                header_idx = i
                break
        
        df = pd.read_csv(file_path, header=header_idx)
        
        # Limpar nomes das colunas (remove espaços extras)
        df.columns = df.columns.str.strip()
        
        # Tratar colunas duplicadas (A segunda 'ATIVIDADE' vira 'ATIVIDADE.1')
        cols = pd.Series(df.columns)
        for dup in cols[cols.duplicated()].unique(): 
            cols[cols[cols == dup].index.values.tolist()] = [dup + '.' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]
        df.columns = cols
        
        # Filtrar linhas válidas
        df = df[df["ITENS"].notna()]
        df = df[df["ITENS"].astype(str).str.strip() != "ITENS"]

    except Exception as e:
        print(f"Erro ao ler CSV: {e}")
        return

    # --- DEFINIÇÃO CRÍTICA DO QUE É PROJETO E O QUE NÃO É ---
    # Adicionei ETAPA e ATIVIDADE.1 aqui para garantir que NÃO virem obras
    cols_ignorar = [
        'ITENS', 'ATIVIDADE', 'DESCRIÇÃO', 'SETOR', 
        'ATIVIDADE1', 'RESPONSÁVEL', 'ETAPA', 'OBSERVAÇÕES'
    ]
    # Projetos são apenas as colunas que SOBRAM (ex: MANÁ I, LAVIE BEACH...)
    projetos_cols = [c for c in df.columns if c not in cols_ignorar and "Unnamed" not in c]

    print(f"🚫 Colunas ignoradas (Dados): {cols_ignorar}")
    print(f"🏗️ Obras identificadas: {projetos_cols}")

    with engine.begin() as conn:
        # Mapas auxiliares
        map_setores = {}
        map_resp = {}
        map_projetos = {}

        # 1. Inserir Obras
        for p in projetos_cols:
            conn.execute(text("INSERT INTO projects (name) VALUES (:n) ON CONFLICT (name) DO NOTHING"), {"n": p.strip()})
            pid = conn.execute(text("SELECT id FROM projects WHERE name=:n"), {"n": p.strip()}).scalar()
            map_projetos[p] = pid

        # 2. Inserir Setores e Responsáveis
        if "SETOR" in df.columns:
            for s in df["SETOR"].dropna().unique():
                val = str(s).strip().upper()
                conn.execute(text("INSERT INTO sectors (name) VALUES (:n) ON CONFLICT (name) DO NOTHING"), {"n": val})
                map_setores[val] = conn.execute(text("SELECT id FROM sectors WHERE name=:n"), {"n": val}).scalar()
        
        if "RESPONSÁVEL" in df.columns:
            for r in df["RESPONSÁVEL"].dropna().unique():
                val = str(r).strip().upper()
                conn.execute(text("INSERT INTO responsibles (name) VALUES (:n) ON CONFLICT (name) DO NOTHING"), {"n": val})
                map_resp[val] = conn.execute(text("SELECT id FROM responsibles WHERE name=:n"), {"n": val}).scalar()

        # 3. Inserir Tarefas e Status
        count = 0
        for _, row in df.iterrows():
            try:
                item = str(row.get("ITENS", "")).strip()
                titulo = str(row.get("ATIVIDADE", "")).strip()
                
                # AQUI: A coluna ATIVIDADE.1 (Atividade1) vai para o campo 'area'
                area_val = str(row.get("ATIVIDADE1", "")).strip()
                if area_val.lower() == 'nan': area_val = None

                # AQUI: Se tiver coluna ETAPA no CSV, mapear aqui. Se não, usa None.
                etapa_val = str(row.get("ETAPA", "")).strip()
                if etapa_val.lower() in ['nan', '']: etapa_val = None

                desc = str(row.get("DESCRIÇÃO", "")).strip()
                if desc.lower() == 'nan': desc = None

                sid = map_setores.get(str(row.get("SETOR", "")).strip().upper())
                rid = map_resp.get(str(row.get("RESPONSÁVEL", "")).strip().upper())

                # Insere Task
                res = conn.execute(text("""
                    INSERT INTO tasks (item_number, title, description, area, stage, sector_id, default_responsible_id)
                    VALUES (:item, :t, :d, :a, :stg, :sid, :rid)
                    RETURNING id
                """), {
                    "item": item, "t": titulo, "d": desc, 
                    "a": area_val, "stg": etapa_val, # Salva Atividade1 e Etapa corretamente
                    "sid": sid, "rid": rid
                }).fetchone()
                
                task_id = res[0]
                count += 1

                # Insere Status para cada Obra Real
                for p_col in projetos_cols:
                    status_raw = str(row.get(p_col, "NÃO INICIADO")).strip().upper()
                    if status_raw in ["NAN", "", "NONE"]: status_raw = "NÃO INICIADO"
                    
                    pid = map_projetos.get(p_col)
                    if pid:
                        conn.execute(text("""
                            INSERT INTO project_tasks (project_id, task_id, status)
                            VALUES (:pid, :tid, :st)
                        """), {"pid": pid, "tid": task_id, "st": status_raw})
            except Exception as e:
                print(f"Erro linha {item}: {e}")

    print(f"✅ Banco corrigido! {count} tarefas importadas. 'Atividade1' e 'Etapa' agora são dados, não obras.")

if __name__ == "__main__":
    main()