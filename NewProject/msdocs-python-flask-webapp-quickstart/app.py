from flask import Flask, render_template, request, redirect, url_for,jsonify, flash
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from flask import send_file 
import pyodbc as podbc
import os
import sqlite3

app = Flask(__name__)

# Azure Blob Storage configurations
STORAGE_ACCOUNT_NAME = 'alizine'
STORAGE_ACCOUNT_KEY = '18nccY7alfHmKyQDvW6mhHnI4oIea0XpZ/0yXiEuzX1LiMgDlmoxBKTUV6g4e4Ph4Ayhv3vne8XL+AStvi25ig=='
CONTAINER_NAME = 'file'
connection_string ="DefaultEndpointsProtocol=https;AccountName=alizine;AccountKey=18nccY7alfHmKyQDvW6mhHnI4oIea0XpZ/0yXiEuzX1LiMgDlmoxBKTUV6g4e4Ph4Ayhv3vne8XL+AStvi25ig==;EndpointSuffix=core.windows.net"

#SQL database configurations 
server = 'alizine.database.windows.net'
database = 'alizine'
username = 'alizine'
password = 'Ali26042002'
driver = '{ODBC Driver 18 for SQL Server}'  
download_directory = 'C:\\Users\\alizi\\Downloads>'

blob_service_client = BlobServiceClient(account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net", credential=STORAGE_ACCOUNT_KEY)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)


def connect_to_blob_storage():
    try:
        blob_service_client = BlobServiceClient(account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
                                                credential=STORAGE_ACCOUNT_KEY)
        return blob_service_client
    except Exception as e:
        print(f"Error connecting to Blob Storage: {str(e)}")
        return None
    


# Test the connection
blob_client = connect_to_blob_storage()
if blob_client:
    print("Connected to Azure Blob Storage")
else:
    print("Failed to connect to Azure Blob Storage")

def upload_to_blob_storage(file_stream, file_name):
    try:
        blob_service_client = BlobServiceClient(account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net", credential=STORAGE_ACCOUNT_KEY)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        
        blob_client = container_client.get_blob_client(file_name)
        blob_client.upload_blob(file_stream)
        
        print(f"Uploaded {file_name} to Azure Blob Storage.")
        return True
    except Exception as e:
        print(f"Error uploading {file_name} to Azure Blob Storage: {str(e)}")
        return False
    
# Function to establish a connection with SQL Server
def create_connection():
  
    try:
        conn = podbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
        print('Connected to the database')
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {str(e)}")
        return None

 # Example route to execute a INSERT query    
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        MaTable = request.form.get('Name')
        type = request.form.get('type')
        
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO MaTable (Name, type) VALUES (?, ?)", (MaTable, type))
                conn.commit()
                conn.close()
                return 'Data inserted successfully'
            except Exception as e:
                return f'Error inserting data: {str(e)}'
        else:
            return 'Failed to connect to the database'
    return render_template('index.html')

# Example route to execute a SELECT query
@app.route('/select_data', methods=['GET'])
def select_data():
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM MaTable')
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]  # Get column names
        
        conn.close()

        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))

        return jsonify({'data': data})
    else:
        return jsonify({'error': 'Failed to connect to the database'})

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    if upload_to_blob_storage(file.stream, file.filename):
        return 'File uploaded successfully to Azure Blob Storage!'
    else:
        return 'File upload failed!'

def list_files():
    # Create BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Get the container client
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    # List all blobs/files in the container
    blob_list = container_client.list_blobs()

    # Get blob names and return them as JSON
    blob_names = [blob.name for blob in blob_list]
    return jsonify(blob_names)
    
@app.route('/download', methods=['POST'])
def download():
    selected_file = request.form['file']
    blob_client = container_client.get_blob_client(selected_file)


    # Download the file to a temporary location
    temp_file_path = f"/tmp/{selected_file}"  # Change this to your preferred temporary location
    with open(temp_file_path, "wb") as my_blob:
        download_stream = blob_client.download_blob()
        my_blob.write(download_stream.readall())

    # Send the file as a response for download
    return send_file(temp_file_path, as_attachment=True)


def index():
    blob_service_client = connect_to_blob_storage()
    if blob_service_client:
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        blob_list = container_client.list_blobs()
        blob_names = [blob.name for blob in blob_list]
        return render_template('index.html', blobs=blob_names)
    else:
        return "Failed to connect to Blob Storage"

@app.route('/afficher_fichiers', methods=['get'])
def afficher_fichiers():
    # Remplacez ces valeurs par vos propres clés d'accès et noms

    blob_service_client = BlobServiceClient(account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net", credential=STORAGE_ACCOUNT_KEY)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    # Récupère le conteneur spécifique
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    # Liste les blobs (fichiers) dans le conteneur
    blob_list = container_client.list_blobs()

    # Récupère les noms des fichiers
    noms_fichiers = [blob.name for blob in blob_list]
    
    return render_template('fichier.html', noms_fichiers=noms_fichiers)

if __name__ == '__main__':
    app.run(debug=False)
    