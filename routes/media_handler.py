import os
from dotenv import load_dotenv

# Ladda miljövariabler från .env-fil
load_dotenv()


# Hämta variabler från miljön
R2_ACCESS_KEY_ID = os.environ.get("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.environ.get("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.environ.get("R2_BUCKET_NAME")
R2_BUCKET_ENDPOINT = os.environ.get("R2_BUCKET_ENDPOINT")
