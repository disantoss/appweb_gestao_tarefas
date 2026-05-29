import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
import time
from datetime import datetime, date
import uuid
from fpdf import FPDF

# ==========================================
# CONFIGURAÇÃO DA PÁGINA & TEMA
# ==========================================
st.set_page_config(page_title="Task Manager Pro", page_icon="📊", layout="wide")

# CSS Customizado (Dark Mode + Dourado)
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0D0705; color: #E0E0E0; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #1A110A; border-right: 1px solid #332211; }
    h1, h2, h3 { color: #C8973A !important; }
    .stButton>button { border: 1px solid #C8973A; color: #C8973A; border-radius: 8px; background-color: transparent; transition: 0.3s; width: 100%; }
    .stButton>button:hover { background-color: #C8973A; color: #0D0705; }
    div[data-testid="stMetricValue"] { color: #C8973A; }
    .task-card { background-color: #1A110A; padding: 15px; border-radius: 8px; border-left: 4px solid #C8973A; margin-bottom: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .task-title { font-weight: bold; font-size: 16px; margin-bottom: 5px; color: #FFFFFF; }
    .task-meta { font-size: 12px; color: #A0A0A0; margin-bottom: 8px; }
    .badge-urgent { background-color: #5A1A1A; color: #FF6B6B; padding: 2px 6px; border-radius: 4px; font-size: 10px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# GERENCIAMENTO DE DADOS (JSON)
# ==========================================
DATA_FILE = 'tasks.json'

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    # Dados iniciais baseados em rotinas de BI
    default_tasks = [
        {
            "id": str(uuid.uuid4()), "title": "Atualizar Dashboard Power BI - Garçons", "desc": "Refletir vendas do último fim de semana.",
            "category": "BI/Dashboard", "priority": "🔴 Urgente", "deadline": str(date.today()),
            "est_hours": 3.0, "tags": "powerbi, performance", "status": "A Fazer", "history": [], "pomodoros": 0
        },
        {
            "id": str(uuid.uuid4()), "title": "Extração Azure SQL", "desc": "Puxar base de clientes para análise de churn.",
            "category": "Banco de Dados", "priority": "🟡 Alta", "deadline": "2026-12-31",
            "est_hours": 2.0, "tags": "sql, azure", "status": "Em Andamento", "history": [], "pomodoros": 1
        }
    ]
    save_tasks(default_tasks)
    return default_tasks

def save_tasks(tasks):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=4)

if 'tasks' not in st.session_state:
    st.session_state.tasks = load_tasks()

def update_task_status(task_id, new_status):
    for t in st.session_state.tasks:
        if t['id'] == task_id:
            old_status = t['status']
            t['status'] = new_status
            t['history'].append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {old_status} ➔ {new_status}")
    save_tasks(st.session_state.tasks)
    st.rerun()

def delete_task(task_id):
    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task_id]
    save_tasks(st.session_state.tasks)
    st.rerun()

# ==========================================
# NOTIFICAÇÕES E CABEÇALHO
# ==========================================
hoje = date.today()
tarefas_atrasadas = [t for t in st.session_state.tasks if t['status'] != 'Concluído' and datetime.strptime(t['deadline'], '%Y-%m-%d').date() < hoje]
tarefas_hoje = [t for t in st.session_state.tasks if t['status'] != 'Concluído' and datetime.strptime(t['deadline'], '%Y-%m-%d').date() == hoje]

col_h1, col_h2, col_h3 = st.columns([2, 1, 1])
with col_h1:
    st.title("🎯 Task Manager | Analytics")
with col_h2:
    if tarefas_atrasadas:
        st.error(f"🚨 {len(tarefas_atrasadas)} Atrasadas!")
with col_h3:
    if tarefas_hoje:
        st.warning(f"⚠️ {len(tarefas_hoje)} Vencendo Hoje!")

# ==========================================
# SIDEBAR / NAVEGAÇÃO
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2098/2098402.png", width=60)
st.sidebar.markdown("### Navegação")
menu = st.sidebar.radio("", ["📋 Quadro Kanban", "📈 Dashboard", "⏱️ Pomodoro", "➕ Nova Tarefa", "⚙️ Exportar"])

# ==========================================
# TELA: NOVA TAREFA
# ==========================================
if menu == "➕ Nova Tarefa":
    st.header("Criar Nova Tarefa")
    with st.form("new_task_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Título da Tarefa*")
            category = st.selectbox("Categoria", ["BI/Dashboard", "Análise", "Reunião", "Banco de Dados", "Relatório", "Outros"])
            priority = st.selectbox("Prioridade", ["🔴 Urgente", "🟡 Alta", "🟢 Normal", "⚪ Baixa"])
        with col2:
            deadline = st.date_input("Prazo*")
            est_hours = st.number_input("Estimativa (Horas)", min_value=0.5, step=0.5)
            tags = st.text_input("Tags (separadas por vírgula)")
        
        desc = st.text_area("Descrição")
        submitted = st.form_submit_button("Salvar Tarefa")
        
        if submitted and title:
            nova_tarefa = {
                "id": str(uuid.uuid4()),
                "title": title, "desc": desc, "category": category, "priority": priority,
                "deadline": str(deadline), "est_hours": est_hours, "tags": tags,
                "status": "A Fazer", "history": [f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Criada"], "pomodoros": 0
            }
            st.session_state.tasks.append(nova_tarefa)
            save_tasks(st.session_state.tasks)
            st.success("Tarefa criada com sucesso!")

# ==========================================
# TELA: QUADRO KANBAN
# ==========================================
elif menu == "📋 Quadro Kanban":
    st.header("Quadro de Atividades")
    
    # Filtros
    f_col1, f_col2, f_col3 = st.columns(3)
    busca = f_col1.text_input("🔍 Buscar tarefa...")
    f_cat = f_col2.selectbox("Filtrar Categoria", ["Todas"] + ["BI/Dashboard", "Análise", "Reunião", "Banco de Dados", "Relatório", "Outros"])
    f_prio = f_col3.selectbox("Filtrar Prioridade", ["Todas", "🔴 Urgente", "🟡 Alta", "🟢 Normal", "⚪ Baixa"])

    # Renderização das Colunas
    cols = st.columns(4)
    status_list = ["A Fazer", "Em Andamento", "Em Revisão", "Concluído"]
    
    for i, status in enumerate(status_list):
        with cols[i]:
            st.markdown(f"<h3 style='text-align: center; font-size: 18px;'>{status}</h3>", unsafe_allow_html=True)
            
            # Filtrar tarefas da coluna
            tasks_col = [t for t in st.session_state.tasks if t['status'] == status]
            if busca:
                tasks_col = [t for t in tasks_col if busca.lower() in t['title'].lower() or busca.lower() in t['desc'].lower()]
            if f_cat != "Todas":
                tasks_col = [t for t in tasks_col if t['category'] == f_cat]
            if f_prio != "Todas":
                tasks_col = [t for t in tasks_col if t['priority'] == f_prio]

            for t in tasks_col:
                is_overdue = datetime.strptime(t['deadline'], '%Y-%m-%d').date() < hoje and status != 'Concluído'
                urgent_badge = "<span class='badge-urgent'>ATRASADA</span>" if is_overdue else ""
                
                st.markdown(f"""
                <div class="task-card">
                    <div class="task-title">{t['title']} {urgent_badge}</div>
                    <div class="task-meta">📁 {t['category']} | ⏳ {t['est_hours']}h</div>
                    <div class="task-meta">📅 {t['deadline']} | {t['priority']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Layout de botões: Voltar | Excluir | Avançar
                b1, b2, b3 = st.columns([1, 1, 1])
                with b1:
                    if i > 0:
                        if st.button("⬅️", key=f"prev_{t['id']}"):
                            update_task_status(t['id'], status_list[i-1])
                with b2:
                    if st.button("❌", key=f"del_{t['id']}"):
                        delete_task(t['id'])
                with b3:
                    if i < 3:
                        if st.button("➡️", key=f"next_{t['id']}"):
                            update_task_status(t['id'], status_list[i+1])

# ==========================================
# TELA: DASHBOARD
# ==========================================
elif menu == "📈 Dashboard":
    st.header("Visão Geral de Produtividade")
    df = pd.DataFrame(st.session_state.tasks)
    
    if not df.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total de Tarefas", len(df))
        c2.metric("Concluídas", len(df[df['status'] == 'Concluído']))
        c3.metric("Atrasadas", len(tarefas_atrasadas))
        c4.metric("Horas Estimadas", df['est_hours'].sum())

        st.markdown("---")
        
        col_graf1, col_graf2 = st.columns(2)
        plotly_template = "plotly_dark"
        cores_douradas = ['#C8973A', '#8B6508', '#DAA520', '#B8860B', '#F5DEB3']

        with col_graf1:
            fig_status = px.pie(df, names='status', title='Tarefas por Status', hole=0.4,
                                color_discrete_sequence=cores_douradas, template=plotly_template)
            fig_status.update_layout(plot_bgcolor='#0D0705', paper_bgcolor='#0D0705')
            st.plotly_chart(fig_status, use_container_width=True)

        with col_graf2:
            fig_cat = px.bar(df.groupby('category').size().reset_index(name='count'), 
                             x='category', y='count', title='Tarefas por Categoria',
                             color_discrete_sequence=['#C8973A'], template=plotly_template)
            fig_cat.update_layout(plot_bgcolor='#0D0705', paper_bgcolor='#0D0705')
            st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("Nenhuma tarefa cadastrada ainda.")

# ==========================================
# TELA: POMODORO
# ==========================================
elif menu == "⏱️ Pomodoro":
    st.header("Timer Foco (25 min)")
    tarefas_ativas = [t for t in st.session_state.tasks if t['status'] in ['A Fazer', 'Em Andamento']]
    
    if tarefas_ativas:
        tarefa_selecionada = st.selectbox("Selecione a tarefa para focar:", [t['title'] for t in tarefas_ativas])
        t_obj = next(t for t in st.session_state.tasks if t['title'] == tarefa_selecionada)
        
        st.write(f"**Pomodoros já registrados nesta tarefa:** {t_obj.get('pomodoros', 0)}")
        
        col_p1, col_p2 = st.columns(2)
        
        with col_p1:
            if st.button("▶️ Iniciar 25 Minutos (Simulação)"):
                timer_placeholder = st.empty()
                for i in range(25, 0, -1):
                    mins, secs = divmod(i, 60)
                    timer_placeholder.markdown(f"<h1 style='text-align:center; font-size: 60px;'>{mins:02d}:{secs:02d}</h1>", unsafe_allow_html=True)
                    time.sleep(1)
                timer_placeholder.success("⏰ Tempo Esgotado!")
                t_obj['pomodoros'] = t_obj.get('pomodoros', 0) + 1
                save_tasks(st.session_state.tasks)
                st.rerun()
                
        with col_p2:
            if st.button("➕ Registrar Pomodoro Manualmente"):
                t_obj['pomodoros'] = t_obj.get('pomodoros', 0) + 1
                save_tasks(st.session_state.tasks)
                st.success("Pomodoro registrado!")
                st.rerun()
    else:
        st.info("Nenhuma tarefa pendente para focar.")

# ==========================================
# TELA: EXPORTAÇÃO
# ==========================================
elif menu == "⚙️ Exportar":
    st.header("Exportar Relatórios")
    df = pd.DataFrame(st.session_state.tasks)
    
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Baixar Dados (CSV)", data=csv, file_name='tarefas_exportadas.csv', mime='text/csv')
        
        st.markdown("### Gerar Relatório em PDF")
        if st.button("📄 Gerar PDF de Concluídas"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Relatório de Produtividade", ln=True, align='C')
            pdf.ln(10)
            
            concluidas = df[df['status'] == 'Concluído']
            for _, row in concluidas.iterrows():
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(200, 10, txt=f"Tarefa: {row['title'].encode('latin-1', 'replace').decode('latin-1')}", ln=True)
                pdf.set_font("Arial", size=10)
                pdf.cell(200, 10, txt=f"Categoria: {row['category']} | Horas: {row['est_hours']}", ln=True)
                pdf.ln(5)
            
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            st.download_button(label="📥 Baixar PDF", data=pdf_bytes, file_name='relatorio_concluidas.pdf', mime='application/pdf')
    else:
        st.info("Sem dados para exportar.")