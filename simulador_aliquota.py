
import streamlit as st
import pandas as pd

st.title("📊 Simulador de Alíquota Efetiva - Simples Nacional (Anexo III)")

st.markdown("Este simulador projeta os próximos 12 meses com base na Receita Bruta acumulada dos últimos 12 meses e no faturamento atual.")

# Entrada de dados iniciais
receita_bruta_12 = st.number_input("Receita bruta acumulada dos últimos 12 meses (incluindo o mês atual)", value=0.0, step=100.0, format="%.2f")
faturamento_atual = st.number_input("Faturamento do mês atual", value=0.0, step=100.0, format="%.2f")

if receita_bruta_12 and faturamento_atual:
    acumulado_anterior = receita_bruta_12 - faturamento_atual
    faturamento_projetado = st.number_input("Faturamento projetado para os próximos meses", value=faturamento_atual, step=100.0, format="%.2f")

    def faixa_simples(rbt12):
        if rbt12 <= 180_000:
            return 0.06, 0
        elif rbt12 <= 360_000:
            return 0.112, 9360
        elif rbt12 <= 720_000:
            return 0.135, 17640
        elif rbt12 <= 1_800_000:
            return 0.16, 35640
        elif rbt12 <= 3_600_000:
            return 0.21, 125640
        else:
            return 0.33, 648000

    projecao = []
    acumulado_atual = acumulado_anterior

    for mes in range(13):
        rotulo_mes = f"Mês {mes}" if mes != 0 else "Mês 0 (Atual)"
        receita_acumulada_antes = acumulado_atual
        receita_mes = faturamento_atual if mes == 0 else faturamento_projetado
        aliquota_nominal, deducao = faixa_simples(receita_acumulada_antes)
        if receita_acumulada_antes <= 0:
            aliquota_efetiva = aliquota_nominal
        else:
            aliquota_efetiva = ((receita_acumulada_antes * aliquota_nominal) - deducao) / receita_acumulada_antes
        imposto_mes = receita_mes * aliquota_efetiva
        projecao.append({
            "Mês": rotulo_mes,
            "Receita 12 meses anteriores": receita_acumulada_antes,
            "Receita do mês": receita_mes,
            "Alíquota Efetiva (%)": aliquota_efetiva * 100,
            "Imposto no mês": imposto_mes
        })
        acumulado_atual += receita_mes

    df_proj = pd.DataFrame(projecao)

    def formatar_moeda(valor):
        return "R$ {:,.2f}".format(valor).replace(",", "X").replace(".", ",").replace("X", ".")

    def formatar_percentual(valor):
        return f"{valor:.4f}"

    df_proj["Receita 12 meses anteriores"] = df_proj["Receita 12 meses anteriores"].apply(formatar_moeda)
    df_proj["Receita do mês"] = df_proj["Receita do mês"].apply(formatar_moeda)
    df_proj["Alíquota Efetiva (%)"] = df_proj["Alíquota Efetiva (%)"].apply(formatar_percentual)
    df_proj["Imposto no mês"] = df_proj["Imposto no mês"].apply(formatar_moeda)

    df_proj.set_index("Mês", inplace=True)
    st.markdown("## 📈 Projeção dos Próximos 12 Meses")
    st.table(df_proj)
