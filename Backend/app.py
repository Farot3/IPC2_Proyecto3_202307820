from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/procesar", methods=["GET", "POST"])
def procesar():
    input = request.form.get("input")

    if input:
        processed_data = input  # Ejemplo de procesamiento
        # Enviar los datos procesados de vuelta a Django
        return jsonify({"datosProcesaods": processed_data}), 200
    else:
        return jsonify({"error": "No se enviaron datos"}), 400


if __name__ == "__main__":
    app.run(debug=True)
