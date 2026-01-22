{\rtf1\ansi\ansicpg1252\cocoartf2867
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import pandas as pd\
import numpy as np\
\
# --- CONFIGURA\'c7\'c3O DA P\'c1GINA ---\
st.set_page_config(page_title="Simulador de B\'f4nus | Controladoria", layout="wide")\
\
# --- CSS CUSTOMIZADO (Visual Executivo) ---\
st.markdown("""\
<style>\
    .metric-card \{background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #1f77b4;\}\
    .big-font \{font-size: 20px !important; font-weight: bold;\}\
</style>\
""", unsafe_allow_html=True)\
\
# --- INICIALIZA\'c7\'c3O DE ESTADO (BANCO DE DADOS EM MEM\'d3RIA) ---\
if 'funcionarios' not in st.session_state:\
    # Dados fict\'edcios iniciais para teste\
    st.session_state.funcionarios = [\
        \{"ID": 1, "Nome": "Jo\'e3o Silva", "Cargo": "Operacional", "Salario": 3500.0, "Tempo_Casa_Meses": 12\},\
        \{"ID": 2, "Nome": "Maria Souza", "Cargo": "T\'e1tico", "Salario": 12000.0, "Tempo_Casa_Meses": 12\},\
        \{"ID": 3, "Nome": "Carlos CEO", "Cargo": "Estrat\'e9gico", "Salario": 45000.0, "Tempo_Casa_Meses": 12\}\
    ]\
\
# --- REGRAS DE NEG\'d3CIO E CONFIGURA\'c7\'d5ES (ABA 1) ---\
# Matriz de M\'faltiplos (Sal\'e1rios) por Atingimento Corporativo\
REGRAS_MULTIPLOS = \{\
    "Estagi\'e1rio":  \{"min": 0.6, "parcial": 0.8, "meta": 1.0, "super": 1.2\},\
    "Operacional": \{"min": 0.6, "parcial": 0.8, "meta": 1.0, "super": 1.2\},\
    "T\'e1tico":      \{"min": 2.0, "parcial": 4.0, "meta": 8.0, "super": 9.0\},\
    "Estrat\'e9gico": \{"min": 2.0, "parcial": 4.0, "meta": 8.0, "super": 9.0\}\
\}\
\
# Defini\'e7\'e3o das Faixas Corporativas (% de Atingimento)\
FAIXAS_CORP = \{"min": 0.90, "parcial": 0.95, "meta": 1.00, "super": 1.10\}\
\
# --- FUN\'c7\'d5ES DE C\'c1LCULO (MOTOR) ---\
def interpolar_multiplo(cargo, atingimento_corp):\
    """\
    Calcula o m\'faltiplo exato usando interpola\'e7\'e3o linear baseada no atingimento corporativo.\
    """\
    regras = REGRAS_MULTIPLOS[cargo]\
    \
    # Pontos X (Atingimento) e Y (M\'faltiplo) para interpola\'e7\'e3o\
    x_points = [FAIXAS_CORP['min'], FAIXAS_CORP['parcial'], FAIXAS_CORP['meta'], FAIXAS_CORP['super']]\
    y_points = [regras['min'], regras['parcial'], regras['meta'], regras['super']]\
    \
    # Gatilho M\'ednimo: Se n\'e3o atingiu o m\'ednimo (90%), m\'faltiplo \'e9 0 (ou gatilho definido)\
    if atingimento_corp < FAIXAS_CORP['min']:\
        return 0.0\
    \
    # Interpola\'e7\'e3o Linear (np.interp faz a m\'e1gica da "Rampa")\
    multiplo_calculado = np.interp(atingimento_corp, x_points, y_points)\
    return multiplo_calculado\
\
# --- INTERFACE DO USU\'c1RIO ---\
\
st.title("\uc0\u55356 \u57263  Simulador de B\'f4nus Corporativo")\
st.markdown("---")\
\
# Menu Lateral de Navega\'e7\'e3o\
menu = st.sidebar.radio("Navega\'e7\'e3o", ["1. Painel Corporativo", "2. Gest\'e3o de Funcion\'e1rios", "3. Simula\'e7\'e3o e Pagamento"])\
\
# --- M\'d3DULO 1: PAINEL CORPORATIVO (ABA 2) ---\
if menu == "1. Painel Corporativo":\
    st.header("\uc0\u55356 \u57314  Desempenho Corporativo (UPX)")\
    st.info("Insira os resultados globais da companhia para definir o 'Tamanho do Bolo'.")\
    \
    col1, col2 = st.columns(2)\
    with col1:\
        st.subheader("Indicador: EBITDA/Resultado")\
        meta_corp = st.number_input("Meta (R$)", value=10000000.0, step=100000.0, format="%.2f")\
        realizado_corp = st.number_input("Realizado (R$)", value=9800000.0, step=100000.0, format="%.2f")\
        \
        atingimento_pct = realizado_corp / meta_corp if meta_corp > 0 else 0\
        \
    with col2:\
        st.subheader("Status de Atingimento")\
        st.metric(label="% Atingimento Global", value=f"\{atingimento_pct:.2%\}")\
        \
        # L\'f3gica visual do status\
        if atingimento_pct < FAIXAS_CORP['min']:\
            st.error("\uc0\u10060  Abaixo do Gatilho (Sem B\'f4nus)")\
        elif atingimento_pct < FAIXAS_CORP['meta']:\
            st.warning("\uc0\u9888 \u65039  Atingimento Parcial")\
        else:\
            st.success("\uc0\u9989  Meta Batida/Superada!")\
            \
    # Salvar no estado global para usar nas outras abas\
    st.session_state.atingimento_global = atingimento_pct\
\
# --- M\'d3DULO 2: GEST\'c3O DE FUNCION\'c1RIOS (NOVO M\'d3DULO SOLICITADO) ---\
elif menu == "2. Gest\'e3o de Funcion\'e1rios":\
    st.header("\uc0\u55357 \u56421  Cadastro de Colaboradores")\
    \
    with st.expander("\uc0\u10133  Adicionar Novo Funcion\'e1rio", expanded=False):\
        with st.form("form_add"):\
            c1, c2, c3 = st.columns(3)\
            nome_input = c1.text_input("Nome Completo")\
            cargo_input = c2.selectbox("N\'edvel do Cargo", ["Estagi\'e1rio", "Operacional", "T\'e1tico", "Estrat\'e9gico"])\
            salario_input = c3.number_input("Sal\'e1rio Base (R$)", min_value=0.0, step=100.0)\
            tempo_input = st.number_input("Meses Trabalhados no Ano (Pro Rata)", min_value=1, max_value=12, value=12)\
            \
            submitted = st.form_submit_button("Cadastrar")\
            if submitted and nome_input:\
                novo_id = len(st.session_state.funcionarios) + 1\
                novo_func = \{\
                    "ID": novo_id,\
                    "Nome": nome_input,\
                    "Cargo": cargo_input,\
                    "Salario": salario_input,\
                    "Tempo_Casa_Meses": tempo_input\
                \}\
                st.session_state.funcionarios.append(novo_func)\
                st.success(f"\{nome_input\} adicionado com sucesso!")\
\
    # Exibi\'e7\'e3o da Tabela\
    if len(st.session_state.funcionarios) > 0:\
        df_func = pd.DataFrame(st.session_state.funcionarios)\
        st.dataframe(df_func.style.format(\{"Salario": "R$ \{:,.2f\}"\}), use_container_width=True)\
    else:\
        st.info("Nenhum funcion\'e1rio cadastrado.")\
\
# --- M\'d3DULO 3: SIMULA\'c7\'c3O E C\'c1LCULO FINAL (ABA 3 e 4) ---\
elif menu == "3. Simula\'e7\'e3o e Pagamento":\
    st.header("\uc0\u55357 \u56496  Simula\'e7\'e3o de Pagamento (Payroll)")\
    \
    # Verificar se temos atingimento global calculado\
    if 'atingimento_global' not in st.session_state:\
        st.warning("Por favor, defina o Resultado Corporativo na Aba 1 primeiro.")\
    else:\
        atingimento_global = st.session_state.atingimento_global\
        st.write(f"**Cen\'e1rio Atual:** Atingimento Corporativo de **\{atingimento_global:.2%\}**")\
        \
        # Tabela de Edi\'e7\'e3o em Massa para Performance Individual\
        st.subheader("Avalia\'e7\'e3o de Desempenho Individual")\
        st.markdown("Ajuste a nota final de cada colaborador (0% a 120%) para simular o impacto.")\
        \
        df = pd.DataFrame(st.session_state.funcionarios)\
        \
        # Editor de dados interativo para performance individual\
        # Criamos uma coluna padr\'e3o de 100% (1.0) se n\'e3o existir\
        if "Performance_Individual" not in df.columns:\
            df["Performance_Individual"] = 1.0\
            \
        edited_df = st.data_editor(\
            df,\
            column_config=\{\
                "Performance_Individual": st.column_config.NumberColumn(\
                    "Nota Individual (0-1.2)",\
                    help="1.0 = Meta (100%), 1.2 = Supera\'e7\'e3o",\
                    min_value=0.0,\
                    max_value=1.2,\
                    step=0.05,\
                    format="%.2f"\
                ),\
                "Salario": st.column_config.NumberColumn(format="R$ %.2f")\
            \},\
            hide_index=True,\
            use_container_width=True\
        )\
        \
        st.divider()\
        \
        # --- C\'c1LCULO DO B\'d4NUS (ENGINE) ---\
        if st.button("\uc0\u55357 \u56960  Calcular B\'f4nus Final"):\
            resultados = []\
            total_folha_bonus = 0\
            \
            for index, row in edited_df.iterrows():\
                # 1. Busca o M\'faltiplo Interpolado (Baseado no Corp)\
                multiplo_aplicado = interpolar_multiplo(row['Cargo'], atingimento_global)\
                \
                # 2. Fator Pro Rata (Meses/12)\
                fator_tempo = row['Tempo_Casa_Meses'] / 12\
                \
                # 3. Fator Performance Individual (Input do Grid)\
                fator_individual = row['Performance_Individual']\
                \
                # 4. F\'f3rmula Final (Validada por voc\'ea)\
                # Bonus = Sal\'e1rio x Indiv x ProRata x M\'faltiplo(j\'e1 impactado pelo Corp) x Fator(1)\
                bonus_bruto = row['Salario'] * fator_individual * fator_tempo * multiplo_aplicado * 1.0\
                \
                resultados.append(\{\
                    "Nome": row['Nome'],\
                    "Cargo": row['Cargo'],\
                    "Sal\'e1rio": row['Salario'],\
                    "M\'faltiplo (Ref. Corp)": multiplo_aplicado,\
                    "Nota Indiv.": fator_individual,\
                    "B\'f4nus Projetado": bonus_bruto\
                \})\
                total_folha_bonus += bonus_bruto\
            \
            # Exibi\'e7\'e3o dos Resultados\
            df_resultado = pd.DataFrame(resultados)\
            \
            # KPIs do Topo\
            kpi1, kpi2 = st.columns(2)\
            kpi1.metric("Total da Folha de B\'f4nus", f"R$ \{total_folha_bonus:,.2f\}")\
            kpi2.metric("Headcount Eleg\'edvel", len(df_resultado))\
            \
            # Tabela Detalhada\
            st.subheader("Extrato Detalhado por Colaborador")\
            st.dataframe(\
                df_resultado.style.format(\{\
                    "Sal\'e1rio": "R$ \{:,.2f\}",\
                    "B\'f4nus Projetado": "R$ \{:,.2f\}",\
                    "M\'faltiplo (Ref. Corp)": "\{:.2f\}x",\
                    "Nota Indiv.": "\{:.0%\}"\
                \}),\
                use_container_width=True\
            )\
            \
            # Gr\'e1fico de Distribui\'e7\'e3o\
            st.bar_chart(df_resultado, x="Nome", y="B\'f4nus Projetado")}