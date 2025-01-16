import os
from pyprojroot import here

# --------------------------------------------------
# Constants for General Setup
# --------------------------------------------------
# Define the root folder of the project
ROOT_FOLDER = here()

# Ensure necessary directories exist
os.makedirs(ROOT_FOLDER, exist_ok=True)
