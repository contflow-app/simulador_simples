
import streamlit as st
import pandas as pd

st.title("📊 Simulador de Alíquota Efetiva - Simples Nacional")

# Definindo as alíquotas e deduções de cada anexo
tabelas_simples = {
    "Anexo I (Comércio)": pd.DataFrame({
        "Faixa": [1, 2, 3, 4, 5, 6],
        "Limite": [180000, 360000, 720000, 1800000, 3600000, 4800000],
        "Aliquota": [0.04, 0.073, 0.095, 0.107, 0.143, 0.19],
        "Deducao": [0, 5940, 13860, 22500, 87300, 378000]
    }),
    "Anexo II (Indústria)": pd.DataFrame({
        "Faixa": [1, 2, 3, 4, 5, 6],
        "Limite": [180000, 360000, 720000, 1800000, 3600000, 4800000],
        "Aliquota": [0.045, 0.078, 0.10, 0.112, 0.147, 0.30],
        "Deducao": [0, 5940, 13860, 22500, 85500, 720000]
    }),
    "Anexo III (Serviços)": pd.DataFrame({
        "Faixa": [1, 2, 3, 4, 5, 6],
        "Limite": [180000, 360000, 720000, 1800000, 3600000, 4800000],
        "Aliquota": [0.06, 0.112, 0.135, 0.16, 0.21, 0.33],
        "Deducao": [0, 9360, 17640, 35640, 125640, 648000]
    }),
    "Anexo IV (Serviços)": pd.DataFrame({
        "Faixa": [1, 2, 3, 4, 5, 6],
        "Limite": [180000, 360000, 720000, 1800000, 3600000, 4800000],
        "Aliquota": [0.045, 0.09, 0.102, 0.112, 0.14, 0.30],
        "Deducao": [0, 8100, 12420, 39780, 183780, 828000]
    }),
    "Anexo V (Serviços)": pd.DataFrame({
        "Faixa": [1, 2, 3, 4, 5, 6],
        "Limite": [180000, 360000, 720000, 1800000, 3600000, 4800000],
        "Aliquota": [0.15, 0.18, 0.195, 0.205, 0.23, 0.305],
        "Deducao": [0, 4500, 9900, 17100, 62100, 540000]
    })
}

# Interface
anexo_selecionado = st.selectbox("Selecione o Anexo:", list(tabelas_simples.keys()))
tabela_anexo = tabelas_simples[anexo_selecionado]

# Opção para marcar se a empresa está iniciando as atividades
empresa_iniciando = st.checkbox("Empresa está iniciando as atividades")

# Entradas principais
if empresa_iniciando:
    receita_bruta_inicial = 0.0
    st.write("Receita Bruta Inicial: R$ 0,00 (empresa em início de atividades)")
else:
    receita_bruta_inicial = st.number_input("Receita bruta acumulada dos últimos 12 meses (até o mês atual)", value=0.0, step=100.0, format="%.2f")

# Entrada de faturamento do mês atual
faturamento_mes_atual = st.number_input("Faturamento do mês atual", value=0.0, step=100.0, format="%.2f")

# Função para buscar faixa no anexo
def faixa_simples(rbt12, tabela):
    faixa = tabela[tabela["Limite"] >= rbt12].iloc[0]
    return faixa["Aliquota"], faixa["Deducao"]

# Verificação de limite do Simples Nacional
if faturamento_mes_atual * 12 > 3600000:
    st.error("⚠️ O faturamento anual projetado excede o limite do Simples Nacional (R$ 3.600.000,00).")
else:
    if empresa_iniciando:
        receita_anualizada = faturamento_mes_atual * 12
        receita_bruta_inicial = receita_anualizada
        acumulado = receita_anualizada
    else:
        receita_anualizada = receita_bruta_inicial
        acumulado = receita_bruta_inicial + faturamento_mes_atual

    projecao = []

    # Mês 0
    aliq_nom, ded = faixa_simples(receita_anualizada, tabela_anexo)
    if receita_anualizada > 0:
        aliq_eff = ((receita_anualizada * aliq_nom) - ded) / receita_anualizada
    else:
        aliq_eff = aliq_nom

    imposto = faturamento_mes_atual * aliq_eff
    projecao.append({
        "Mês": "Mês 0 (Atual)",
        "Receita Bruta Base": receita_bruta_inicial,
        "Receita do Mês": faturamento_mes_atual,
        "Alíquota Efetiva (%)": aliq_eff * 100,
        "Imposto Estimado": imposto
    })

    # Próximos 12 meses
    for i in range(1, 13):
        receita_mes = faturamento_mes_atual
        aliq_nom, ded = faixa_simples(acumulado, tabela_anexo)
        if acumulado > 0:
            aliq_eff = ((acumulado * aliq_nom) - ded) / acumulado
        else:
            aliq_eff = aliq_nom

        imposto = receita_mes * aliq_eff
        projecao.append({
            "Mês": f"Mês {i}",
            "Receita Bruta Base": acumulado,
            "Receita do Mês": receita_mes,
            "Alíquota Efetiva (%)": aliq_eff * 100,
            "Imposto Estimado": imposto
        })
        acumulado += receita_mes

    df = pd.DataFrame(projecao)

    def moeda(v): return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    def pct(v): return f"{v:.4f}"

    df["Receita Bruta Base"] = df["Receita Bruta Base"].apply(moeda)
    df["Receita do Mês"] = df["Receita do Mês"].apply(moeda)
    df["Alíquota Efetiva (%)"] = df["Alíquota Efetiva (%)"].apply(pct)
    df["Imposto Estimado"] = df["Imposto Estimado"].apply(moeda)

    df.set_index("Mês", inplace=True)
    st.markdown(f"## 📈 Projeção Mês a Mês - {anexo_selecionado}")
    st.table(df)
