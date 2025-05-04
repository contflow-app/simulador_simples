
import streamlit as st
import pandas as pd

# Título da aplicação
st.header("Projeção dos Próximos 12 Meses")

# Explicação inicial
st.markdown("Mês **0** representa o mês atual já exibido no cálculo principal. As linhas seguintes (Mês 1, Mês 2, ...) correspondem aos meses futuros projetados.")
st.markdown(
    """
    **Descrição das colunas da tabela:**
    - **Receita 12 meses anteriores:** soma do faturamento dos 12 meses anteriores ao mês projetado (antes de incluir a receita do mês em questão).
    - **Receita do mês:** faturamento bruto projetado para o mês em questão.
    - **Alíquota Efetiva:** alíquota efetiva do Simples Nacional recalculada de acordo com o novo faturamento acumulado (incluindo o mês projetado).
    - **Imposto no mês:** valor estimado do imposto (Simples Nacional) a ser pago no mês, calculado como **Receita do mês × Alíquota Efetiva**.
    """
)

# Entrada de dados (poderiam já ter sido calculados anteriormente no app):
# Receita bruta total dos últimos 12 meses (incluindo o mês atual)
receita_bruta_12 = st.number_input("Receita bruta acumulada dos últimos 12 meses (incluindo o mês atual)", value=0.0, step=1e3, format="%.2f")
# Faturamento do mês atual
faturamento_atual = st.number_input("Faturamento do mês atual", value=0.0, step=1e3, format="%.2f")

# Verifica se os valores iniciais foram informados
if receita_bruta_12 and faturamento_atual:
    # Calcula o faturamento acumulado dos 12 meses anteriores (antes do mês atual)
    acumulado_anterior = receita_bruta_12 - faturamento_atual

    # Entrada para o faturamento projetado mensal (considerando um valor constante para simplicidade)
    faturamento_projetado = st.number_input(
        "Faturamento projetado para os próximos meses (valor mensal constante)",
        value=faturamento_atual, step=1e3, format="%.2f"
    )

    # Entrada para quantidade de meses a projetar (incluindo o mês atual)
    meses_projecao = st.slider("Meses de projeção (incluindo o mês atual)", min_value=1, max_value=24, value=12)

    # Função para obter a alíquota nominal e dedução da faixa do Simples (Anexo III)
    def faixa_simples(rbt12):
        if rbt12 <= 180_000:
            return 0.06, 0       # Faixa 1: até 180.000,00 – 6.00% (dedução 0)
        elif rbt12 <= 360_000:
            return 0.112, 9_360  # Faixa 2: até 360.000,00 – 11.20% (dedução 9.360)
        elif rbt12 <= 720_000:
            return 0.135, 17_640 # Faixa 3: até 720.000,00 – 13.50% (dedução 17.640)
        elif rbt12 <= 1_800_000:
            return 0.16, 35_640  # Faixa 4: até 1.800.000,00 – 16.00% (dedução 35.640)
        elif rbt12 <= 3_600_000:
            return 0.21, 125_640 # Faixa 5: até 3.600.000,00 – 21.00% (dedução 125.640)
        else:
            return 0.33, 648_000 # Faixa 6: acima de 3.600.000,00 – 33.00% (dedução 648.000)

    # Lista para armazenar os resultados de cada mês
    projecao = []
    acumulado_atual = acumulado_anterior  # começamos com o acumulado antes do mês 0

    for mes in range(meses_projecao):
        # Determina o rótulo do mês (Mês 0, Mês 1, ...)
        rotulo_mes = f"Mês {mes}" if mes != 0 else "Mês 0 (Atual)"
        # Receita acumulada dos 12 meses anteriores ao mês
        receita_acumulada_antes = acumulado_atual
        # Receita do mês projetado
        receita_mes = faturamento_atual if mes == 0 else faturamento_projetado

        # Obtém a alíquota nominal e a dedução correspondentes à faixa do Simples
        aliquota_nominal, deducao = faixa_simples(receita_acumulada_antes)
        # Calcula a alíquota efetiva do Simples Nacional para o novo acumulado
        # (Se o acumulado anterior for 0, consideramos a alíquota nominal diretamente para evitar divisão por zero)
        if receita_acumulada_antes <= 0:
            aliquota_efetiva = aliquota_nominal
        else:
            aliquota_efetiva = ((receita_acumulada_antes * aliquota_nominal) - deducao) / receita_acumulada_antes

        # Calcula o valor estimado do imposto no mês
        imposto_mes = receita_mes * aliquota_efetiva

        # Armazena os resultados deste mês na lista
        projecao.append({
            "Mês": rotulo_mes,
            "Receita 12 meses anteriores": receita_acumulada_antes,
            "Receita do mês": receita_mes,
            "Alíquota Efetiva (%)": aliquota_efetiva * 100,  # em porcentagem
            "Imposto no mês": imposto_mes
        })

        # Atualiza o acumulado atual adicionando a receita do mês (para usar no próximo mês projetado)
        acumulado_atual += receita_mes

    # Converte a lista de projeção em DataFrame para formatação
    df_projecao = pd.DataFrame(projecao)

    # Funções auxiliares para formatar os valores monetários e percentuais
    def formatar_moeda(valor):
        return "R$ {:,.2f}".format(valor).replace(",", "X").replace(".", ",").replace("X", ".")

    def formatar_percentual(valor):
        return f"{valor:.4f}"

    # Aplica a formatação desejada
    df_projecao["Receita 12 meses anteriores"] = df_projecao["Receita 12 meses anteriores"].apply(formatar_moeda)
    df_projecao["Receita do mês"] = df_projecao["Receita do mês"].apply(formatar_moeda)
    df_projecao["Alíquota Efetiva (%)"] = df_projecao["Alíquota Efetiva (%)"].apply(formatar_percentual)
    df_projecao["Imposto no mês"] = df_projecao["Imposto no mês"].apply(formatar_moeda)

    # Define a coluna "Mês" como índice para exibição (opcional, para melhorar apresentação)
    df_projecao.set_index("Mês", inplace=True)

    # Exibe a tabela de projeção formatada
    st.table(df_projecao)