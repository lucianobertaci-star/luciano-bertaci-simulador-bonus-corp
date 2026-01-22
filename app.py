import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Simulador de Bônus | Controladoria", layout="wide")

# --- CSS CUSTOMIZADO (Visual Executivo) ---
st.markdown("""
<style>
    .metric-card {background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #1f77b4;}
    .big-font {font-size: 20px !important; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADO (BANCO DE DADOS EM MEMÓRIA) ---
if 'funcionarios' not in st.session_state:
    # Dados fictícios iniciais para teste
    st.session_state.funcionarios = [
        {"ID": 1, "Nome": "João Silva", "Cargo": "Operacional", "Salario": 3500.0, "Tempo_Casa_Meses": 12},
        {"ID": 2, "Nome": "Maria Souza", "Cargo": "Tático", "Salario": 12000.0, "Tempo_Casa_Meses": 12},
        {"ID": 3, "Nome": "Carlos CEO", "Cargo": "Estratégico", "Salario": 45000.0, "Tempo_Casa_Meses": 12}
    ]

# --- REGRAS DE NEGÓCIO E CONFIGURAÇÕES (ABA 1) ---
# Matriz de Múltiplos (Salários) por Atingimento Corporativo
REGRAS_MULTIPLOS = {
    "Estagiário":  {"min": 0.6, "parcial": 0.8, "meta": 1.0, "super": 1.2},
    "Operacional": {"min": 0.6, "parcial": 0.8, "meta": 1.0, "super": 1.2},
    "Tático":      {"min": 2.0, "parcial": 4.0, "meta": 8.0, "super": 9.0},
    "Estratégico": {"min": 2.0, "parcial": 4.0, "meta": 8.0, "super": 9.0}
}

# Definição das Faixas Corporativas (% de Atingimento)
FAIXAS_CORP = {"min": 0.90, "parcial": 0.95, "meta": 1.00, "super": 1.10}

# --- FUNÇÕES DE CÁLCULO (MOTOR) ---
def interpolar_multiplo(cargo, atingimento_corp):
    """
    Calcula o múltiplo exato usando interpolação linear baseada no atingimento corporativo.
    """
    regras = REGRAS_MULTIPLOS[cargo]
    
    # Pontos X (Atingimento) e Y (Múltiplo) para interpolação
    x_points = [FAIXAS_CORP['min'], FAIXAS_CORP['parcial'], FAIXAS_CORP['meta'], FAIXAS_CORP['super']]
    y_points = [regras['min'], regras['parcial'], regras['meta'], regras['super']]
    
    # Gatilho Mínimo: Se não atingiu o mínimo (90%), múltiplo é 0 (ou gatilho definido)
    if atingimento_corp < FAIXAS_CORP['min']:
        return 0.0
    
    # Interpolação Linear (np.interp faz a mágica da "Rampa")
    multiplo_calculado = np.interp(atingimento_corp, x_points, y_points)
    return multiplo_calculado

# --- INTERFACE DO USUÁRIO ---

st.title("🎯 Simulador de Bônus Corporativo")
st.markdown("---")

# Menu Lateral de Navegação
menu = st.sidebar.radio("Navegação", ["1. Painel Corporativo", "2. Gestão de Funcionários", "3. Simulação e Pagamento"])

# --- MÓDULO 1: PAINEL CORPORATIVO (ABA 2) ---
if menu == "1. Painel Corporativo":
    st.header("🏢 Desempenho Corporativo (UPX)")
    st.info("Insira os resultados globais da companhia para definir o 'Tamanho do Bolo'.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Indicador: EBITDA/Resultado")
        meta_corp = st.number_input("Meta (R$)", value=10000000.0, step=100000.0, format="%.2f")
        realizado_corp = st.number_input("Realizado (R$)", value=9800000.0, step=100000.0, format="%.2f")
        
        atingimento_pct = realizado_corp / meta_corp if meta_corp > 0 else 0
        
    with col2:
        st.subheader("Status de Atingimento")
        st.metric(label="% Atingimento Global", value=f"{atingimento_pct:.2%}")
        
        # Lógica visual do status
        if atingimento_pct < FAIXAS_CORP['min']:
            st.error("❌ Abaixo do Gatilho (Sem Bônus)")
        elif atingimento_pct < FAIXAS_CORP['meta']:
            st.warning("⚠️ Atingimento Parcial")
        else:
            st.success("✅ Meta Batida/Superada!")
            
    # Salvar no estado global para usar nas outras abas
    st.session_state.atingimento_global = atingimento_pct

# --- MÓDULO 2: GESTÃO DE FUNCIONÁRIOS (NOVO MÓDULO SOLICITADO) ---
elif menu == "2. Gestão de Funcionários":
    st.header("👥 Cadastro de Colaboradores")
    
    with st.expander("➕ Adicionar Novo Funcionário", expanded=False):
        with st.form("form_add"):
            c1, c2, c3 = st.columns(3)
            nome_input = c1.text_input("Nome Completo")
            cargo_input = c2.selectbox("Nível do Cargo", ["Estagiário", "Operacional", "Tático", "Estratégico"])
            salario_input = c3.number_input("Salário Base (R$)", min_value=0.0, step=100.0)
            tempo_input = st.number_input("Meses Trabalhados no Ano (Pro Rata)", min_value=1, max_value=12, value=12)
            
            submitted = st.form_submit_button("Cadastrar")
            if submitted and nome_input:
                novo_id = len(st.session_state.funcionarios) + 1
                novo_func = {
                    "ID": novo_id,
                    "Nome": nome_input,
                    "Cargo": cargo_input,
                    "Salario": salario_input,
                    "Tempo_Casa_Meses": tempo_input
                }
                st.session_state.funcionarios.append(novo_func)
                st.success(f"{nome_input} adicionado com sucesso!")

    # Exibição da Tabela
    if len(st.session_state.funcionarios) > 0:
        df_func = pd.DataFrame(st.session_state.funcionarios)
        st.dataframe(df_func.style.format({"Salario": "R$ {:,.2f}"}), use_container_width=True)
    else:
        st.info("Nenhum funcionário cadastrado.")

# --- MÓDULO 3: SIMULAÇÃO E CÁLCULO FINAL (ABA 3 e 4) ---
elif menu == "3. Simulação e Pagamento":
    st.header("💰 Simulação de Pagamento (Payroll)")
    
    # Verificar se temos atingimento global calculado
    if 'atingimento_global' not in st.session_state:
        st.warning("Por favor, defina o Resultado Corporativo na Aba 1 primeiro.")
    else:
        atingimento_global = st.session_state.atingimento_global
        st.write(f"**Cenário Atual:** Atingimento Corporativo de **{atingimento_global:.2%}**")
        
        # Tabela de Edição em Massa para Performance Individual
        st.subheader("Avaliação de Desempenho Individual")
        st.markdown("Ajuste a nota final de cada colaborador (0% a 120%) para simular o impacto.")
        
        df = pd.DataFrame(st.session_state.funcionarios)
        
        # Editor de dados interativo para performance individual
        # Criamos uma coluna padrão de 100% (1.0) se não existir
        if "Performance_Individual" not in df.columns:
            df["Performance_Individual"] = 1.0
            
        edited_df = st.data_editor(
            df,
            column_config={
                "Performance_Individual": st.column_config.NumberColumn(
                    "Nota Individual (0-1.2)",
                    help="1.0 = Meta (100%), 1.2 = Superação",
                    min_value=0.0,
                    max_value=1.2,
                    step=0.05,
                    format="%.2f"
                ),
                "Salario": st.column_config.NumberColumn(format="R$ %.2f")
            },
            hide_index=True,
            use_container_width=True
        )
        
        st.divider()
        
        # --- CÁLCULO DO BÔNUS (ENGINE) ---
        if st.button("🚀 Calcular Bônus Final"):
            resultados = []
            total_folha_bonus = 0
            
            for index, row in edited_df.iterrows():
                # 1. Busca o Múltiplo Interpolado (Baseado no Corp)
                multiplo_aplicado = interpolar_multiplo(row['Cargo'], atingimento_global)
                
                # 2. Fator Pro Rata (Meses/12)
                fator_tempo = row['Tempo_Casa_Meses'] / 12
                
                # 3. Fator Performance Individual (Input do Grid)
                fator_individual = row['Performance_Individual']
                
                # 4. Fórmula Final (Validada por você)
                # Bonus = Salário x Indiv x ProRata x Múltiplo(já impactado pelo Corp) x Fator(1)
                bonus_bruto = row['Salario'] * fator_individual * fator_tempo * multiplo_aplicado * 1.0
                
                resultados.append({
                    "Nome": row['Nome'],
                    "Cargo": row['Cargo'],
                    "Salário": row['Salario'],
                    "Múltiplo (Ref. Corp)": multiplo_aplicado,
                    "Nota Indiv.": fator_individual,
                    "Bônus Projetado": bonus_bruto
                })
                total_folha_bonus += bonus_bruto
            
            # Exibição dos Resultados
            df_resultado = pd.DataFrame(resultados)
            
            # KPIs do Topo
            kpi1, kpi2 = st.columns(2)
            kpi1.metric("Total da Folha de Bônus", f"R$ {total_folha_bonus:,.2f}")
            kpi2.metric("Headcount Elegível", len(df_resultado))
            
            # Tabela Detalhada
            st.subheader("Extrato Detalhado por Colaborador")
            st.dataframe(
                df_resultado.style.format({
                    "Salário": "R$ {:,.2f}",
                    "Bônus Projetado": "R$ {:,.2f}",
                    "Múltiplo (Ref. Corp)": "{:.2f}x",
                    "Nota Indiv.": "{:.0%}"
                }),
                use_container_width=True
            )
            
            # Gráfico de Distribuição
            st.bar_chart(df_resultado, x="Nome", y="Bônus Projetado")
