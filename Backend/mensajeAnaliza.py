class MensajesAnalizados:
    def __init__(self):
        self.mensajes_analizados = []

    def agregar_mensaje(self, mensaje):
        self.mensajes_analizados.append(mensaje)

    def obtener_mensajes(self):
        return self.mensajes_analizados

    def reset(self):
        self.mensajes_analizados = []
