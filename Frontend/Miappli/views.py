from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
from django.core.files.storage import FileSystemStorage


# Create your views here.
def home(request):
    return render(request, "index.html")


def enviando(request):
    if request.method == "POST":
        input = request.POST.get("input")
        urlflask_o_algosimilar = "http://127.0.0.1:5000/procesar"
        response = requests.post(urlflask_o_algosimilar, data={"input": input})
        if response.status_code == 200:
            recibir = response.json().get("datosProcesaods")
            return render(request, "index.html", {"datosProcesaods": recibir})
        else:
            return HttpResponse("Error al enviar los datos")
    return render(request, "index.html")


def ayuda(request):
    return render(request, "ayuda.html")


def cargar_archivo_XML(request):
    if request.method == "POST" and request.FILES["archivo"]:
        archivo = request.FILES["archivo"]
        if archivo.name.endswith(".xml"):
            fs = FileSystemStorage()
            filename = fs.save(archivo.name, archivo)
            uploaded_file_url = fs.url(filename)

            # Leer el contenido del archivo
            with fs.open(filename, "r") as file:
                file_content = file.read()

            return render(request, "index.html", {"file_content": file_content})
        else:
            return HttpResponse("Solo se permiten archivos con extensión .xml")
    return render(request, "cargar_archivo.html")
