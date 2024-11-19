import matplotlib.pyplot as plt
import pandas as pd
from django.core.management.base import BaseCommand
from myapp.models import Notifications

class Command(BaseCommand):
    help = 'Run APC analysis and generate continuous graph from 2022 to 2024'

    def handle(self, *args, **kwargs):
        # Extrair dados de Notifications
        dados = Notifications.objects.all().values(
            'notification_id', 'disease', 'region', 
            'notification_week', 'notification_year', 
            'cases_confirmed'
        )

        # Converter para um DataFrame
        df_dados = pd.DataFrame(dados)
        
        # Agrupar por semana e somar os casos confirmados
        df_semana = df_dados.groupby(['notification_year', 'notification_week']).agg(
            total_cases=('cases_confirmed', 'sum')
        ).reset_index()

        # Criar uma coluna 'week_number' para representar as semanas de forma contínua
        df_semana['week_number'] = (df_semana['notification_year'] - 2022) * 52 + df_semana['notification_week']

        # Exibir o DataFrame resultante com semanas contínuas e casos confirmados
        print("DataFrame com semanas contínuas:")
        print(df_semana[['week_number', 'total_cases']])

        # Gerar o gráfico
        plt.figure(figsize=(14, 7))
        plt.plot(df_semana['week_number'], df_semana['total_cases'], marker='o', color='b', label='Casos Confirmados')

        # Personalizar o gráfico
        plt.title('Casos Confirmados por Semana (2022 - 2024)', fontsize=14)
        plt.xlabel('Semana (2022 - 2024)', fontsize=12)
        plt.ylabel('Casos Confirmados', fontsize=12)
        plt.grid(True)

        # Adicionar marcas de semana no eixo X
        # Definir a cada 10 semanas uma marca no eixo X para evitar sobrecarga visual
        ticks = df_semana['week_number'][::10]  # Pega cada 10ª semana
        labels = [f"{year}-W{week}" for year, week in zip(df_semana['notification_year'][::10], df_semana['notification_week'][::10])]
        
        plt.xticks(ticks=ticks, labels=labels, rotation=45, ha='right')

        # Exibir o gráfico
        plt.legend()
        plt.show()
