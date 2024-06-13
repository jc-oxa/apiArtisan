from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import mysql.connector
from typing import List, Optional

app = FastAPI()

def conectarNube():
    try:
        conn = mysql.connector.connect(
            host='mysql-43314-0.cloudclusters.net',
            user='admin',
            password='adbO1NJG',
            database='marca_nuevo',
            port=19751
        )
        return conn
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database connection error: {err}")

class Proceso(BaseModel):
    IdOrdenProduccion: str
    IdOperario: str
    Nombres: Optional[str] = None
    IdSeccion: str
    FechaHora: str
    Tipo: Optional[str] = None

@app.get("/data", response_model=List[Proceso])
def get_data(
    IdOrdenProduccion: Optional[str] = Query(None),
    IdOperario: Optional[str] = Query(None),
    IdSeccion: Optional[str] = Query(None)
):
    try:
        conn = conectarNube()
        cursor = conn.cursor()
        
        query = """SELECT A.IdOrdenProduccion, A.IdOperario, B.nombres, A.IdSeccion, A.FechaHora, A.Tipo
                   FROM procesos A
                   LEFT JOIN dnis B ON A.IdOperario = B.dni"""
        
        conditions = []
        if IdOrdenProduccion:
            conditions.append(f"A.IdOrdenProduccion = '{IdOrdenProduccion}'")
        if IdOperario:
            conditions.append(f"A.IdOperario = '{IdOperario}'")
        if IdSeccion:
            conditions.append(f"A.IdSeccion = '{IdSeccion}'")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY A.FechaHora DESC;"
        
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        result = [{'IdOrdenProduccion': row[0], 'IdOperario': row[1], 'Nombres': row[2], 
                   'IdSeccion': row[3], 'FechaHora': row[4] if isinstance(row[4], str) else row[4].strftime('%Y-%m-%d %H:%M:%S'), 'Tipo': row[5]} for row in data]
        return result
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database query error: {err}")
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {err}")

@app.put("/data/{IdOrdenProduccion}")
def update_data(IdOrdenProduccion: str, proceso: Proceso):
    try:
        conn = conectarNube()
        cursor = conn.cursor()

        query = """UPDATE procesos SET IdOperario = %s, IdSeccion = %s, FechaHora = %s, Tipo = %s
                   WHERE IdOrdenProduccion = %s"""

        cursor.execute(query, (proceso.IdOperario, proceso.IdSeccion, proceso.FechaHora, proceso.Tipo, IdOrdenProduccion))
        conn.commit()
        cursor.close()
        conn.close()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item not found")

        return {"message": "Item updated successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database update error: {err}")
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {err}")

@app.delete("/data/{IdOrdenProduccion}")
def delete_data(IdOrdenProduccion: str):
    try:
        conn = conectarNube()
        cursor = conn.cursor()

        query = "DELETE FROM procesos WHERE IdOrdenProduccion = %s"

        cursor.execute(query, (IdOrdenProduccion,))
        conn.commit()
        cursor.close()
        conn.close()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item not found")

        return {"message": "Item deleted successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database delete error: {err}")
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {err}")
