class Mensaje:
    def __init__(self, texto):
        self.texto = texto
        self.positivos = []
        self.negativos = []
        self.servicios = []
        self.neutros_count = 0

    def agregar_positivo(self, palabra):
        self.positivos.append(palabra)

    def agregar_negativo(self, palabra):
        self.negativos.append(palabra)

    def agregar_servicio(self, servicio):
        self.servicios.append(servicio)

    def contar_neutros(self):
        self.neutros_count = min(len(self.positivos), len(self.negativos))

    def obtener_positivos(self):
        return self.positivos

    def obtener_negativos(self):
        return self.negativos

    def obtener_servicios(self):
        return self.servicios

    def obtener_neutros(self):
        return self.neutros_count
