from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
from django.core.files.storage import FileSystemStorage
from django.contrib import messages


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


def consultar_datos(request):
    # Implementar la lógica para consultar datos
    return HttpResponse("Consultar Datos")


def resumen_clasificacion_fecha(request):
    # Implementar la lógica para resumen de clasificación por fecha
    return HttpResponse("Resumen de clasificación por fecha")


def resumen_rango_fechas(request):
    # Implementar la lógica para resumen por rango de fechas
    return HttpResponse("Resumen por rango de fechas")


def reporte_pdf(request):
    # Implementar la lógica para generar reporte en PDF
    return HttpResponse("Reporte en PDF")


def prueba_mensaje(request):
    # Implementar la lógica para prueba de mensaje
    return HttpResponse("Prueba de mensaje")
