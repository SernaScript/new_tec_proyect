import requests
import pandas as pd
import json
from datetime import datetime

def get_auth_headers(auth_token, token_type='Bearer'):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'{token_type} {auth_token}'
    }
    return headers

def obtener_documentos_fiscales():
    url_login = "http://localhost:8080/api/auth/login"
    
    credenciales = {
        "identification": "133553",
        "password": "Nutabe*2020"
    }
    
    response = requests.post(url_login, json=credenciales)
    
    if response.status_code == 200:
        data_response = response.json()
        token = data_response.get('token') or data_response.get('accessToken') or data_response.get('access_token')
        
        if token:
            print(f"Autenticación exitosa - Status Code: {response.status_code}")
            AUTH_TOKEN = token
            token_type = data_response.get('tokenType', 'Bearer') or 'Bearer'
            AUTH_TOKEN_TYPE = token_type
            
            url_fiscal_documents = "http://localhost:8080/api/fiscal-documents"
            headers = get_auth_headers(AUTH_TOKEN, AUTH_TOKEN_TYPE)
            
            response = requests.get(url_fiscal_documents, headers=headers)
            
            if response.status_code == 200:
                fiscal_documents_data = response.json()
                print(f"Petición exitosa - Status Code: {response.status_code} - Registros obtenidos: {len(fiscal_documents_data)}")
                
                df_fiscal_documents = pd.DataFrame(fiscal_documents_data)
                print(f"DataFrame creado - Registros: {len(df_fiscal_documents)}")
                
                return df_fiscal_documents
            else:
                print(f"Error en la petición - Status Code: {response.status_code}")
                return pd.DataFrame()
        else:
            print("Error: No se pudo obtener el token de la respuesta")
            return pd.DataFrame()
    else:
        print(f"Error en la autenticación - Status Code: {response.status_code}")
        return pd.DataFrame()

if __name__ == "__main__":
    df = obtener_documentos_fiscales()
    
    if not df.empty:
        print(f"\nDataFrame listo con {len(df)} registros")
    else:
        print("\nNo se pudo obtener el DataFrame")

