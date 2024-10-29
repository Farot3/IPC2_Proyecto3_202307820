from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
import requests
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
import io

# Create your views here.
def home(request):
    return render(request, "index.html")


def enviando(request):
    if request.method == "POST":
        input = request.POST.get("input")
        urlflask_o_algosimilar = "http://127.0.0.1:5000/procesar"
        response = requests.post(urlflask_o_algosimilar, data={"input": input})
        if response.status_code == 200:
            xml_response = response.text
            return render(request, "index.html", {"datosProcesaods": xml_response})
        else:
            return HttpResponse("Error al enviar los datos")
    return render(request, "index.html")


def consultar_datos(request):
    urlflask_o_algosimilar = "http://127.0.0.1:5000/consultar_datos"
    response = requests.get(urlflask_o_algosimilar)
    if response.status_code == 200:
        xml_response = response.text
        return render(
            request, "consultarDatos.html", {"datosConsultados": xml_response}
        )
    else:
        return HttpResponse("Error al consultar los datos")


def reset(request):
    if request.method == "POST":
        urlflask_o_algosimilar = "http://127.0.0.1:5000/reset"
        response = requests.post(urlflask_o_algosimilar)
        if response.status_code == 200:
            messages.success(request, "Base de datos restablecida al estado inicial")
        else:
            messages.error(request, "Error al restablecer la base de datos")
        return redirect("home")
    return render(request, "index.html")


def ayuda(request):
    return render(request, "ayuda.html")


def cargar_archivo_XML(request):
    if request.method == "POST" and request.FILES["archivo"]:
        archivo = request.FILES["archivo"]
        if archivo.name.endswith(".xml"):
            fs = FileSystemStorage()
            filename = fs.save(archivo.name, archivo)

            # Leer el contenido del archivo como bytes y luego decodificarlo a una cadena usando UTF-8
            with fs.open(filename, "rb") as file:
                file_content = file.read().decode("utf-8")

            return render(request, "index.html", {"file_content": file_content})
        else:
            return HttpResponse("Solo se permiten archivos con extensión .xml")
    return render(request, "cargar_archivo.html")


def peticiones(request):
    return render(request, "peticiones.html")


def resumen_clasificacion_fecha(request):
    if request.method == "POST":
        fecha_seleccionada = request.POST.get("fecha")
        empresa_seleccionada = request.POST.get("empresa")

        # Aquí debes agregar la lógica para obtener los datos del resumen
        # Por ejemplo, puedes hacer una solicitud a la API de Flask para obtener los datos
        urlflask_o_algosimilar = "http://127.0.0.1:5000/obtener_resumen"
        response = requests.post(
            urlflask_o_algosimilar,
            data={"fecha": fecha_seleccionada, "empresa": empresa_seleccionada},
        )

        if response.status_code == 200:
            resumen = response.json()
            print(
                "Resumen obtenido:", resumen
            )  # Agregar un print para verificar el resumen obtenido
            return render(
                request,
                "ResumenClasificacionFecha.html",
                {
                    "fechas": obtener_fechas(),  # Función para obtener las fechas disponibles
                    "empresas": obtener_empresas(),  # Función para obtener las empresas disponibles
                    "resumen": resumen,
                    "fecha_seleccionada": fecha_seleccionada,
                    "empresa_seleccionada": empresa_seleccionada,
                },
            )
        else:
            return HttpResponse("Error al obtener el resumen")
    else:
        return render(
            request,
            "ResumenClasificacionFecha.html",
            {
                "fechas": obtener_fechas(),  # Función para obtener las fechas disponibles
                "empresas": obtener_empresas(),  # Función para obtener las empresas disponibles
            },
        )


def obtener_fechas():
    # Aquí debes agregar la lógica para obtener las fechas disponibles
    # Por ejemplo, puedes hacer una solicitud a la API de Flask para obtener las fechas
    urlflask_o_algosimilar = "http://127.0.0.1:5000/obtener_fechas"
    response = requests.get(urlflask_o_algosimilar)
    if response.status_code == 200:
        fechas = response.json()
        print(
            "Fechas obtenidas:", fechas
        )  # Agregar un print para verificar las fechas obtenidas
        return fechas
    else:
        return []


def obtener_empresas():
    # Aquí debes agregar la lógica para obtener las empresas disponibles
    # Por ejemplo, puedes hacer una solicitud a la API de Flask para obtener las empresas
    urlflask_o_algosimilar = "http://127.0.0.1:5000/obtener_empresas"
    response = requests.get(urlflask_o_algosimilar)
    if response.status_code == 200:
        empresas = response.json()
        print(
            "Empresas obtenidas:", empresas
        )  # Agregar un print para verificar las empresas obtenidas
        return empresas
    else:
        return []


def resumen_rango_fechas(request):
    # Implementar la lógica para resumen por rango de fechas
    return HttpResponse("Resumen por rango de fechas")


def reporte_pdf(request):
    urlflask_o_algosimilar = "http://127.0.0.1:5000/reporte_pdf"
    response = requests.get(urlflask_o_algosimilar)
    if response.status_code == 200:
        pdf_content = response.content
        return FileResponse(io.BytesIO(pdf_content), content_type='application/pdf', filename='reporte.pdf')
    else:
        return HttpResponse("Error al generar el reporte en PDF")


def prueba_mensaje(request):
    if request.method == "POST":
        mensaje = request.POST.get("mensaje")
        urlflask_o_algosimilar = "http://127.0.0.1:5000/prueba_mensaje"
        response = requests.post(urlflask_o_algosimilar, data={"mensaje": mensaje})
        if response.status_code == 200:
            respuesta = response.text
            return render(request, "prueba_mensaje.html", {"respuesta": respuesta})
        else:
            return HttpResponse("Error al analizar el mensaje")
    return render(request, "prueba_mensaje.html")
