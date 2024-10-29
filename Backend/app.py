from flask import Flask, request, jsonify, Response
from xml.dom import minidom
import xml.etree.ElementTree as ET
import re
from analizador import Analizador
from empresa import Empresa
from servicio import Servicio
from mensaje import Mensaje
from MensajeFecha import MensajesPorFecha
from mensajeAnaliza import MensajesAnalizados
from Totalfecha import TotalesPorFecha
from datosAnalizados import DatosAnalizados
import unicodedata
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)

# Inicializar las variables globales
analizador = Analizador()
mensajes_por_fecha = MensajesPorFecha()
mensajes_analizados = MensajesAnalizados()
totales_por_fecha = TotalesPorFecha()
datos_analizados = DatosAnalizados()

def normalize_text(text):
    text = text.lower()
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("ASCII")
    return text

def clean_text(text):
    return " ".join(text.split())

def extract_date(text):
    match = re.search(r"\d{2}/\d{2}/\d{4}", text)
    return match.group(0) if match else "Fecha no encontrada"

@app.route("/prueba_mensaje", methods=["POST"])
def prueba_mensaje():
    mensaje_xml = request.form.get("mensaje")
    try:
        root = ET.fromstring(mensaje_xml)
        mensaje_texto = root.text.strip()

        # Crear un analizador temporal para procesar el mensaje sin almacenarlo
        analizador_temp = Analizador()
        mensaje = Mensaje(normalize_text(clean_text(mensaje_texto)))
        analizador_temp.agregar_mensaje(mensaje)

        fecha = extract_date(mensaje.texto)
        red_social = re.search(r"red social: (\w+)", mensaje.texto).group(1)
        usuario = re.search(r"usuario: (\S+)", mensaje.texto).group(1)

        for palabra in analizador.obtener_sentimientos().obtener_positivos():
            if palabra in mensaje.texto:
                mensaje.agregar_positivo(palabra)

        for palabra in analizador.obtener_sentimientos().obtener_negativos():
            if palabra in mensaje.texto:
                mensaje.agregar_negativo(palabra)

        for empresa in analizador.obtener_empresas():
            for servicio in empresa.obtener_servicios():
                if servicio.nombre in mensaje.texto or any(
                    alias in mensaje.texto for alias in servicio.obtener_alias()
                ):
                    mensaje.agregar_servicio(servicio.nombre)

        # Contar neutros
        if (
            len(mensaje.obtener_positivos()) == 0
            and len(mensaje.obtener_negativos()) == 0
        ):
            mensaje.neutros_count = 1
        elif len(mensaje.obtener_positivos()) == len(mensaje.obtener_negativos()):
            mensaje.neutros_count = len(mensaje.obtener_positivos())
        else:
            mensaje.neutros_count = 0

        total_palabras = len(mensaje.obtener_positivos()) + len(mensaje.obtener_negativos())
        sentimiento_positivo = (len(mensaje.obtener_positivos()) / total_palabras) * 100 if total_palabras > 0 else 0
        sentimiento_negativo = (len(mensaje.obtener_negativos()) / total_palabras) * 100 if total_palabras > 0 else 0
        sentimiento_analizado = "positivo" if sentimiento_positivo > sentimiento_negativo else "negativo"

        respuesta = ET.Element("respuesta")
        fecha_elem = ET.SubElement(respuesta, "fecha")
        fecha_elem.text = fecha
        red_social_elem = ET.SubElement(respuesta, "red_social")
        red_social_elem.text = red_social
        usuario_elem = ET.SubElement(respuesta, "usuario")
        usuario_elem.text = usuario

        empresas_elem = ET.SubElement(respuesta, "empresas")
        for empresa in analizador.obtener_empresas():
            empresa_elem = ET.SubElement(empresas_elem, "empresa", nombre=empresa.nombre)
            for servicio in empresa.obtener_servicios():
                if servicio.nombre in mensaje.obtener_servicios():
                    servicio_elem = ET.SubElement(empresa_elem, "servicio")
                    servicio_elem.text = servicio.nombre

        palabras_positivas_elem = ET.SubElement(respuesta, "palabras_positivas")
        palabras_positivas_elem.text = str(len(mensaje.obtener_positivos()))
        palabras_negativas_elem = ET.SubElement(respuesta, "palabras_negativas")
        palabras_negativas_elem.text = str(len(mensaje.obtener_negativos()))
        sentimiento_positivo_elem = ET.SubElement(respuesta, "sentimiento_positivo")
        sentimiento_positivo_elem.text = f"{sentimiento_positivo}%"
        sentimiento_negativo_elem = ET.SubElement(respuesta, "sentimiento_negativo")
        sentimiento_negativo_elem.text = f"{sentimiento_negativo}%"
        sentimiento_analizado_elem = ET.SubElement(respuesta, "sentimiento_analizado")
        sentimiento_analizado_elem.text = sentimiento_analizado

        return Response(ET.tostring(respuesta, encoding="utf-8"), mimetype="application/xml")
    except ET.ParseError:
        return jsonify({"error": "Error al parsear el mensaje XML."}), 400
    except Exception as e:
        return jsonify({"error": f"Error al procesar el mensaje: {str(e)}"}), 500


@app.route("/reporte_pdf", methods=["GET"])
def reporte_pdf():
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Título del reporte
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 40, "Reporte de Clasificación de Mensajes")

    y_position = height - 80

    # Obtener los datos analizados
    datos = datos_analizados.obtener_datos()

    for data in datos:
        for fecha, mensajes in data["mensajes_por_fecha"].items():
            if y_position < 100:
                p.showPage()
                y_position = height - 40

            p.setFont("Helvetica-Bold", 12)
            p.drawString(100, y_position, f"Fecha: {fecha}")
            y_position -= 20

            p.setFont("Helvetica", 10)
            p.drawString(100, y_position, f"Cantidad total de mensajes recibidos: {len(mensajes)}")
            y_position -= 20

            totales = data["totales_por_fecha"][fecha]
            p.drawString(100, y_position, f"Cantidad total de mensajes positivos: {totales['positivos']}")
            y_position -= 20
            p.drawString(100, y_position, f"Cantidad total de mensajes negativos: {totales['negativos']}")
            y_position -= 20
            p.drawString(100, y_position, f"Cantidad total de mensajes neutros: {totales['neutros']}")
            y_position -= 20

            for empresa in data["empresas"]:
                empresa_totales = empresa.obtener_totales_por_fecha(fecha)
                p.setFont("Helvetica-Bold", 12)
                p.drawString(100, y_position, f"Empresa: {empresa.nombre}")
                y_position -= 20

                p.setFont("Helvetica", 10)
                p.drawString(100, y_position, f"Número total de mensajes que mencionan a {empresa.nombre}: {empresa_totales['positivos'] + empresa_totales['negativos'] + empresa_totales['neutros']}")
                y_position -= 20
                p.drawString(100, y_position, f"Mensajes positivos: {empresa_totales['positivos']}")
                y_position -= 20
                p.drawString(100, y_position, f"Mensajes negativos: {empresa_totales['negativos']}")
                y_position -= 20
                p.drawString(100, y_position, f"Mensajes neutros: {empresa_totales['neutros']}")
                y_position -= 20

                for servicio in empresa.obtener_servicios():
                    servicio_totales = servicio.obtener_totales_por_fecha(fecha)
                    p.setFont("Helvetica-Bold", 10)
                    p.drawString(120, y_position, f"Servicio: {servicio.nombre}")
                    y_position -= 20

                    p.setFont("Helvetica", 10)
                    p.drawString(120, y_position, f"Número total de mensajes que mencionan al servicio: {servicio_totales['positivos'] + servicio_totales['negativos'] + servicio_totales['neutros']}")
                    y_position -= 20
                    p.drawString(120, y_position, f"Mensajes positivos: {servicio_totales['positivos']}")
                    y_position -= 20
                    p.drawString(120, y_position, f"Mensajes negativos: {servicio_totales['negativos']}")
                    y_position -= 20
                    p.drawString(120, y_position, f"Mensajes neutros: {servicio_totales['neutros']}")
                    y_position -= 20

            y_position -= 20

    p.showPage()
    p.save()

    buffer.seek(0)
    return Response(buffer, mimetype='application/pdf', headers={"Content-Disposition": "attachment;filename=reporte.pdf"})

@app.route("/consultar_datos", methods=["GET"])
def consultar_datos():
    try:
        # Leer el último archivo de respuesta
        with open("ultimo_respuesta.xml", "r", encoding="utf-8") as file:
            data = file.read()
        return Response(data, mimetype="application/xml")
    except FileNotFoundError:
        return jsonify({"error": "No se encontró el archivo de respuesta"}), 404
    except Exception as e:
        return jsonify({"error": f"Error al procesar el archivo: {str(e)}"}), 500

@app.route("/obtener_fechas", methods=["GET"])
def obtener_fechas():
    # Obtener las fechas disponibles
    fechas = list(mensajes_por_fecha.obtener_mensajes().keys())
    return jsonify(fechas)

@app.route("/obtener_empresas", methods=["GET"])
def obtener_empresas():
    # Obtener las empresas disponibles
    empresas = [empresa.nombre for empresa in analizador.obtener_empresas()]
    return jsonify(empresas)

@app.route("/obtener_resumen", methods=["POST"])
def obtener_resumen():
    fecha = request.form.get("fecha")
    empresa = request.form.get("empresa")
    
    # Obtener el resumen de clasificación por fecha y empresa
    resumen = {
        "total": 0,
        "positivos": 0,
        "negativos": 0,
        "neutros": 0
    }
    
    mensajes = mensajes_por_fecha.obtener_mensajes().get(fecha, [])
    print(f"Mensajes para la fecha {fecha}: {[mensaje.texto for mensaje in mensajes]}")
    for mensaje in mensajes:
        servicios = mensaje.obtener_servicios()
        print(f"Servicios del mensaje: {servicios}")
        if empresa == "todas" or empresa in servicios:
            resumen["total"] += 1
            resumen["positivos"] += len(mensaje.obtener_positivos())
            resumen["negativos"] += len(mensaje.obtener_negativos())
            resumen["neutros"] += mensaje.obtener_neutros()
            # Agregar prints para verificar los mensajes y sus clasificaciones
            print(f"Mensaje: {mensaje.texto}")
            print(f"  Positivos: {mensaje.obtener_positivos()}")
            print(f"  Negativos: {mensaje.obtener_negativos()}")
            print(f"  Neutros: {mensaje.obtener_neutros()}")
            print(f"  Servicios: {servicios}")
    
    print("Resumen final:", resumen)
    return jsonify(resumen)

def leer_archivo_entrada(archivo):
    try:
        tree = ET.parse(archivo)
        root = tree.getroot()
        if root.tag != "solicitud_clasificacion":
            return {
                "error": "El archivo XML debe empezar con la etiqueta <solicitud_clasificacion>."
            }

        # Usar las variables globales
        global analizador, mensajes_por_fecha, mensajes_analizados, totales_por_fecha

        # Reiniciar las variables globales
        analizador = Analizador()
        mensajes_por_fecha = MensajesPorFecha()
        mensajes_analizados = MensajesAnalizados()
        totales_por_fecha = TotalesPorFecha()

        # Extraer sentimientos positivos
        for palabra in root.findall(".//sentimientos_positivos/palabra"):
            analizador.obtener_sentimientos().agregar_positivo(
                normalize_text(palabra.text.strip())
            )
        print("Sentimientos positivos:", analizador.obtener_sentimientos().obtener_positivos())

        # Extraer sentimientos negativos
        for palabra in root.findall(".//sentimientos_negativos/palabra"):
            analizador.obtener_sentimientos().agregar_negativo(
                normalize_text(palabra.text.strip())
            )
        print("Sentimientos negativos:", analizador.obtener_sentimientos().obtener_negativos())

        # Extraer empresas y sus servicios
        for empresa in root.findall(".//empresas_analizar/empresa"):
            empresa_data = Empresa(normalize_text(empresa.find("nombre").text.strip()))
            for servicio in empresa.findall(".//servicios/servicio"):
                servicio_data = Servicio(normalize_text(servicio.attrib.get("nombre")))
                for alias in servicio.findall("alias"):
                    servicio_data.agregar_alias(normalize_text(alias.text.strip()))
                empresa_data.agregar_servicio(servicio_data)
            analizador.agregar_empresa(empresa_data)
        print("Empresas y servicios:", [(empresa.nombre, [servicio.nombre for servicio in empresa.obtener_servicios()]) for empresa in analizador.obtener_empresas()])

        # Extraer mensajes
        for mensaje in root.findall(".//lista_mensajes/mensaje"):
            analizador.agregar_mensaje(
                Mensaje(normalize_text(clean_text(mensaje.text)))
            )
        print("Mensajes extraídos:", [mensaje.texto for mensaje in analizador.obtener_mensajes()])

        # Analizar mensajes
        for mensaje in analizador.obtener_mensajes():
            fecha = extract_date(mensaje.texto)
            mensajes_por_fecha.agregar_mensaje(fecha, mensaje)

            for palabra in analizador.obtener_sentimientos().obtener_positivos():
                if palabra in mensaje.texto:
                    mensaje.agregar_positivo(palabra)

            for palabra in analizador.obtener_sentimientos().obtener_negativos():
                if palabra in mensaje.texto:
                    mensaje.agregar_negativo(palabra)

            for empresa in analizador.obtener_empresas():
                for servicio in empresa.obtener_servicios():
                    if servicio.nombre in mensaje.texto or any(
                        alias in mensaje.texto for alias in servicio.obtener_alias()
                    ):
                        mensaje.agregar_servicio(servicio.nombre)
                        servicio.agregar_totales_por_fecha(
                            fecha,
                            len(mensaje.obtener_positivos()),
                            len(mensaje.obtener_negativos()),
                            mensaje.obtener_neutros(),
                        )
                        empresa.agregar_totales_por_fecha(
                            fecha,
                            len(mensaje.obtener_positivos()),
                            len(mensaje.obtener_negativos()),
                            mensaje.obtener_neutros(),
                        )

            # Contar neutros
            if (
                len(mensaje.obtener_positivos()) == 0
                and len(mensaje.obtener_negativos()) == 0
            ):
                mensaje.neutros_count = 1
            elif len(mensaje.obtener_positivos()) == len(mensaje.obtener_negativos()):
                mensaje.neutros_count = len(mensaje.obtener_positivos())
            else:
                mensaje.neutros_count = 0

            totales_por_fecha.agregar_totales(
                fecha,
                len(mensaje.obtener_positivos()),
                len(mensaje.obtener_negativos()),
                mensaje.obtener_neutros(),
            )

        data = {
            "mensajes_analizados": mensajes_analizados.obtener_mensajes(),
            "mensajes_por_fecha": mensajes_por_fecha.obtener_mensajes(),
            "totales_por_fecha": totales_por_fecha.totales,
            "empresas": analizador.obtener_empresas(),  # Asegurarse de agregar las empresas al diccionario
        }

        # Imprimir los datos extraídos
        for fecha, mensajes in mensajes_por_fecha.obtener_mensajes().items():
            print(f"Fecha: {fecha}")
            for mensaje in mensajes:
                print("  Mensaje:", mensaje.texto)
                print("    Lugar:", mensaje.lugar)
                print("    Usuario:", mensaje.usuario)
                print("    Red Social:", mensaje.red_social)
                print("    Positivos:", mensaje.obtener_positivos())
                print("    Negativos:", mensaje.obtener_negativos())
                print("    Servicios:", mensaje.obtener_servicios())
                print("    Neutros:", mensaje.obtener_neutros())
        for fecha, totales in totales_por_fecha.totales.items():
            print(f"Fecha: {fecha}")
            print("  Total Positivos:", totales["positivos"])
            print("  Total Negativos:", totales["negativos"])
            print("  Total Neutros:", totales["neutros"])

        datos_analizados.agregar_datos(data)
        return data

    except ET.ParseError:
        return {"error": "Error al parsear el archivo XML."}
    except Exception as e:
        return {"error": f"Error al procesar el archivo: {str(e)}"}

def prettify_xml(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ")

def generar_xml(data):
    root = ET.Element("lista_respuestas")

    for fecha, mensajes in data["mensajes_por_fecha"].items():
        respuesta = ET.SubElement(root, "respuesta")
        fecha_elem = ET.SubElement(respuesta, "fecha")
        fecha_elem.text = fecha

        mensajes_elem = ET.SubElement(respuesta, "mensajes")
        total_elem = ET.SubElement(mensajes_elem, "total")
        total_elem.text = str(len(mensajes))
        positivos_elem = ET.SubElement(mensajes_elem, "positivos")
        positivos_elem.text = str(data["totales_por_fecha"][fecha]["positivos"])
        negativos_elem = ET.SubElement(mensajes_elem, "negativos")
        negativos_elem.text = str(data["totales_por_fecha"][fecha]["negativos"])
        neutros_elem = ET.SubElement(mensajes_elem, "neutros")
        neutros_elem.text = str(data["totales_por_fecha"][fecha]["neutros"])

        analisis_elem = ET.SubElement(respuesta, "analisis")
        for empresa in data["empresas"]:
            empresa_totales = empresa.obtener_totales_por_fecha(fecha)
            empresa_elem = ET.SubElement(
                analisis_elem, "empresa", nombre=empresa.nombre
            )
            mensajes_empresa_elem = ET.SubElement(empresa_elem, "mensajes")
            total_empresa_elem = ET.SubElement(mensajes_empresa_elem, "total")
            total_empresa_elem.text = str(
                empresa_totales["positivos"]
                + empresa_totales["negativos"]
                + empresa_totales["neutros"]
            )
            positivos_empresa_elem = ET.SubElement(mensajes_empresa_elem, "positivos")
            positivos_empresa_elem.text = str(empresa_totales["positivos"])
            negativos_empresa_elem = ET.SubElement(mensajes_empresa_elem, "negativos")
            negativos_empresa_elem.text = str(empresa_totales["negativos"])
            neutros_empresa_elem = ET.SubElement(mensajes_empresa_elem, "neutros")
            neutros_empresa_elem.text = str(empresa_totales["neutros"])

            servicios_elem = ET.SubElement(empresa_elem, "servicios")
            for servicio in empresa.obtener_servicios():
                servicio_totales = servicio.obtener_totales_por_fecha(fecha)
                servicio_elem = ET.SubElement(
                    servicios_elem, "servicio", nombre=servicio.nombre
                )
                mensajes_servicio_elem = ET.SubElement(servicio_elem, "mensajes")
                total_servicio_elem = ET.SubElement(mensajes_servicio_elem, "total")
                total_servicio_elem.text = str(
                    servicio_totales["positivos"]
                    + servicio_totales["negativos"]
                    + servicio_totales["neutros"]
                )
                positivos_servicio_elem = ET.SubElement(
                    mensajes_servicio_elem, "positivos"
                )
                positivos_servicio_elem.text = str(servicio_totales["positivos"])
                negativos_servicio_elem = ET.SubElement(
                    mensajes_servicio_elem, "negativos"
                )
                negativos_servicio_elem.text = str(servicio_totales["negativos"])
                neutros_servicio_elem = ET.SubElement(mensajes_servicio_elem, "neutros")
                neutros_servicio_elem.text = str(servicio_totales["neutros"])

    return prettify_xml(root)

@app.route("/procesar", methods=["POST"])
def procesar():
    input_data = request.form.get("input")

    if input_data:
        with open("entrada.xml", "w", encoding="utf-8") as file:
            file.write(input_data)
        data = leer_archivo_entrada("entrada.xml")
        xml_response = generar_xml(data)
        with open("ultimo_respuesta.xml", "w", encoding="utf-8") as file:
            file.write(xml_response)
        
        # Verificar que los datos se están guardando correctamente
        print("Datos analizados:", datos_analizados.obtener_datos())
        print("Mensajes por fecha:", mensajes_por_fecha.obtener_mensajes())
        print("Totales por fecha:", totales_por_fecha.totales)
        
        return Response(xml_response, mimetype="application/xml")
    else:
        return jsonify({"error": "No se proporcionó ningún dato de entrada"}), 400

@app.route("/reset", methods=["POST"])
def reset():
    # Restablecer la base de datos al estado inicial
    analizador.obtener_sentimientos().positivos = []
    analizador.obtener_sentimientos().negativos = []
    analizador.empresas = []
    analizador.mensajes = []
    mensajes_por_fecha.reset()
    mensajes_analizados.reset()
    datos_analizados.reset()

    return jsonify({"message": "Base de datos restablecida al estado inicial"}), 200

if __name__ == "__main__":
    app.run(debug=True)