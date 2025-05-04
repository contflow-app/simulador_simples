
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import deque

# Tabela oficial Anexo III - Simples Nacional
tabela_simples = pd.DataFrame({
    "Faixa": [1, 2, 3, 4, 5, 6],
    "Limite": [180000, 360000, 720000, 1800000, 3600000, 4800000],
    "Aliquota": [0.06, 0.112, 0.135, 0.16, 0.21, 0.33],
    "Deducao": [0, 9360, 17640, 35640, 125640, 648000]
})

# Inicializa a lista de receitas mensais com no máximo 12 valores
if "receitas" not in st.session_state:
    st.session_state.receitas = deque(maxlen=12)

st.title("📊 Simulador de Alíquota Efetiva - Simples Nacional (Anexo III)")
st.markdown("Este simulador calcula a **alíquota efetiva** com base na receita acumulada dos últimos 12 meses. Você também pode simular os próximos meses.")

st.markdown("## Etapa 1: Insira a Receita do Mês Atual")
receita_mes = st.number_input("Receita bruta do mês atual (R$):", min_value=0.0, step=100.0)
if st.button("Adicionar Receita do Mês"):
    st.session_state.receitas.append(receita_mes)
    st.success(f"Receita de R$ {receita_mes:,.2f} adicionada com sucesso!")

# Cálculo da receita acumulada
acumulado = sum(st.session_state.receitas)
faixa = tabela_simples[tabela_simples["Limite"] >= acumulado].iloc[0]
aliquota_efetiva = ((acumulado * faixa["Aliquota"]) - faixa["Deducao"]) / acumulado if acumulado > 0 else 0

st.markdown("## Resultado do Mês Atual")
st.write(f"Receita Bruta Acumulada (últimos 12 meses): **R$ {acumulado:,.2f}**")
st.write(f"Faixa: **{faixa['Faixa']}**")
st.write(f"Alíquota Nominal: **{faixa['Aliquota'] * 100:.2f}%**")
st.write(f"Parcela a Deduzir: **R$ {faixa['Deducao']:,.2f}**")
st.success(f"**Alíquota Efetiva Aplicável: {aliquota_efetiva * 100:.2f}%**")

# Etapa opcional: projeção
st.markdown("## Etapa Opcional: Simule os Próximos Meses")
faturamento_medio = st.number_input("Faturamento médio mensal para projeção (R$):", min_value=0.0, step=100.0)
if st.button("Gerar Projeção dos Próximos 6 Meses"):
    receitas_futuras = list(st.session_state.receitas)
    projecao = []

    for i in range(6):
        receitas_futuras.append(faturamento_medio)
        receitas_futuras = receitas_futuras[-12:]
        acumulado_proj = sum(receitas_futuras)
        faixa_proj = tabela_simples[tabela_simples["Limite"] >= acumulado_proj].iloc[0]
        aliq_efetiva_proj = ((acumulado_proj * faixa_proj["Aliquota"]) - faixa_proj["Deducao"]) / acumulado_proj
        projecao.append((f"Mês {i+1}", acumulado_proj, aliq_efetiva_proj * 100))

    df_proj = pd.DataFrame(projecao, columns=["Mês", "Receita Bruta Acumulada", "Alíquota Efetiva (%)"])
    df_proj["Receita Bruta Acumulada"] = df_proj["Receita Bruta Acumulada"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.write("📈 Projeção para os Próximos 6 Meses:")
    st.dataframe(df_proj)

    fig, ax = plt.subplots()
    ax.plot(range(1, 7), [p[2] for p in projecao], marker='o')
    ax.set_xlabel("Mês")
    ax.set_ylabel("Alíquota Efetiva (%)")
    ax.set_title("Projeção da Alíquota Efetiva")
    st.pyplot(fig)

# Redefinir tudo
if st.button("🔄 Limpar histórico"):
    st.session_state.receitas.clear()
    st.success("Histórico de receitas zerado.")
