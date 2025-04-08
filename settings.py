import os


# Determine the absolute path to the directory containing this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, 'src')
# INPUT_DIR = os.path.join(BASE_DIR, 'download')
from pathlib import Path
#for dynamic user_name/user_project folder structure
# def get_project_path(user_id, project_id):
#     return Path(f"download/user_{user_id}/project_{project_id}")
# INPUT_DIR = get_project_path(current_user.user_id, project_id)


DATA_DIR = os.path.join(BASE_DIR, 'data')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
print(BASE_DIR)

