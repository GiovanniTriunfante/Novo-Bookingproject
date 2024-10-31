import streamlit as st
import pandas as pd
import plotly.express as px
from gerenciamento_reservas import GerenciamentoReservas
from datetime import date, timedelta
import os
import io

def dashboard():
    st.title("Gerenciamento de Reservas")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    reservas_path = os.path.join(current_dir, "reservas.xlsx")
    parceiros_path = os.path.join(current_dir, "parceiros.xlsx")
    proprietarios_path = os.path.join(current_dir, "proprietarios.xlsx")

    reservas = GerenciamentoReservas(reservas_path, parceiros_path, proprietarios_path)

    if st.button("Recarregar Dados", key="botao_recarregar_dados"):
        reservas.df_reservas = reservas.load_data(reservas.reservas_path)
        reservas.df_parceiros = reservas.load_data(reservas.parceiros_path)
        reservas.df_proprietarios = reservas.load_data(reservas.proprietarios_path)
        st.success("Dados recarregados com sucesso!")

    exibir_relatorio_semanal(reservas)
    exibir_relatorio_parceiros(reservas)
    exibir_detalhamento_reservas(reservas)
    exibir_filtros(reservas)
    exportar_dados(reservas)

    # Organizar as seções de edição e adição em abas
    with st.container():
        tabs = st.tabs(["Editar Reservas", "Editar Parceiros", "Editar Proprietários", 
                        "Adicionar Nova Reserva", "Adicionar Novo Parceiro", "Adicionar Novo Proprietário"])

        with tabs[0]:  # Aba para editar reservas
            editar_reservas(reservas)
        with tabs[1]:  # Aba para editar parceiros
            editar_parceiros(reservas)
        with tabs[2]:  # Aba para editar proprietários
            editar_proprietarios(reservas)
        with tabs[3]:  # Aba para adicionar nova reserva
            adicionar_nova_reserva(reservas)
        with tabs[4]:  # Aba para adicionar novo parceiro
            adicionar_novo_parceiro(reservas)
        with tabs[5]:  # Aba para adicionar novo proprietário
            adicionar_novo_proprietario(reservas)

def exportar_dados(reservas):
    st.subheader("Exportação de Dados")

    # Exportar Relatório Semanal
    if st.button("Gerar Relatório Semanal", key="exportar_relatorio_semanal"):
        df_semanal, total_hospedagem, total_a_pagar, total_a_receber_parceiros, apartamentos_ocupados = reservas.calcular_totais_semanal()

        colunas_ordenadas = [
            'Nome do hóspede', 'Data de entrada', 'Data de saída', 
            'Número do apartamento', 'Valor da hospedagem', 
            'Nome do Condomínio', 'Bloco', 'Endereço'
        ]
        df_semanal = df_semanal[colunas_ordenadas]

        resumo = pd.DataFrame({
            'Descrição': ['Total Hospedagem', 'Total a Pagar', 'Total a Receber', 'Apartamentos Ocupados'],
            'Valores': [total_hospedagem, total_a_pagar, total_a_receber_parceiros, apartamentos_ocupados]
        })

        output = io.StringIO()
        resumo.to_csv(output, index=False)
        output.write("\n")
        df_semanal.to_csv(output, index=False, float_format="%.2f")
        csv_data = output.getvalue().encode('utf-8')

        st.download_button(
            label="Baixar Relatório Semanal como CSV",
            data=csv_data,
            file_name="relatorio_semanal_formatado.csv",
            mime="text/csv"
        )

    # Exportar Relatório de Parceiros
    if st.button("Gerar Relatório de Parceiros", key="exportar_relatorio_parceiros"):
        df_parceiros, total_a_receber, total_a_pagar = reservas.gerar_relatorio_parceiros()

        resumo_parceiros = pd.DataFrame({
            'Descrição': ['Total a Receber', 'Total a Pagar'],
            'Valores': [total_a_receber, total_a_pagar]
        })

        output_parceiros = io.StringIO()
        resumo_parceiros.to_csv(output_parceiros, index=False)
        output_parceiros.write("\n")
        df_parceiros[['Parceiro', 'A receber', 'A pagar']].to_csv(output_parceiros, index=False, float_format="%.2f")
        csv_data_parceiros = output_parceiros.getvalue().encode('utf-8')

        st.download_button(
            label="Baixar Relatório de Parceiros como CSV",
            data=csv_data_parceiros,
            file_name="relatorio_parceiros_formatado.csv",
            mime="text/csv"
        )

    # Exportar Relatório de Proprietários
    if st.button("Gerar Relatório de Proprietários", key="exportar_relatorio_proprietarios"):
        total_a_pagar = reservas.df_proprietarios['A pagar'].sum() if 'A pagar' in reservas.df_proprietarios.columns else 0

        resumo_proprietarios = pd.DataFrame({
            'Descrição': ['Total a Pagar aos Proprietários'],
            'Valores': [total_a_pagar]
        })

        output_proprietarios = io.StringIO()
        resumo_proprietarios.to_csv(output_proprietarios, index=False)
        output_proprietarios.write("\n")
        df_proprietarios = reservas.df_proprietarios[['Nome Completo', 'Email', 'Telefone', 'Documento']]
        if 'A pagar' in reservas.df_proprietarios.columns:
            df_proprietarios['A pagar'] = reservas.df_proprietarios['A pagar']
        
        df_proprietarios.to_csv(output_proprietarios, index=False, float_format="%.2f")
        csv_data_proprietarios = output_proprietarios.getvalue().encode('utf-8')

        st.download_button(
            label="Baixar Relatório de Proprietários como CSV",
            data=csv_data_proprietarios,
            file_name="relatorio_proprietarios_formatado.csv",
            mime="text/csv"
        )

def exibir_relatorio_semanal(reservas):
    st.subheader("Relatório Semanal")
    df_semanal, total_hospedagem, total_a_pagar, total_a_receber_parceiros, apartamentos_ocupados = reservas.calcular_totais_semanal()
    
    st.write("**Valor total da hospedagem:**", total_hospedagem)
    st.write("**Total a pagar ao proprietário:**", total_a_pagar)
    st.write("**Total a receber dos parceiros:**", total_a_receber_parceiros)
    st.write("**Número de apartamentos ocupados na semana:**", apartamentos_ocupados)

    grafico_df = pd.DataFrame({
        'Descrição': ['Total Hospedagem', 'Total a Pagar', 'Total a Receber'],
        'Valores': [total_hospedagem, total_a_pagar, total_a_receber_parceiros]
    })
    fig = px.bar(grafico_df, x='Descrição', y='Valores', title="Totais Semanais")
    st.plotly_chart(fig)

def exibir_relatorio_parceiros(reservas):
    st.subheader("Relatório de Parceiros")
    df_parceiros, total_a_receber, total_a_pagar = reservas.gerar_relatorio_parceiros()

    st.write("**Total a receber dos parceiros:**", total_a_receber)
    st.write("**Total a pagar aos parceiros:**", total_a_pagar)
    st.write("**Resumo por Parceiro:**")
    st.dataframe(df_parceiros)

    fig = px.bar(df_parceiros, x='Parceiro', y=['A receber', 'A pagar'], title="Valores a Receber e Pagar por Parceiro")
    st.plotly_chart(fig)

def exibir_detalhamento_reservas(reservas):
    st.subheader("Detalhes das Reservas Semanais")
    df_semanal, *_ = reservas.calcular_totais_semanal()
    st.dataframe(df_semanal[['Nome do hóspede', 'Data de entrada', 'Data de saída', 
                             'Número do apartamento', 'Valor da hospedagem',
                             'Nome do Condomínio', 'Bloco', 'Endereço']])

def exibir_filtros(reservas):
    st.sidebar.header("Filtros de Reservas")
    nome_hospede = st.sidebar.text_input("Nome do Hóspede", key="filtro_nome_hospede")
    numero_apartamento = st.sidebar.number_input("Número do Apartamento", min_value=0, step=1, key="filtro_numero_apartamento")
    data_inicial = st.sidebar.date_input("Data de Entrada (inicial)", date.today() - timedelta(days=30), key="filtro_data_inicial")
    data_final = st.sidebar.date_input("Data de Entrada (final)", date.today(), key="filtro_data_final")

    df_filtrado = reservas.df_reservas.copy()
    if nome_hospede:
        df_filtrado = df_filtrado[df_filtrado['Nome do hóspede'].str.contains(nome_hospede, case=False)]
    if numero_apartamento > 0:
        df_filtrado = df_filtrado[df_filtrado['Número do apartamento'] == numero_apartamento]
    df_filtrado = df_filtrado[(df_filtrado['Data de entrada'] >= pd.Timestamp(data_inicial)) & 
                              (df_filtrado['Data de entrada'] <= pd.Timestamp(data_final))]

    st.subheader("Reservas Filtradas")
    st.dataframe(df_filtrado[['Nome do hóspede', 'Data de entrada', 'Data de saída', 
                              'Número do apartamento', 'Valor da hospedagem',
                              'Nome do Condomínio', 'Bloco', 'Endereço']])

def editar_reservas(reservas):
    st.subheader("Editar Reservas")
    id_reserva = st.selectbox("Selecione a Reserva para Editar", reservas.df_reservas.index, key="select_reserva_editar")
    reserva_selecionada = reservas.df_reservas.loc[id_reserva]

    nome = st.text_input("Nome do Hóspede", reserva_selecionada['Nome do hóspede'], key="editar_nome_hospede")
    data_entrada = st.date_input("Data de Entrada", reserva_selecionada['Data de entrada'], key="editar_data_entrada")
    data_saida = st.date_input("Data de Saída", reserva_selecionada['Data de saída'], key="editar_data_saida")
    numero_apartamento = st.number_input("Número do Apartamento", value=int(reserva_selecionada['Número do apartamento']), key="editar_numero_apartamento")
    valor_hospedagem = st.number_input("Valor da Hospedagem", value=float(reserva_selecionada['Valor da hospedagem']), key="editar_valor_hospedagem")
    condominio = st.text_input("Nome do Condomínio", reserva_selecionada.get('Nome do Condomínio', ''), key="editar_condominio")
    bloco = st.text_input("Bloco", reserva_selecionada.get('Bloco', ''), key="editar_bloco")
    endereco = st.text_input("Endereço", reserva_selecionada.get('Endereço', ''), key="editar_endereco")

    if st.button("Salvar Alterações", key="salvar_alteracoes_reserva"):
        reservas.atualizar_reserva(id_reserva, nome, data_entrada, data_saida, numero_apartamento, valor_hospedagem, condominio, bloco, endereco)
        st.success("Reserva atualizada com sucesso!")

def editar_parceiros(reservas):
    st.subheader("Editar Parceiros")
    id_parceiro = st.selectbox("Selecione o Parceiro para Editar", reservas.df_parceiros.index, key="select_parceiro_editar")
    parceiro_selecionado = reservas.df_parceiros.loc[id_parceiro]

    parceiro = st.text_input("Nome do Parceiro", parceiro_selecionado['Parceiro'], key="editar_nome_parceiro")
    a_receber = st.number_input("A Receber", value=float(parceiro_selecionado['A receber']), key="editar_a_receber")
    a_pagar = st.number_input("A Pagar", value=float(parceiro_selecionado['A pagar']), key="editar_a_pagar")

    if st.button("Salvar Alterações no Parceiro", key="salvar_alteracoes_parceiro"):
        reservas.atualizar_parceiro(id_parceiro, parceiro, a_receber, a_pagar)
        st.success("Parceiro atualizado com sucesso!")

def editar_proprietarios(reservas):
    st.subheader("Editar Proprietários")
    id_proprietario = st.selectbox("Selecione o Proprietário para Editar", reservas.df_proprietarios.index, key="select_proprietario_editar")
    proprietario_selecionado = reservas.df_proprietarios.loc[id_proprietario]

    nome = st.text_input("Nome Completo", proprietario_selecionado['Nome Completo'], key="editar_nome_proprietario")
    email = st.text_input("Email", proprietario_selecionado['Email'], key="editar_email_proprietario")
    telefone = st.text_input("Telefone", proprietario_selecionado['Telefone'], key="editar_telefone_proprietario")
    documento = st.text_input("Documento", proprietario_selecionado['Documento'], key="editar_documento_proprietario")

    if st.button("Salvar Alterações no Proprietário", key="salvar_alteracoes_proprietario"):
        reservas.atualizar_proprietario(id_proprietario, nome, email, telefone, documento)
        st.success("Proprietário atualizado com sucesso!")

# Funções de Adicionar com Expansores
def adicionar_novo_parceiro(reservas):
    with st.expander("Adicionar Novo Parceiro"):
        parceiro = st.text_input("Nome do Parceiro", key="novo_nome_parceiro")
        a_receber = st.number_input("A Receber", min_value=0.0, step=0.01, key="novo_a_receber_parceiro")
        a_pagar = st.number_input("A Pagar", min_value=0.0, step=0.01, key="novo_a_pagar_parceiro")

        if st.button("Adicionar Parceiro", key="botao_adicionar_parceiro"):
            reservas.adicionar_parceiro(parceiro, a_receber, a_pagar)
            st.success("Novo parceiro adicionado com sucesso!")
            reservas.df_parceiros = reservas.load_data(reservas.parceiros_path)

def adicionar_novo_proprietario(reservas):
    with st.expander("Adicionar Novo Proprietário"):
        nome = st.text_input("Nome Completo", key="novo_nome_proprietario")
        email = st.text_input("Email", key="novo_email_proprietario")
        telefone = st.text_input("Telefone", key="novo_telefone_proprietario")
        documento = st.text_input("Documento", key="novo_documento_proprietario")

        if st.button("Adicionar Proprietário", key="botao_adicionar_proprietario"):
            reservas.adicionar_proprietario(nome, email, telefone, documento)
            st.success("Novo proprietário adicionado com sucesso!")
            reservas.df_proprietarios = reservas.load_data(reservas.proprietarios_path)

def adicionar_nova_reserva(reservas):
    with st.expander("Adicionar Nova Reserva"):
        nome = st.text_input("Nome do Hóspede", key="nome_hospede")
        data_entrada = st.date_input("Data de Entrada", date.today(), key="data_entrada")
        data_saida = st.date_input("Data de Saída", date.today() + timedelta(days=1), key="data_saida")
        numero_apartamento = st.number_input("Número do Apartamento", min_value=1, step=1, key="numero_apartamento")
        valor_hospedagem = st.number_input("Valor da Hospedagem", min_value=0.0, step=0.01, key="valor_hospedagem")
        condominio = st.text_input("Nome do Condomínio", key="condominio")
        bloco = st.text_input("Bloco", key="bloco")
        endereco = st.text_input("Endereço", key="endereco")

        if st.button("Adicionar Reserva", key="botao_adicionar_reserva"):
            reservas.adicionar_reserva(nome, data_entrada, data_saida, numero_apartamento, valor_hospedagem, condominio, bloco, endereco)
            st.success("Nova reserva adicionada com sucesso!")
            reservas.df_reservas = reservas.load_data(reservas.reservas_path)

if __name__ == "__main__":
    dashboard()
