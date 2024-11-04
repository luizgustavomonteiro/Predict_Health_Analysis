from django.core.management.base import BaseCommand
import pandas as pd 
import numpy as np
from scipy.stats import linregress
from myapp.models import Notifications

class Command(BaseCommand):
    help = 'Run APC analysis'

    def handle(self, *args, **kwargs):
        limite_apc = 10
        # Extrair dados de Notifications
        dados = Notifications.objects.all().values(
            'notification_id', 'disease', 'region', 
            'notification_week', 'notification_year', 
            'cases_confirmed'
        )

        # Converter para um DataFrame
        df_dados = pd.DataFrame(dados)

        # Agrupar os dados por região e doença
        segments = df_dados.groupby(['region', 'disease'])

        # Calcular APC
        results = self.calc_apc(segments, limite_apc)

        # Exibir os resultados
        print(results)

    def calc_apc(self, segments, limite_apc):
        results = []
        for (region, disease), segment in segments:
            if len(segment) > 1 and segment['cases_confirmed'].notnull().all():
                x = np.arange(len(segment))
                y = segment['cases_confirmed'].values

                slope, intercept, r_value, p_value, std_err = linregress(x, np.log(y))
                apc = (np.exp(slope) - 1) * 100
                duration = segment['notification_week'].iloc[-1] - segment['notification_week'].iloc[0] + 1

                # Emitir alerta se o APC ultrapassar o limite
                if apc > limite_apc:
                    print(f"Alerta! O APC na região {region} para a doença {disease} ultrapassou o limite de {limite_apc}% com um valor de {apc:.2f}%.")
                
                # Adicionar resultados na lista
                results.append({
                    'region': region,
                    'Disease': disease,
                    'Slope Log': slope,
                    'APC (%)': apc,
                    'Intercept': intercept,
                    'R-squared': r_value ** 2,
                    'P-value': p_value,
                    'Std Err': std_err,
                    'Início': segment['notification_week'].iloc[0],
                    'Fim': segment['notification_week'].iloc[-1],
                    'Casos Início': segment['cases_confirmed'].iloc[0],
                    'Casos Fim': segment['cases_confirmed'].iloc[-1],
                    'Duração': duration
                })

        df_results = pd.DataFrame(results)
        return df_results
