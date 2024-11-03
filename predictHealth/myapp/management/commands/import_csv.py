import pandas as pd
from django.core.management.base import BaseCommand
from myapp.models import Diseases, Regions, Notifications  # Substitua pelo nome do seu aplicativo

class Command(BaseCommand):
    
    help = 'Importa dados de um arquivo CSV para o banco de dados'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Caminho para o arquivo CSV')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        data = self.read_data(csv_file)

        if data is not None:
            df_long = self.process_data(data)
            self.save_to_database(df_long)

    def read_data(self, file_path):
        try:
            data = pd.read_csv(file_path, sep=';')
            return data
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reading CSV file: {e}"))
            return None

    def process_data(self, data):
        data.rename(columns={"Semana epidem. notificação": "Week"}, inplace=True)

        df_long = data.melt(id_vars=["Week"], var_name="Region", value_name="Cases_Confirmed")
        df_long['Week'] = df_long['Week'].str.extract(r'(\d+)').astype(int)
        return df_long

    def save_to_database(self, df_long):  # Adicionado `self` aqui
        disease, created = Diseases.objects.get_or_create(disease_name="Dengue")

        for _, row in df_long.iterrows():
            region, created = Regions.objects.get_or_create(region_name=row["Region"])

            Notifications.objects.create(
                notification_week=row["Week"],  
                notification_year=2024,
                cases_confirmed=row["Cases_Confirmed"],
                deaths_confirmed=0,
                disease=disease,  # Correção aqui: use `disease` ao invés de `disease_id`
                region=region      # Correção aqui: use `region` ao invés de `region_id`
            )

            # Usar self.stdout.write para mensagens
            self.stdout.write(f"Dados salvos: Semana {row['Week']}, Região {row['Region']}, Casos Confirmados {row['Cases_Confirmed']}")


