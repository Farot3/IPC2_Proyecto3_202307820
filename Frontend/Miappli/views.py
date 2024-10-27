from django.shortcuts import render
from django.http import HttpResponse
import requests


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
