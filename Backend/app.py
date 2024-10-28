from flask import Flask, request, jsonify, Response
import xml.etree.ElementTree as ET
import re
from xml.dom import minidom
from analizador import Analizador
from empresa import Empresa
from servicio import Servicio
from mensaje import Mensaje
from MensajeFecha import MensajesPorFecha
from mensajeAnaliza import MensajesAnalizados

app = Flask(__name__)


def clean_text(text):
    return " ".join(text.split())


def extract_date(text):
    match = re.search(r"\d{2}/\d{2}/\d{4}", text)
    return match.group(0) if match else "Fecha no encontrada"


def leer_archivo_entrada(archivo):
    try:
        tree = ET.parse(archivo)
        root = tree.getroot()
        if root.tag != "solicitud_clasificacion":
            return {
                "error": "El archivo XML debe empezar con la etiqueta <solicitud_clasificacion>."
            }

        analizador = Analizador()
        mensajes_por_fecha = MensajesPorFecha()
        mensajes_analizados = MensajesAnalizados()

        # Extraer sentimientos positivos
        for palabra in root.findall(".//sentimientos_positivos/palabra"):
            analizador.obtener_sentimientos().agregar_positivo(palabra.text.strip())

        # Extraer sentimientos negativos
        for palabra in root.findall(".//sentimientos_negativos/palabra"):
            analizador.obtener_sentimientos().agregar_negativo(palabra.text.strip())

        # Extraer empresas y sus servicios
        for empresa in root.findall(".//empresas_analizar/empresa"):
            empresa_data = Empresa(empresa.find("nombre").text.strip())
            for servicio in empresa.findall(".//servicios/servicio"):
                servicio_data = Servicio(servicio.attrib.get("nombre"))
                for alias in servicio.findall("alias"):
                    servicio_data.agregar_alias(alias.text.strip())
                empresa_data.agregar_servicio(servicio_data)
            analizador.agregar_empresa(empresa_data)

        # Extraer mensajes
        for mensaje in root.findall(".//lista_mensajes/mensaje"):
            analizador.agregar_mensaje(Mensaje(clean_text(mensaje.text)))

        # Analizar mensajes
        total_positivos = 0
        total_negativos = 0
        total_neutros = 0
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
            mensaje.contar_neutros()
            total_positivos += len(mensaje.obtener_positivos())
            total_negativos += len(mensaje.obtener_negativos())
            total_neutros += mensaje.obtener_neutros()

        data = {
            "mensajes_analizados": mensajes_analizados.obtener_mensajes(),
            "mensajes_por_fecha": mensajes_por_fecha.obtener_mensajes(),
            "total_positivos": total_positivos,
            "total_negativos": total_negativos,
            "total_neutros": total_neutros,
            "total_mensajes": total_positivos + total_negativos + total_neutros,
            "empresas": analizador.obtener_empresas(),  # Asegurarse de agregar las empresas al diccionario
        }

        # Imprimir los datos extraídos
        print(
            "Sentimientos Positivos:",
            analizador.obtener_sentimientos().obtener_positivos(),
        )
        print(
            "Sentimientos Negativos:",
            analizador.obtener_sentimientos().obtener_negativos(),
        )
        for empresa in analizador.obtener_empresas():
            print("Empresa:", empresa.nombre)
            for servicio in empresa.obtener_servicios():
                print("  Servicio:", servicio.nombre)
                print("    Alias:", servicio.obtener_alias())
        for fecha, mensajes in mensajes_por_fecha.obtener_mensajes().items():
            print(f"Fecha: {fecha}")
            for mensaje in mensajes:
                print("  Mensaje:", mensaje.texto)
                print("    Positivos:", mensaje.obtener_positivos())
                print("    Negativos:", mensaje.obtener_negativos())
                print("    Servicios:", mensaje.obtener_servicios())
                print("    Neutros:", mensaje.obtener_neutros())
        print("Total Positivos:", total_positivos)
        print("Total Negativos:", total_negativos)
        print("Total Neutros:", total_neutros)
        print("Total Mensajes:", total_positivos + total_negativos + total_neutros)

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
        positivos_elem.text = str(sum(len(m.obtener_positivos()) for m in mensajes))
        negativos_elem = ET.SubElement(mensajes_elem, "negativos")
        negativos_elem.text = str(sum(len(m.obtener_negativos()) for m in mensajes))
        neutros_elem = ET.SubElement(mensajes_elem, "neutros")
        neutros_elem.text = str(sum(m.obtener_neutros() for m in mensajes))

        analisis_elem = ET.SubElement(respuesta, "analisis")
        for empresa in data["empresas"]:
            empresa_elem = ET.SubElement(
                analisis_elem, "empresa", nombre=empresa.nombre
            )
            mensajes_empresa_elem = ET.SubElement(empresa_elem, "mensajes")
            total_empresa_elem = ET.SubElement(mensajes_empresa_elem, "total")
            total_empresa_elem.text = str(
                len([m for m in mensajes if empresa.nombre in m.texto])
            )
            positivos_empresa_elem = ET.SubElement(mensajes_empresa_elem, "positivos")
            positivos_empresa_elem.text = str(
                sum(
                    len(m.obtener_positivos())
                    for m in mensajes
                    if empresa.nombre in m.texto
                )
            )
            negativos_empresa_elem = ET.SubElement(mensajes_empresa_elem, "negativos")
            negativos_empresa_elem.text = str(
                sum(
                    len(m.obtener_negativos())
                    for m in mensajes
                    if empresa.nombre in m.texto
                )
            )
            neutros_empresa_elem = ET.SubElement(mensajes_empresa_elem, "neutros")
            neutros_empresa_elem.text = str(
                sum(m.obtener_neutros() for m in mensajes if empresa.nombre in m.texto)
            )

            servicios_elem = ET.SubElement(empresa_elem, "servicios")
            for servicio in empresa.obtener_servicios():
                servicio_elem = ET.SubElement(
                    servicios_elem, "servicio", nombre=servicio.nombre
                )
                mensajes_servicio_elem = ET.SubElement(servicio_elem, "mensajes")
                total_servicio_elem = ET.SubElement(mensajes_servicio_elem, "total")
                total_servicio_elem.text = str(
                    len(
                        [
                            m
                            for m in mensajes
                            if servicio.nombre in m.texto
                            or any(
                                alias in m.texto for alias in servicio.obtener_alias()
                            )
                        ]
                    )
                )
                positivos_servicio_elem = ET.SubElement(
                    mensajes_servicio_elem, "positivos"
                )
                positivos_servicio_elem.text = str(
                    sum(
                        len(m.obtener_positivos())
                        for m in mensajes
                        if servicio.nombre in m.texto
                        or any(alias in m.texto for alias in servicio.obtener_alias())
                    )
                )
                negativos_servicio_elem = ET.SubElement(
                    mensajes_servicio_elem, "negativos"
                )
                negativos_servicio_elem.text = str(
                    sum(
                        len(m.obtener_negativos())
                        for m in mensajes
                        if servicio.nombre in m.texto
                        or any(alias in m.texto for alias in servicio.obtener_alias())
                    )
                )
                neutros_servicio_elem = ET.SubElement(mensajes_servicio_elem, "neutros")
                neutros_servicio_elem.text = str(
                    sum(
                        m.obtener_neutros()
                        for m in mensajes
                        if servicio.nombre in m.texto
                        or any(alias in m.texto for alias in servicio.obtener_alias())
                    )
                )

    return prettify_xml(root)


@app.route("/procesar", methods=["POST"])
def procesar():
    input_data = request.form.get("input")

    if input_data:
        # Guardar el contenido del archivo en un archivo temporal
        with open("temp.xml", "w", encoding="utf-8") as temp_file:
            temp_file.write(input_data)

        # Leer y procesar el archivo XML
        data = leer_archivo_entrada("temp.xml")
        if "error" in data:
            return jsonify(data), 400

        # Generar el XML de respuesta
        xml_response = generar_xml(data)

        # Enviar el XML de respuesta de vuelta a Django
        return Response(xml_response, mimetype="application/xml")
    else:
        return jsonify({"error": "No se enviaron datos"}), 400


@app.route("/reset", methods=["POST"])
def reset():
    # Aquí puedes agregar la lógica para restablecer la base de datos al estado inicial
    # Por ejemplo, si estás usando una base de datos en memoria, puedes simplemente vaciarla
    # Si estás usando una base de datos persistente, puedes ejecutar una consulta para eliminar todos los datos

    # Ejemplo de restablecimiento de una base de datos en memoria
    analizador = Analizador()
    mensajes_por_fecha = MensajesPorFecha()
    mensajes_analizados = MensajesAnalizados()

    analizador.obtener_sentimientos().positivos = []
    analizador.obtener_sentimientos().negativos = []
    analizador.empresas = []
    analizador.mensajes = []
    mensajes_por_fecha.reset()
    mensajes_analizados.reset()

    return jsonify({"message": "Base de datos restablecida al estado inicial"}), 200


if __name__ == "__main__":
    app.run(debug=True)
