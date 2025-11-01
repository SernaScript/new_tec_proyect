"""
Script para verificar que el servidor esté funcionando correctamente
"""
import requests
import sys

def test_server():
    base_url = "http://localhost:8000"
    
    print("Verificando servidor FastAPI...")
    print(f"URL base: {base_url}\n")
    
    # Test 1: Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("[OK] Servidor esta corriendo correctamente")
            print(f"  Respuesta: {response.json()}\n")
        else:
            print(f"[ERROR] Servidor respondio con codigo: {response.status_code}\n")
    except requests.exceptions.ConnectionError:
        print("[ERROR] No se puede conectar al servidor")
        print("  El servidor probablemente no esta corriendo.\n")
        print("SOLUCION:")
        print("  1. Abre una nueva terminal")
        print("  2. Ejecuta: python server.py")
        print("  3. O ejecuta: uvicorn server:app --host 0.0.0.0 --port 8000 --reload")
        return False
    except Exception as e:
        print(f"[ERROR] {str(e)}\n")
        return False
    
    # Test 2: Verificar endpoint raíz
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("[OK] Endpoint raiz (/) funciona correctamente")
            print(f"  Respuesta: {response.json()}\n")
        else:
            print(f"[ERROR] Endpoint raiz respondio con codigo: {response.status_code}\n")
    except Exception as e:
        print(f"[ERROR] en endpoint raiz: {str(e)}\n")
    
    # Test 3: Verificar endpoint de documentos fiscales
    try:
        print("Probando endpoint /api/fiscal-documents...")
        response = requests.get(f"{base_url}/api/fiscal-documents", timeout=30)
        if response.status_code == 200:
            print("[OK] Endpoint /api/fiscal-documents funciona correctamente")
            data = response.json()
            print(f"  Total de registros: {data.get('total_records', 0)}")
            print(f"  Suma total: {data.get('total_sum', 0)}")
        elif response.status_code == 404:
            print("[ERROR] 404: Endpoint no encontrado")
            print("  Verifica que la ruta del endpoint sea correcta en server.py")
        elif response.status_code == 401:
            print("[WARNING] 401: Problema de autenticacion")
            print("  Verifica las credenciales en la API local")
        elif response.status_code == 500:
            print("[ERROR] 500: Error interno del servidor")
            print(f"  Detalle: {response.text}")
        else:
            print(f"[ERROR] Endpoint respondio con codigo: {response.status_code}")
            print(f"  Respuesta: {response.text[:200]}")
    except requests.exceptions.Timeout:
        print("[ERROR] TIMEOUT: La peticion tardo demasiado (posible problema de conexion a la API local)")
    except Exception as e:
        print(f"[ERROR] {str(e)}")
    
    return True

if __name__ == "__main__":
    test_server()

