
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Inicializando valores
if "receita_acumulada" not in st.session_state:
    st.session_state.receita_acumulada = None

# Função para identificar a faixa do Simples Nacional Anexo III
def faixa_simples(receita):
    if receita <= 180000:
        return "Faixa 1 (4%)", 0.04, 0
    elif receita <= 360000:
        return "Faixa 2 (7.3%)", 0.073, 5940
    elif receita <= 720000:
        return "Faixa 3 (9.5%)", 0.095, 13860
    elif receita <= 1800000:
        return "Faixa 4 (10.7%)", 0.107, 22500
    elif receita <= 3600000:
        return "Faixa 5 (14.3%)", 0.143, 87300
    else:
        return "Fora do Anexo III", 0, 0

def aliquota_efetiva(receita, faturamento_mes):
    faixa, aliquota_nominal, parcela_deduzir = faixa_simples(receita)
    if aliquota_nominal == 0:
        return faixa, 0
    efetiva = ((receita * aliquota_nominal) - parcela_deduzir) / receita
    return faixa, efetiva

# Interface do usuário
st.title("📊 Simulador de Receita e Alíquota - Simples Nacional (Anexo III)")
st.markdown("Este simulador ajuda você a acompanhar a **receita bruta acumulada** e fazer projeções de faturamento para os próximos meses.")

# Solicitar receita acumulada no primeiro uso
if st.session_state.receita_acumulada is None:
    receita_inicial = st.number_input("Digite a Receita Bruta Acumulada dos últimos 12 meses:", min_value=0.0, step=100.0)
    if st.button("Salvar Receita Inicial"):
        st.session_state.receita_acumulada = receita_inicial
        st.success(f"Receita inicial registrada: R$ {receita_inicial:.2f}")
else:
    st.markdown(f"### Receita Acumulada Atual: R$ {st.session_state.receita_acumulada:,.2f}")
    faixa_atual, aliq_efetiva = aliquota_efetiva(st.session_state.receita_acumulada, 0)
    st.info(f"Faixa atual: **{faixa_atual}** | Alíquota efetiva estimada: **{aliq_efetiva*100:.2f}%**")

    # Entrada de faturamento mensal
    faturamento_mes = st.number_input("Digite o faturamento do mês:", min_value=0.0, step=100.0)
    if st.button("Atualizar Receita Acumulada"):
        st.session_state.receita_acumulada += faturamento_mes
        st.success(f"Nova Receita Acumulada: R$ {st.session_state.receita_acumulada:.2f}")
        st.experimental_rerun()

    # Gerar projeção dos próximos meses
    faturamento_medio = st.number_input("Digite o faturamento médio mensal para projeção:", min_value=0.0, step=100.0)
    if st.button("Gerar Projeção"):
        projecao = []
        receita_projetada = st.session_state.receita_acumulada
        for i in range(6):
            receita_projetada += faturamento_medio
            faixa_proj, aliq_efetiva_proj = aliquota_efetiva(receita_projetada, faturamento_medio)
            projecao.append((i + 1, receita_projetada, faixa_proj, f"{aliq_efetiva_proj*100:.2f}%"))

        # Exibir tabela de projeção
        df_projecao = pd.DataFrame(projecao, columns=["Mês", "Receita Bruta Projetada", "Faixa", "Alíquota Efetiva"])
        df_projecao["Receita Bruta Projetada"] = df_projecao["Receita Bruta Projetada"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.write("Projeção dos Próximos 6 Meses:")
        st.dataframe(df_projecao)

        # Gerar gráfico da evolução do faturamento
        fig, ax = plt.subplots()
        valores_receita = [float(str(valor).replace("R$", "").replace(".", "").replace(",", ".")) for valor in df_projecao["Receita Bruta Projetada"]]
        ax.plot(df_projecao["Mês"], valores_receita, marker='o', linestyle='-', label="Projeção Receita Acumulada")
        ax.set_title("Projeção de Receita Bruta para os Próximos 6 Meses")
        ax.set_xlabel("Mês")
        ax.set_ylabel("Receita Bruta (R$)")
        ax.legend()
        st.pyplot(fig)

    if st.button("Redefinir Receita Acumulada"):
        st.session_state.receita_acumulada = None
        st.experimental_rerun()
