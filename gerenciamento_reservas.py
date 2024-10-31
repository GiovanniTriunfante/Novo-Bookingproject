import pandas as pd
from datetime import date, timedelta
import os

class GerenciamentoReservas:
    def __init__(self, reservas_path, parceiros_path, proprietarios_path):
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Caminhos para os arquivos
        self.reservas_path = os.path.join(current_dir, reservas_path)
        self.parceiros_path = os.path.join(current_dir, parceiros_path)
        self.proprietarios_path = os.path.join(current_dir, proprietarios_path)
        
        # Carregar dados das planilhas
        self.df_reservas = self.load_data(self.reservas_path)
        self.df_parceiros = self.load_data(self.parceiros_path)
        self.df_proprietarios = self.load_data(self.proprietarios_path)

    def load_data(self, file_path):
        """Carrega dados de uma planilha Excel e retorna um DataFrame."""
        try:
            df = pd.read_excel(file_path)
            print(f"Colunas carregadas de {file_path}: {df.columns.tolist()}")
            return df
        except FileNotFoundError:
            print(f"Erro: O arquivo '{file_path}' não foi encontrado.")
            return pd.DataFrame()
        except Exception as e:
            print(f"Erro ao carregar '{file_path}': {e}")
            return pd.DataFrame()

    def save_to_excel(self, df, file_path):
        """Método centralizado para salvar DataFrames no formato Excel."""
        try:
            df.to_excel(file_path, index=False)
            print(f"Arquivo salvo com sucesso em: {file_path}")
        except Exception as e:
            print(f"Erro ao salvar arquivo Excel: {e}")

    def adicionar_reserva(self, nome, data_entrada, data_saida, numero_apartamento, 
                          valor_hospedagem, condominio, bloco, endereco, status):
        """Adiciona uma nova reserva e salva no Excel diretamente no DataFrame."""
        new_data = pd.DataFrame({
            'Nome do hóspede': [nome],
            'Data de entrada': [data_entrada],
            'Data de saída': [data_saida],
            'Número do apartamento': [numero_apartamento],
            'Valor da hospedagem': [valor_hospedagem],
            'Nome do Condomínio': [condominio],
            'Bloco': [bloco],
            'Endereço': [endereco],
            'Status': [status]
        })
        self.df_reservas = pd.concat([self.df_reservas, new_data], ignore_index=True)
        self.save_to_excel(self.df_reservas, self.reservas_path)

    def atualizar_reserva(self, id_reserva, nome, data_entrada, data_saida, numero_apartamento, 
                          valor_hospedagem, condominio, bloco, endereco, status):
        """Atualiza uma reserva específica no DataFrame e salva no Excel."""
        if id_reserva in self.df_reservas.index:
            self.df_reservas.at[id_reserva, 'Nome do hóspede'] = nome
            self.df_reservas.at[id_reserva, 'Data de entrada'] = data_entrada
            self.df_reservas.at[id_reserva, 'Data de saída'] = data_saida
            self.df_reservas.at[id_reserva, 'Número do apartamento'] = numero_apartamento
            self.df_reservas.at[id_reserva, 'Valor da hospedagem'] = valor_hospedagem
            self.df_reservas.at[id_reserva, 'Nome do Condomínio'] = condominio
            self.df_reservas.at[id_reserva, 'Bloco'] = bloco
            self.df_reservas.at[id_reserva, 'Endereço'] = endereco
            self.df_reservas.at[id_reserva, 'Status'] = status
            self.save_to_excel(self.df_reservas, self.reservas_path)
        else:
            print(f"Reserva com ID {id_reserva} não encontrada.")

    def adicionar_parceiro(self, parceiro, a_receber, a_pagar):
        """Adiciona um novo parceiro e salva no arquivo Excel diretamente no DataFrame."""
        new_data = pd.DataFrame({
            'Parceiro': [parceiro],
            'A receber': [a_receber],
            'A pagar': [a_pagar]
        })
        self.df_parceiros = pd.concat([self.df_parceiros, new_data], ignore_index=True)
        self.save_to_excel(self.df_parceiros, self.parceiros_path)

    def atualizar_parceiro(self, id_parceiro, parceiro, a_receber, a_pagar):
        """Atualiza um parceiro específico no DataFrame e salva no Excel."""
        if id_parceiro in self.df_parceiros.index:
            self.df_parceiros.at[id_parceiro, 'Parceiro'] = parceiro
            self.df_parceiros.at[id_parceiro, 'A receber'] = a_receber
            self.df_parceiros.at[id_parceiro, 'A pagar'] = a_pagar
            self.save_to_excel(self.df_parceiros, self.parceiros_path)
        else:
            print(f"Parceiro com ID {id_parceiro} não encontrado.")

    def adicionar_proprietario(self, nome, email, telefone, documento):
        """Adiciona um novo proprietário e salva no arquivo Excel diretamente no DataFrame."""
        new_data = pd.DataFrame({
            'Nome Completo': [nome],
            'Email': [email],
            'Telefone': [telefone],
            'Documento': [documento]
        })
        self.df_proprietarios = pd.concat([self.df_proprietarios, new_data], ignore_index=True)
        self.save_to_excel(self.df_proprietarios, self.proprietarios_path)

    def atualizar_proprietario(self, id_proprietario, nome, email, telefone, documento):
        """Atualiza um proprietário específico no DataFrame e salva no Excel."""
        if id_proprietario in self.df_proprietarios.index:
            self.df_proprietarios.at[id_proprietario, 'Nome Completo'] = nome
            self.df_proprietarios.at[id_proprietario, 'Email'] = email
            self.df_proprietarios.at[id_proprietario, 'Telefone'] = telefone
            self.df_proprietarios.at[id_proprietario, 'Documento'] = documento
            self.save_to_excel(self.df_proprietarios, self.proprietarios_path)
        else:
            print(f"Proprietário com ID {id_proprietario} não encontrado.")

    def calcular_saldos(self):
        """Calcula saldos de receitas e despesas totais das reservas e parceiros."""
        if not self.check_columns(self.df_reservas, ['Valor da hospedagem']) or \
           not self.check_columns(self.df_parceiros, ['A receber', 'A pagar']):
            return None

        total_receitas = self.df_reservas['Valor da hospedagem'].sum()
        total_a_receber_parceiros = self.df_parceiros['A receber'].sum()
        total_a_pagar_parceiros = self.df_parceiros['A pagar'].sum()
        
        return {
            'total_receitas': total_receitas,
            'total_a_receber_parceiros': total_a_receber_parceiros,
            'total_a_pagar_parceiros': total_a_pagar_parceiros
        }

    def calcular_totais_semanal(self):
        """Calcula totais semanais de hospedagem, valores a pagar e a receber, e apartamentos ocupados."""
        hoje = pd.Timestamp(date.today())
        uma_semana_atras = pd.Timestamp(date.today() - timedelta(days=7))
        
        df_semanal = self.df_reservas[
            (self.df_reservas['Data de entrada'] >= uma_semana_atras) & 
            (self.df_reservas['Data de entrada'] <= hoje)
        ]
        
        total_hospedagem = df_semanal['Valor da hospedagem'].sum()
        total_a_pagar = self.df_proprietarios['A pagar'].sum() if 'A pagar' in self.df_proprietarios.columns else 0
        total_a_receber_parceiros = self.df_parceiros['A receber'].sum() if 'A receber' in self.df_parceiros.columns else 0
        apartamentos_ocupados = df_semanal['Número do apartamento'].nunique()
        
        return df_semanal, total_hospedagem, total_a_pagar, total_a_receber_parceiros, apartamentos_ocupados

    def gerar_relatorio_parceiros(self):
        """Gera um relatório dos parceiros com totais a receber e a pagar."""
        if not self.check_columns(self.df_parceiros, ['A receber', 'A pagar']):
            return pd.DataFrame(), 0, 0

        total_a_receber = self.df_parceiros['A receber'].sum()
        total_a_pagar = self.df_parceiros['A pagar'].sum()
        return self.df_parceiros, total_a_receber, total_a_pagar

    def check_columns(self, df, required_columns):
        """Verifica se as colunas necessárias estão presentes no DataFrame."""
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Erro: As seguintes colunas estão ausentes: {missing_columns}")
            return False
        return True
