class Empresa:
    def __init__(self, nombre):
        self.nombre = nombre
        self.servicios = []

    def agregar_servicio(self, servicio):
        self.servicios.append(servicio)

    def obtener_servicios(self):
        return self.servicios
