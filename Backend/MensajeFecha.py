class MensajesPorFecha:
    def __init__(self):
        self.mensajes_por_fecha = {}

    def agregar_mensaje(self, fecha, mensaje):
        if fecha not in self.mensajes_por_fecha:
            self.mensajes_por_fecha[fecha] = []
        self.mensajes_por_fecha[fecha].append(mensaje)

    def obtener_mensajes(self):
        return self.mensajes_por_fecha

    def reset(self):
        self.mensajes_por_fecha = {}
