class Sentimientos:
    def __init__(self):
        self.positivos = []
        self.negativos = []

    def agregar_positivo(self, palabra):
        self.positivos.append(palabra)

    def agregar_negativo(self, palabra):
        self.negativos.append(palabra)

    def obtener_positivos(self):
        return self.positivos

    def obtener_negativos(self):
        return self.negativos
