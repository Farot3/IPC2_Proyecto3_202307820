class DatosAnalizados:
    def __init__(self):
        self.datos = []

    def agregar_datos(self, datos):
        self.datos.append(datos)

    def obtener_datos(self):
        return self.datos

    def reset(self):
        self.datos = []
