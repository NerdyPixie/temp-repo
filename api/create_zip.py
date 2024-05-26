import zipfile
import os

def zip_dir(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)

folder_path = 'C:/Users/Laksh/Desktop/Project/Experiment/Gardening Assistant/api/dependencies'
zip_path = 'C:/Users/Laksh/Desktop/Project/Experiment/Gardening Assistant/aws_lambda_artifact.zip'

zip_dir(folder_path, zip_path)