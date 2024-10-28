class Servicio:
    def __init__(self, nombre):
        self.nombre = nombre
        self.alias = []

    def agregar_alias(self, alias):
        self.alias.append(alias)

    def obtener_alias(self):
        return self.alias
