import requests
import os

# Configuración
# Ajustá la URL si tu API corre en un puerto o host distinto
URL_API = "http://127.0.0.1:8000/populate/contratos/csv"
NOMBRE_ARCHIVO = "/home/mario/Repositorios/Secop_hackatondatos/app/muestra/SECOP_II_-_Contratos_Electrónicos_20260413guacari.csv"

# Obtenemos la ruta absoluta del archivo en el mismo directorio que este script
dir_path = os.path.dirname(os.path.realpath(__file__))
RUTA_ARCHIVO = os.path.join(dir_path, NOMBRE_ARCHIVO)


def subir_csv_contratos():
    if not os.path.exists(RUTA_ARCHIVO):
        print(f"⚠️ El archivo no se encontró en la ruta: {RUTA_ARCHIVO}")
        return

    try:
        # Abrimos el archivo en modo binario
        with open(RUTA_ARCHIVO, "rb") as f:
            # El diccionario 'files' debe coincidir con el nombre del parámetro en FastAPI (file: UploadFile)
            files = {"file": (NOMBRE_ARCHIVO, f, "text/csv")}

            print(f"🚀 Subiendo archivo: {NOMBRE_ARCHIVO}...")
            print(f"📍 Destino: {URL_API}")

            response = requests.post(URL_API, files=files)

        # Verificamos la respuesta
        if response.status_code == 200:
            resultado = response.json()
            print("\n✅ ¡Carga completada con éxito!")
            print(f"📊 Resumen del procesamiento:")
            print(f"   - Insertados: {resultado.get('insertados', 0)}")
            print(f"   - Actualizados: {resultado.get('actualizados', 0)}")
            print(f"   - Errores: {resultado.get('errores', 0)}")
        else:
            print(f"\n❌ Error del servidor ({response.status_code})")
            print(f"📝 Detalle: {response.text}")

    except requests.exceptions.ConnectionError:
        print(
            "\n❌ Error de conexión: ¿Está el servidor de FastAPI corriendo en localhost:8000?"
        )
    except Exception as e:
        print(f"\n💥 Ocurrió un error inesperado: {str(e)}")


if __name__ == "__main__":
    subir_csv_contratos()
