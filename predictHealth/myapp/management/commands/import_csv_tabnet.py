import os
import logging
import pandas as pd
from django.core.management.base import BaseCommand
from myapp.models import Diseases, Regions, Notifications
from datetime import datetime

log_file_path = "C:\\Dev\\ScientifcSearch\\predictHealth\\central_data\\logs\\application_stage.log"
stage_log_path = "C:\\Dev\\ScientifcSearch\\predictHealth\\central_data\\logs\\download_historical.txt"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    
    help = 'Import multiple CSV files for database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--folder', 
            type=str, 
            default="C:\\Dev\\ScientifcSearch\\predictHealth\\central_data\\source_data",
            help='Folder that contains CSV files'
        )
        parser.add_argument(
            '--base_name', 
            type=str, 
            default='Dengue',
            help='Base name of the files (e.g., Dengue)'
        )

    def handle(self, *args, **kwargs):
        base_dir = kwargs['folder']
        base_name = kwargs['base_name']
        current_year = datetime.now().year
        
        # Monta os nomes dos últimos 3 anos
        files = [f"{base_name}_{year}.csv" for year in range(current_year, current_year - 3, -1)]
        files_paths = [os.path.join(base_dir, file) for file in files]

        for file_path in files_paths:
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                continue

            logger.info(f"Processing file: {file_path}")
            data = self.read_data(file_path)

            if data is not None:
                logger.info(f"File read successfully: {file_path}")
                logger.info(f"First five rows:\n{data.head()}")
                df_long = self.process_data(data)
                self.save_to_database(df_long, file_path)
            else:
                logger.error(f"Failed to process file: {file_path}")

    def read_data(self, file_path):
        try:
            # Lê o arquivo CSV com separador ";"
            data = pd.read_csv(file_path, sep=';')
            return data
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            return None

    def process_data(self, data):
        # Verifica se a coluna "Semana epidem. notificação" existe
        if "Semana epidem. notificação" not in data.columns:
            logger.error("Missing column: 'Semana epidem. notificação'")
            return None

        # Renomeia a coluna "Semana epidem. notificação" para "Week"
        data.rename(columns={"Semana epidem. notificação": "Week"}, inplace=True)

        # Substitui valores '-' por 0
        data.replace('-', 0, inplace=True)

        # Converte as colunas de casos para numérico, tratando erros
        # O melt vai "derreter" as colunas de região em uma nova coluna chamada "Region"
        df_long = data.melt(id_vars=["Week"], var_name="Region", value_name="Cases_Confirmed")
        
        # Converte a coluna de casos confirmados para int, se possível
        df_long['Cases_Confirmed'] = pd.to_numeric(df_long['Cases_Confirmed'], errors='coerce').fillna(0).astype(int)
        
        # Extrai números da semana para garantir que a coluna 'Week' tenha formato correto
        df_long['Week'] = df_long['Week'].str.extract(r'(\d+)').astype(int)

        return df_long

    def save_to_database(self, df_long, file_path):
        # Extrai o nome da doença e o ano do nome do arquivo
        try:
            disease_name = os.path.basename(file_path).split('_')[0]
            year = int(os.path.basename(file_path).split('_')[1].split('.')[0])

            # Cria ou obtém a doença
            disease, _ = Diseases.objects.get_or_create(disease_name=disease_name)
            
            # Itera sobre cada linha do dataframe e salva os dados no banco
            for _, row in df_long.iterrows():
                region, _ = Regions.objects.get_or_create(region_name=row["Region"])
                Notifications.objects.create(
                    notification_week=row["Week"],  
                    notification_year=year,
                    cases_confirmed=row["Cases_Confirmed"],
                    deaths_confirmed=0,
                    disease=disease,  
                    region=region      
                )

                # Log de dados salvos
                logger.info(
                    f"Saved data: Year {year}, Week {row['Week']}, Region {row['Region']}, Confirmed Cases {row['Cases_Confirmed']}"
                )
        except Exception as e:
            logger.error(f"Error saving data to the database: {e}")
