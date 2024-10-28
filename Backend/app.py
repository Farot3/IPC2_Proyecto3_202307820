from flask import Flask, request, jsonify
import xml.etree.ElementTree as ET
from lxml import etree
from unidecode import unidecode

app = Flask(__name__)


def normalize_text(text):
    return unidecode(text).lower()


@app.route("/procesar", methods=["GET", "POST"])
def procesar():
    input = request.form.get("input")

    if input:
        processed_data = input  # Ejemplo de procesamiento4
        newInput = normalize_text(input)
        # Enviar los datos procesados de vuelta a Django
        return jsonify({"datosProcesaods": newInput}), 200
    else:
        return jsonify({"error": "No se enviaron datos"}), 400


def leer_archivo_entrada(archivo):
    try:
        tree = ET.parse(archivo)
        root = tree.getroot()
        if root.tag != "solicitud_clasificacion":
            print(
                "Error: El archivo XML debe empezar con la etiqueta <solicitud_clasificacion>."
            )
    except Exception as e:
        print(f"Error al procesar el archivo: {str(e)}", "error")
        error1 = True


if __name__ == "__main__":
    app.run(debug=True)
