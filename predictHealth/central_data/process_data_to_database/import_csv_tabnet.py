import os
import logging
import pandas as pd
import sys
sys.path.append(r"C:\\Dev\\ScientifcSearch")
from predictHealth.myapp.models import Diseases, Regions, Notifications
from datetime import datetime

# Define log paths
log_file_path = "C:\\Dev\\ScientifcSearch\\predictHealth\\central_data\\logs\\application_stage.log"
stage_log_path = "C:\\Dev\\ScientifcSearch\\predictHealth\\central_data\\logs\\download_historical.txt"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ProcessData:
    def __init__(self, folder="C:\\Dev\\ScientifcSearch\\predictHealth\\central_data\\source_data", base_name='Dengue'):
        self.base_dir = folder
        self.base_name = base_name
        self.current_year = datetime.now().year

    def process_files(self):
        # Monta os nomes dos últimos 3 anos
        files = [f"{self.base_name}_{year}.csv" for year in range(self.current_year, self.current_year - 3, -1)]
        files_paths = [os.path.join(self.base_dir, file) for file in files]

        # Processa cada arquivo
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
        # Renomeia a coluna para "Week"
        if "Semana epidem. notificação" not in data.columns:
            logger.error("Missing column: 'Semana epidem. notificação'")
            return None

        data.rename(columns={"Semana epidem. notificação": "Week"}, inplace=True)
        
        # Converte dados para formato longo
        df_long = data.melt(id_vars=["Week"], var_name="Region", value_name="Cases_Confirmed")
        df_long['Week'] = df_long['Week'].str.extract(r'(\d+)').astype(int)
        return df_long

    def save_to_database(self, df_long, file_path):
        # Extrai o nome da doença e o ano do nome do arquivo
        disease_name = os.path.basename(file_path).split('_')[0]
        year = int(os.path.basename(file_path).split('_')[1].split('.')[0])

        # Obtém ou cria a entrada da doença
        disease, _ = Diseases.objects.get_or_create(disease_name=disease_name)
        
        for _, row in df_long.iterrows():
            # Obtém ou cria a entrada da região
            region, _ = Regions.objects.get_or_create(region_name=row["Region"])
            
            # Cria o registro de notificação
            Notifications.objects.create(
                notification_week=row["Week"],  
                notification_year=year,
                cases_confirmed=row["Cases_Confirmed"],
                deaths_confirmed=0,  # Assuming no death data in this example
                disease=disease,  
                region=region      
            )

            # Log de dados salvos
            logger.info(
                f"Saved data: Year {year}, Week {row['Week']}, Region {row['Region']}, Confirmed Cases {row['Cases_Confirmed']}"
            )


if __name__ == "__main__":
    # Define o diretório de dados e o nome base
    folder = "C:\\Dev\\ScientifcSearch\\predictHealth\\central_data\\source_data"
    base_name = "Dengue"

    # Cria o objeto ProcessData e processa os arquivos
    processor = ProcessData(folder=folder, base_name=base_name)
    processor.process_files()
