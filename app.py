import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Simulador de Bônus | Controladoria", layout="wide")

# --- SISTEMA DE LOGIN ---
def check_password():
    if st.secrets.get("PASSWORD") is None: return True
    def password_entered():
        if st.session_state["password"] == st.secrets["PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False
    if st.session_state.get("password_correct", False): return True
    st.text_input("🔒 Digite a senha de acesso:", type="password", on_change=password_entered, key="password")
    return False

if not check_password(): st.stop()

# --- INICIALIZAÇÃO DE DADOS (SESSION STATE) ---
# Aqui transformamos as regras fixas em Tabelas Editáveis

if 'config_multiplos' not in st.session_state:
    # Dados iniciais
    data = [
        {"Cargo": "Estagiário", "Mínimo": 0.6, "Parcial": 0.8, "Meta": 1.0, "Superado": 1.2},
        {"Cargo": "Operacional", "Mínimo": 0.6, "Parcial": 0.8, "Meta": 1.0, "Superado": 1.2},
        {"Cargo": "Tático", "Mínimo": 2.0, "Parcial": 4.0, "Meta": 8.0, "Superado": 9.0},
        {"Cargo": "Estratégico", "Mínimo": 2.0, "Parcial": 4.0, "Meta": 8.0, "Superado": 9.0}
    ]
    st.session_state.config_multiplos = pd.DataFrame(data)

if 'config_faixas' not in st.session_state:
    # Dados iniciais de faixas
    data_faixas = [
        {"Nível": "Mínimo", "Gatilho": 0.90},
        {"Nível": "Parcial", "Gatilho": 0.95},
        {"Nível": "Meta", "Gatilho": 1.00},
        {"Nível": "Superado", "Gatilho": 1.10}
    ]
    st.session_state.config_faixas = pd.DataFrame(data_faixas)

if 'funcionarios' not in st.session_state:
    st.session_state.funcionarios = [
        {"ID": 1, "Nome": "João Silva", "Cargo": "Operacional", "Salario": 3500.0, "Tempo_Casa_Meses": 12},
        {"ID": 2, "Nome": "Maria Souza", "Cargo": "Tático", "Salario": 12000.0, "Tempo_Casa_Meses": 12},
        {"ID": 3, "Nome": "Carlos CEO", "Cargo": "Estratégico", "Salario": 45000.0, "Tempo_Casa_Meses": 12}
    ]

# --- FUNÇÃO DE CÁLCULO ATUALIZADA (Lê das tabelas configuradas) ---
def interpolar_multiplo(cargo, atingimento_corp):
    # 1. Ler as Faixas (Eixo X) da configuração
    df_faixas = st.session_state.config_faixas
    try:
        min_g = df_faixas.loc[df_faixas['Nível']=='Mínimo', 'Gatilho'].values[0]
        par_g = df_faixas.loc[df_faixas['Nível']=='Parcial', 'Gatilho'].values[0]
        meta_g = df_faixas.loc[df_faixas['Nível']=='Meta', 'Gatilho'].values[0]
        super_g = df_faixas.loc[df_faixas['Nível']=='Superado', 'Gatilho'].values[0]
    except:
        return 0.0 # Fallback se deletarem linhas
        
    x_points = [min_g, par_g, meta_g, super_g]
    
    # 2. Ler os Múltiplos (Eixo Y) para o cargo específico
    df_mult = st.session_state.config_multiplos
    row = df_mult[df_mult['Cargo'] == cargo]
    
    if row.empty: return 0.0
    
    y_points = [
        row['Mínimo'].values[0], 
        row['Parcial'].values[0], 
        row['Meta'].values[0], 
        row['Superado'].values[0]
    ]
    
    if atingimento_corp < min_g: return 0.0
    
    return np.interp(atingimento_corp, x_points, y_points)

# --- INTERFACE ---
st.title("🎯 Simulador de Bônus Corporativo")
st.markdown("---")

menu = st.sidebar.radio("Navegação", [
    "0. Configurações Gerais", 
    "1. Painel Corporativo", 
    "2. Gestão de Funcionários", 
    "3. Simulação e Pagamento"
])

# --- ABA 0: CONFIGURAÇÕES (NOVA) ---
if menu == "0. Configurações Gerais":
    st.header("⚙️ Parâmetros do Sistema")
    st.info("Ajuste aqui as regras que alimentam o cálculo.")
    
    st.subheader("1. Múltiplos Salariais por Cargo")
    # Tabela 1: Formatada com 1 casa decimal
    edited_mult = st.data_editor(
        st.session_state.config_multiplos,
        column_config={
            "Mínimo": st.column_config.NumberColumn(format="%.1f"),
            "Parcial": st.column_config.NumberColumn(format="%.1f"),
            "Meta": st.column_config.NumberColumn(format="%.1f"),
            "Superado": st.column_config.NumberColumn(format="%.1f"),
        },
        use_container_width=True,
        key="editor_multiplos"
    )
    st.session_state.config_multiplos = edited_mult
    
    st.markdown("---") # Divisor visual
    
    st.subheader("2. Faixas de Atingimento (Gatilhos)")
    # Tabela 2: Abaixo da 1, formatada em % com 2 casas
    edited_faixas = st.data_editor(
        st.session_state.config_faixas,
        column_config={
            "Gatilho": st.column_config.NumberColumn(
                label="Gatilho (%)",
                format="%.2f %%",
                min_value=0.0,
                max_value=2.0,
                step=0.01
            )
        },
        use_container_width=True,
        key="editor_faixas"
    )
    st.session_state.config_faixas = edited_faixas

# --- ABA 1: CORPORATIVO (IGUAL V2) ---
elif menu == "1. Painel Corporativo":
    st.header("🏢 Desempenho Corporativo")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Indicador: EBITDA/Resultado")
        meta_corp = st.number_input("Meta (R$)", value=10000000.0, step=100000.0, format="%.2f")
        realizado_corp = st.number_input("Realizado (R$)", value=9800000.0, step=100000.0, format="%.2f")
        atingimento_pct = realizado_corp / meta_corp if meta_corp > 0 else 0
        
    with col2:
        st.subheader("Status")
        st.metric(label="% Atingimento Global", value=f"{atingimento_pct:.2%}")
        
        # Leitura dinâmica do gatilho mínimo para dar feedback
        df_f = st.session_state.config_faixas
        try:
            min_trigger = df_f.loc[df_f['Nível']=='Mínimo', 'Gatilho'].values[0]
            if atingimento_pct < min_trigger:
                st.error("❌ Abaixo do Gatilho")
            else:
                st.success("✅ Elegível para Bônus")
        except:
            st.warning("Verifique as configurações.")
            
    st.session_state.atingimento_global = atingimento_pct

# --- ABA 2: FUNCIONÁRIOS (IGUAL V2) ---
elif menu == "2. Gestão de Funcionários":
    st.header("👥 Cadastro de Colaboradores")
    
    with st.expander("➕ Adicionar Novo Funcionário", expanded=False):
        with st.form("form_add"):
            c1, c2, c3 = st.columns(3)
            nome_input = c1.text_input("Nome")
            # Carrega cargos dinamicamente da configuração
            lista_cargos = list(st.session_state.config_multiplos['Cargo'].unique())
            cargo_input = c2.selectbox("Cargo", lista_cargos)
            salario_input = c3.number_input("Salário (R$)", step=100.0)
            tempo_input = st.number_input("Meses", 1, 12, 12)
            
            if st.form_submit_button("Cadastrar"):
                new_id = len(st.session_state.funcionarios) + 1
                st.session_state.funcionarios.append({
                    "ID": new_id, "Nome": nome_input, "Cargo": cargo_input, 
                    "Salario": salario_input, "Tempo_Casa_Meses": tempo_input
                })
                st.success("Adicionado!")
                st.rerun()

    if len(st.session_state.funcionarios) > 0:
        st.dataframe(pd.DataFrame(st.session_state.funcionarios).style.format({"Salario": "R$ {:,.2f}"}), use_container_width=True)
        if st.button("Limpar Lista"):
            st.session_state.funcionarios = []
            st.rerun()

# --- ABA 3: SIMULAÇÃO (IGUAL V2) ---
elif menu == "3. Simulação e Pagamento":
    st.header("💰 Simulação de Pagamento")
    
    if 'atingimento_global' not in st.session_state:
        st.warning("Defina o Painel Corporativo primeiro.")
    else:
        atingimento = st.session_state.atingimento_global
        st.write(f"**Cenário:** Atingimento Global de **{atingimento:.2%}**")
        
        df = pd.DataFrame(st.session_state.funcionarios)
        if not df.empty:
            if "Performance_Individual" not in df.columns: df["Performance_Individual"] = 1.0
            
            edited_df = st.data_editor(
                df,
                column_config={
                    "Performance_Individual": st.column_config.NumberColumn("Nota Indiv. (0-1.2)", format="%.2f", step=0.05),
                    "Salario": st.column_config.NumberColumn(format="R$ %.2f")
                },
                hide_index=True,
                use_container_width=True
            )
            
            if st.button("🚀 Calcular"):
                res = []
                total = 0
                for i, row in edited_df.iterrows():
                    mult = interpolar_multiplo(row['Cargo'], atingimento)
                    bonus = row['Salario'] * row['Performance_Individual'] * (row['Tempo_Casa_Meses']/12) * mult
                    res.append({
                        "Nome": row['Nome'], "Cargo": row['Cargo'], "Salário": row['Salario'],
                        "Múltiplo": mult, "Nota Indiv.": row['Performance_Individual'], "Bônus": bonus
                    })
                    total += bonus
                
                df_res = pd.DataFrame(res)
                st.metric("Total Folha", f"R$ {total:,.2f}")
                st.dataframe(df_res.style.format({"Salário": "R$ {:,.2f}", "Bônus": "R$ {:,.2f}", "Múltiplo": "{:.2f}x", "Nota Indiv.": "{:.0%}"}), use_container_width=True)
        else:
            st.warning("Sem funcionários.")
