import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Simulador Bônus V2 | Controladoria", layout="wide", initial_sidebar_state="expanded")

# --- ESTILO CSS ---
st.markdown("""
<style>
    .main-header {font-size: 24px; font-weight: bold; color: #1f77b4;}
    .sub-header {font-size: 18px; font-weight: bold; color: #333;}
    .metric-box {background-color: #f8f9fa; border: 1px solid #ddd; padding: 15px; border-radius: 5px;}
    .formula-box {background-color: #e8f4f8; padding: 15px; border-left: 5px solid #1f77b4; font-family: monospace;}
</style>
""", unsafe_allow_html=True)

# --- SISTEMA DE LOGIN ---
def check_password():
    if st.secrets.get("PASSWORD") is None: return True # Se não tiver senha configurada, libera
    
    def password_entered():
        if st.session_state["password"] == st.secrets["PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.text_input("🔒 Senha de Acesso:", type="password", on_change=password_entered, key="password")
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("Senha incorreta.")
    return False

if not check_password():
    st.stop()

# --- INICIALIZAÇÃO DE DADOS (SESSION STATE) ---
if 'config_multiplos' not in st.session_state:
    # Dados Iniciais de Configuração (Conforme seu pedido)
    data_mult = {
        "Cargo": ["Estagiário", "Operacional", "Tático", "Estratégico"],
        "Mínimo (x)": [0.6, 0.6, 1.0, 2.0],
        "Parcial (x)": [0.8, 0.8, 3.0, 4.0],
        "Meta (x)": [1.0, 1.0, 5.0, 8.0],
        "Superado (x)": [1.2, 1.2, 6.0, 9.0]
    }
    st.session_state.config_multiplos = pd.DataFrame(data_mult)

if 'config_faixas' not in st.session_state:
    # Faixas de Atingimento (% da Meta)
    data_faixas = {
        "Nível": ["Mínimo", "Parcial", "Meta", "Superado"],
        "Gatilho (%)": [0.90, 0.95, 1.00, 1.10]
    }
    st.session_state.config_faixas = pd.DataFrame(data_faixas)

if 'metas_corp' not in st.session_state:
    # Indicadores Corporativos Iniciais
    st.session_state.metas_corp = [
        {"Indicador": "Receitas", "Peso": 80, "Meta ($)": 40735845.0, "Realizado ($)": 38700644.0},
        {"Indicador": "Fluxo Caixa", "Peso": 20, "Meta ($)": 16922142.0, "Realizado ($)": 18154955.0}
    ]

if 'funcionarios' not in st.session_state:
    # Estrutura complexa: Lista de Dicionários contendo sub-listas de metas
    st.session_state.funcionarios = [
        {
            "ID": 1, "Nome": "João Silva", "Cargo": "Tático", "Salario": 12000.0, "Tempo_Casa": 12,
            "Metas": [
                {"Descricao": "Dashboard Resultados", "Peso": 25, "Meta": 100.0, "Realizado": 50.0},
                {"Descricao": "Processos Financeiros", "Peso": 25, "Meta": 100.0, "Realizado": 95.0},
                {"Descricao": "Migração Netsuite", "Peso": 50, "Meta": 100.0, "Realizado": 95.0}
            ]
        }
    ]

# --- FUNÇÕES DE CÁLCULO ---
def calcular_interpolacao(realizado_pct, faixas_df, multiplos_row=None):
    """
    Motor de cálculo que serve tanto para Corp quanto para Individual.
    Se receber 'multiplos_row', interpola Salários. Se não, interpola Nota (0 a 1.2 ou similar).
    """
    # Extrair os gatilhos da configuração
    min_g = faixas_df.loc[faixas_df['Nível']=='Mínimo', 'Gatilho (%)'].values[0]
    par_g = faixas_df.loc[faixas_df['Nível']=='Parcial', 'Gatilho (%)'].values[0]
    meta_g = faixas_df.loc[faixas_df['Nível']=='Meta', 'Gatilho (%)'].values[0]
    super_g = faixas_df.loc[faixas_df['Nível']=='Superado', 'Gatilho (%)'].values[0]
    
    x_points = [min_g, par_g, meta_g, super_g]
    
    # Se for cálculo de múltiplos (Salários)
    if multiplos_row is not None:
        y_points = [
            multiplos_row['Mínimo (x)'], multiplos_row['Parcial (x)'], 
            multiplos_row['Meta (x)'], multiplos_row['Superado (x)']
        ]
    else:
        # Se for nota pura (Corporativa ou Individual), assumimos nota 0.6, 0.8, 1.0, 1.2 como padrão de performance
        # Ou conforme sua tabela "Meta Corporativo: 0.6, 0.8, 1.0, 1.2"
        y_points = [0.6, 0.8, 1.0, 1.2] # Padrão definido na sua mensagem para "Meta Corporativo"

    if realizado_pct < min_g:
        return 0.0
    
    return np.interp(realizado_pct, x_points, y_points)

# --- MENU LATERAL ---
st.sidebar.title("Simulador Bônus V2")
menu = st.sidebar.radio("Ir para:", ["1. Configurações Gerais", "2. Painel Corporativo", "3. Gestão Funcionários", "4. Simulação/Pagamento"])

# --- ABA 1: CONFIGURAÇÕES ---
if menu == "1. Configurações Gerais":
    st.markdown("<div class='main-header'>⚙️ Configurações e Parâmetros</div>", unsafe_allow_html=True)
    st.info("Aqui você define as regras globais. Alterações aqui impactam todo o cálculo.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("1. Múltiplos Salariais por Cargo")
        # Editor de Tabela para Múltiplos
        edited_mult = st.data_editor(st.session_state.config_multiplos, num_rows="dynamic", use_container_width=True)
        st.session_state.config_multiplos = edited_mult
        
    with c2:
        st.subheader("2. Faixas de Atingimento (Gatilhos)")
        st.markdown("Defina os % da meta necessários para atingir cada nível.")
        edited_faixas = st.data_editor(st.session_state.config_faixas, use_container_width=True)
        st.session_state.config_faixas = edited_faixas

# --- ABA 2: PAINEL CORPORATIVO ---
elif menu == "2. Painel Corporativo":
    st.markdown("<div class='main-header'>🏢 Painel de Metas Corporativas</div>", unsafe_allow_html=True)
    
    # Converter lista para DF para edição
    df_metas_corp = pd.DataFrame(st.session_state.metas_corp)
    
    st.subheader("Indicadores Globais")
    config_metas = st.column_config.NumberColumn("Meta ($)", format="$ %.2f")
    config_real = st.column_config.NumberColumn("Realizado ($)", format="$ %.2f")
    
    edited_corp = st.data_editor(
        df_metas_corp, 
        column_config={"Meta ($)": config_metas, "Realizado ($)": config_real},
        num_rows="dynamic", 
        use_container_width=True
    )
    
    # Atualizar session state
    st.session_state.metas_corp = edited_corp.to_dict('records')
    
    # Cálculo em Tempo Real do Resultado Corporativo
    st.divider()
    st.subheader("🧮 Apuração do Resultado Corporativo")
    
    total_score = 0
    total_peso = 0
    
    detalhes_calc = []
    
    for item in st.session_state.metas_corp:
        peso = item['Peso']
        meta = item['Meta ($)']
        real = item['Realizado ($)']
        
        atingimento_pct = real / meta if meta > 0 else 0
        
        # Calcular Nota Interpolada (0.6 a 1.2 baseado no atingimento)
        nota_interpolada = calcular_interpolacao(atingimento_pct, st.session_state.config_faixas, multiplos_row=None)
        
        score_item = nota_interpolada * (peso / 100)
        total_score += score_item
        total_peso += peso
        
        detalhes_calc.append({
            "Indicador": item['Indicador'],
            "Atingimento (%)": atingimento_pct,
            "Nota Interpolada": nota_interpolada,
            "Contribuição p/ Nota Final": score_item
        })
        
    df_detalhe = pd.DataFrame(detalhes_calc)
    st.dataframe(df_detalhe.style.format({
        "Atingimento (%)": "{:.1%}", 
        "Nota Interpolada": "{:.2f}",
        "Contribuição p/ Nota Final": "{:.4f}"
    }))
    
    col_res1, col_res2 = st.columns(2)
    col_res1.metric("Nota Corporativa Final", f"{total_score:.2f}", help="Soma das Contribuições")
    
    if total_peso != 100:
        col_res2.error(f"⚠️ Atenção: A soma dos pesos está {total_peso}%. Deve ser 100%.")
    else:
        col_res2.success("Pesos balanceados (100%)")
        
    st.session_state.nota_corporativa_final = total_score

# --- ABA 3: GESTÃO DE FUNCIONÁRIOS ---
elif menu == "3. Gestão Funcionários":
    st.markdown("<div class='main-header'>👥 Gestão de Colaboradores e Metas</div>", unsafe_allow_html=True)
    
    # Seletor de Funcionário para Editar ou Criar
    lista_nomes = [f"{f['ID']} - {f['Nome']}" for f in st.session_state.funcionarios]
    lista_nomes.insert(0, "➕ Novo Funcionário")
    
    selection = st.selectbox("Selecione para editar:", lista_nomes)
    
    if selection == "➕ Novo Funcionário":
        st.subheader("Cadastrar Novo")
        with st.form("new_func"):
            nome = st.text_input("Nome")
            cargo = st.selectbox("Cargo", st.session_state.config_multiplos['Cargo'].unique())
            salario = st.number_input("Salário", step=1000.0)
            tempo = st.number_input("Meses de Casa", 1, 12, 12)
            if st.form_submit_button("Salvar"):
                new_id = len(st.session_state.funcionarios) + 1
                st.session_state.funcionarios.append({
                    "ID": new_id, "Nome": nome, "Cargo": cargo, "Salario": salario, "Tempo_Casa": tempo,
                    "Metas": [{"Descricao": "Meta Padrão", "Peso": 100, "Meta": 100.0, "Realizado": 0.0}]
                })
                st.rerun()
                
    else:
        # Modo Edição
        id_selecionado = int(selection.split(" - ")[0])
        func_index = next((i for i, item in enumerate(st.session_state.funcionarios) if item["ID"] == id_selecionado), None)
        func = st.session_state.funcionarios[func_index]
        
        c1, c2, c3, c4 = st.columns(4)
        func['Nome'] = c1.text_input("Nome", func['Nome'])
        func['Cargo'] = c2.selectbox("Cargo", st.session_state.config_multiplos['Cargo'].unique(), index=list(st.session_state.config_multiplos['Cargo']).index(func['Cargo']) if func['Cargo'] in list(st.session_state.config_multiplos['Cargo']) else 0)
        func['Salario'] = c3.number_input("Salário", value=float(func['Salario']))
        func['Tempo_Casa'] = c4.number_input("Meses", 1, 12, int(func['Tempo_Casa']))
        
        st.divider()
        st.subheader(f"🎯 Metas Individuais de {func['Nome']}")
        
        # Edição das Metas deste funcionário
        df_metas_indiv = pd.DataFrame(func['Metas'])
        edited_metas_indiv = st.data_editor(
            df_metas_indiv, 
            num_rows="dynamic", 
            use_container_width=True,
            column_config={
                "Peso": st.column_config.NumberColumn("Peso (%)", min_value=0, max_value=100),
                "Realizado": st.column_config.NumberColumn("Realizado (Absoluto)")
            }
        )
        
        # Salvar as alterações das metas na memória
        st.session_state.funcionarios[func_index]['Metas'] = edited_metas_indiv.to_dict('records')
        
        # Preview do Cálculo Individual
        total_nota_indiv = 0
        soma_pesos = 0
        for m in st.session_state.funcionarios[func_index]['Metas']:
            peso = m['Peso']
            meta = m['Meta']
            real = m['Realizado']
            soma_pesos += peso
            
            atg = real / meta if meta > 0 else 0
            # Interpolação da nota individual (0.6 a 1.2 ou conforme regra)
            # AQUI ASSUMIMOS QUE A TABELA DE ATINGIMENTO SEGUE A MESMA LÓGICA (Min, Parcial, Meta, Super)
            nota = calcular_interpolacao(atg, st.session_state.config_faixas, multiplos_row=None)
            total_nota_indiv += nota * (peso/100)
            
        st.info(f"Nota Individual Projetada: {total_nota_indiv:.2f} (Soma Pesos: {soma_pesos}%)")

# --- ABA 4: SIMULAÇÃO E PAGAMENTO ---
elif menu == "4. Simulação/Pagamento":
    st.markdown("<div class='main-header'>💰 Folha de Pagamento de Bônus</div>", unsafe_allow_html=True)
    
    if 'nota_corporativa_final' not in st.session_state:
        st.warning("Vá na aba 'Painel Corporativo' para calcular o resultado da empresa primeiro.")
        st.stop()
        
    nota_corp = st.session_state.nota_corporativa_final
    st.markdown(f"**Nota Corporativa Aplicada:** {nota_corp:.4f}")
    
    # Explicar a Fórmula
    with st.expander("Ver Fórmula de Cálculo"):
        st.markdown("""
        **Fórmula:**
        $$
        Bônus = Salário \times FatorTempo \times MúltiploCargo(NotaCorp) \times FatorIndividual
        $$
        
        Onde:
        1. **MúltiploCargo:** Vem da tabela de configuração, interpolando a Nota Corporativa.
        2. **FatorIndividual:** É a média ponderada das metas do funcionário.
        """)
    
    if st.button("🚀 Calcular Folha de Bônus"):
        folha = []
        
        for f in st.session_state.funcionarios:
            # 1. Calcular Nota Individual
            nota_indiv_total = 0
            for m in f['Metas']:
                atg = m['Realizado'] / m['Meta'] if m['Meta'] > 0 else 0
                nota_item = calcular_interpolacao(atg, st.session_state.config_faixas, multiplos_row=None)
                nota_indiv_total += nota_item * (m['Peso']/100)
            
            # 2. Buscar Regra de Múltiplos do Cargo
            row_mult = st.session_state.config_multiplos.loc[st.session_state.config_multiplos['Cargo'] == f['Cargo']].iloc[0]
            
            # 3. Calcular Múltiplo Salarial Baseado na Nota Corporativa
            # AQUI TEM UM PULO DO GATO:
            # A "Nota Corporativa" (ex: 0.85) precisa ser mapeada nas faixas para descobrir o Múltiplo (Salários)
            # Mas espera, a nota corporativa JÁ É o resultado interpolado? 
            # Se a Nota Corp Final for "0.95" (Parcial), usamos isso como input para buscar o Múltiplo.
            
            # Assumindo que a Nota Corporativa reflete o % de Atingimento Global Agregado
            # Se Nota Corp = 1.0, pagamos o Múltiplo da Meta.
            
            multiplo_final_salarial = calcular_interpolacao(nota_corp, st.session_state.config_faixas, multiplos_row=row_mult)
            
            # 4. Pro Rata
            fator_tempo = f['Tempo_Casa'] / 12
            
            # 5. Cálculo Final
            bonus_val = f['Salario'] * fator_tempo * multiplo_final_salarial * nota_indiv_total
            
            folha.append({
                "Nome": f['Nome'],
                "Cargo": f['Cargo'],
                "Salário": f['Salario'],
                "Nota Corp": nota_corp,
                "Múltiplo Alvo": multiplo_final_salarial,
                "Nota Indiv": nota_indiv_total,
                "Bônus Final": bonus_val
            })
            
        df_folha = pd.DataFrame(folha)
        st.dataframe(df_folha.style.format({
            "Salário": "R$ {:,.2f}",
            "Nota Corp": "{:.2f}",
            "Múltiplo Alvo": "{:.2f} salários",
            "Nota Indiv": "{:.2%}",
            "Bônus Final": "R$ {:,.2f}"
        }))
        
        total = df_folha['Bônus Final'].sum()
        st.metric("Custo Total do Bônus", f"R$ {total:,.2f}")
