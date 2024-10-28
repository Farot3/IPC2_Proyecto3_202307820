from Sentimiento import Sentimientos


class Analizador:
    def __init__(self):
        self.sentimientos = Sentimientos()
        self.empresas = []
        self.mensajes = []

    def agregar_empresa(self, empresa):
        self.empresas.append(empresa)

    def agregar_mensaje(self, mensaje):
        self.mensajes.append(mensaje)

    def obtener_empresas(self):
        return self.empresas

    def obtener_mensajes(self):
        return self.mensajes

    def obtener_sentimientos(self):
        return self.sentimientos
