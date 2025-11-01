from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import pandas as pd
from typing import Optional, Tuple
from pydantic import BaseModel

app = FastAPI(title="Fiscal Documents API", version="1.0.0")

# Configurar CORS para permitir solicitudes desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Response model for the endpoint
class FiscalDocumentsResponse(BaseModel):
    total_records: int
    total_sum: float
    records: list[dict]
    statistics: dict


def get_auth_headers(auth_token: str, token_type: str = "Bearer") -> dict:
    """Genera los headers de autenticación para las peticiones."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"{token_type} {auth_token}",
    }
    return headers


def obtener_token(
    identification: str, password: str
) -> Tuple[Optional[str], Optional[str]]:
    """Obtiene el token de autenticación de la API."""
    url_login = "http://localhost:8080/api/auth/login"

    credenciales = {"identification": identification, "password": password}

    try:
        response = requests.post(url_login, json=credenciales, timeout=10)

        if response.status_code == 200:
            data_response = response.json()
            token = (
                data_response.get("token")
                or data_response.get("accessToken")
                or data_response.get("access_token")
            )

            if token:
                token_type = data_response.get("tokenType", "Bearer") or "Bearer"
                return token, token_type
            else:
                return None, None
        else:
            return None, None
    except Exception as e:
        print(f"Error al obtener token: {str(e)}")
        return None, None


def obtener_documentos_fiscales(token: str, token_type: str) -> pd.DataFrame:
    """Obtiene los documentos fiscales de la API."""
    url_fiscal_documents = "http://localhost:8080/api/fiscal-documents"
    headers = get_auth_headers(token, token_type)

    try:
        response = requests.get(url_fiscal_documents, headers=headers, timeout=10)

        if response.status_code == 200:
            fiscal_documents_data = response.json()
            df_fiscal_documents = pd.DataFrame(fiscal_documents_data)
            return df_fiscal_documents
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"Error al obtener documentos fiscales: {str(e)}")
        return pd.DataFrame()


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Fiscal Documents API",
        "version": "1.0.0",
        "endpoints": {
            "/api/fiscal-documents": "Get fiscal documents filtered by group_info='Emitido' and calculates the total sum",
            "/health": "Server health check",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "fiscal-documents-api"}


@app.get("/api/fiscal-documents", response_model=FiscalDocumentsResponse)
async def get_fiscal_documents_filtered(
    identification: Optional[str] = "1000747836", password: Optional[str] = "Admin2024!"
):
    """
    Get fiscal documents filtered by group_info='Emitido' and calculates the total sum.

    Parameters:
    - identification: User identification (optional, defaults to notebook credentials)
    - password: User password (optional, defaults to notebook credentials)

    Returns:
    - FiscalDocumentsResponse with filtered records, total sum and statistics
    """
    # Obtener token de autenticación
    token, token_type = obtener_token(identification, password)

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Error authenticating with the API. Please verify your credentials.",
        )

    # Obtener documentos fiscales
    df_fiscal_documents = obtener_documentos_fiscales(token, token_type)

    if df_fiscal_documents.empty:
        raise HTTPException(
            status_code=404, detail="Could not retrieve fiscal documents."
        )

    # Filtrar por group_info == "Emitido"
    # Intentar diferentes nombres de columna posibles
    columna_group_info = None
    for col in ["group_info", "groupInfo", "group_info", "status"]:
        if col in df_fiscal_documents.columns:
            columna_group_info = col
            break

    if columna_group_info is None:
        raise HTTPException(
            status_code=500,
            detail=f"Column group_info not found. Available columns: {list(df_fiscal_documents.columns)}",
        )

    df_filtrado = df_fiscal_documents[
        df_fiscal_documents[columna_group_info] == "Emitido"
    ]

    if df_filtrado.empty:
        return FiscalDocumentsResponse(
            total_records=0,
            total_sum=0.0,
            records=[],
            statistics={"min": 0.0, "max": 0.0, "average": 0.0},
        )

    # Buscar columna total
    columna_total = None
    for col in ["total", "Total", "amount", "amount_total"]:
        if col in df_filtrado.columns:
            columna_total = col
            break

    if columna_total is None:
        raise HTTPException(
            status_code=500,
            detail=f"Column total not found. Available columns: {list(df_filtrado.columns)}",
        )

    # Calculate sum and statistics
    suma_total = float(df_filtrado[columna_total].sum())
    minimo = float(df_filtrado[columna_total].min())
    maximo = float(df_filtrado[columna_total].max())
    promedio = float(df_filtrado[columna_total].mean())

    # Convert DataFrame to list of dictionaries
    registros = df_filtrado.to_dict("records")

    # Convert numpy values to native Python types
    for registro in registros:
        for key, value in registro.items():
            if pd.isna(value):
                registro[key] = None
            elif isinstance(
                value, (pd.Timestamp, pd._libs.tslibs.timestamps.Timestamp)
            ):
                registro[key] = value.isoformat()
            elif hasattr(value, "item"):  # For numpy types
                registro[key] = value.item()

    return FiscalDocumentsResponse(
        total_records=len(df_filtrado),
        total_sum=suma_total,
        records=registros,
        statistics={"min": minimo, "max": maximo, "average": promedio},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
