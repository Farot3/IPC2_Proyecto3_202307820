import re
from Usuariosos import Usuario
from Lugar import Lugar
from Resocial import RedSocial


class Mensaje:
    def __init__(self, texto):
        self.texto = texto
        self.positivos = []
        self.negativos = []
        self.servicios = []
        self.neutros_count = 0
        self.lugar = self.extraer_lugar()
        self.usuario = self.extraer_usuario()
        self.red_social = self.extraer_red_social()

    def extraer_lugar(self):
        match = re.search(r"lugar y fecha: ([^,]+),", self.texto)
        return Lugar(match.group(1).strip()) if match else Lugar("Lugar no encontrado")

    def extraer_usuario(self):
        match = re.search(r"usuario: ([^\s]+)", self.texto)
        return (
            Usuario(match.group(1).strip())
            if match
            else Usuario("Usuario no encontrado")
        )

    def extraer_red_social(self):
        match = re.search(r"red social: ([^\s]+)", self.texto)
        return (
            RedSocial(match.group(1).strip())
            if match
            else RedSocial("Red social no encontrada")
        )

    def agregar_positivo(self, palabra):
        self.positivos.append(palabra)

    def agregar_negativo(self, palabra):
        self.negativos.append(palabra)

    def agregar_servicio(self, servicio):
        self.servicios.append(servicio)

    def obtener_positivos(self):
        return self.positivos

    def obtener_negativos(self):
        return self.negativos

    def obtener_servicios(self):
        return self.servicios

    def obtener_neutros(self):
        return self.neutros_count

    def __str__(self):
        return f"Mensaje: {self.texto}\nLugar: {self.lugar}\nUsuario: {self.usuario}\nRed Social: {self.red_social}"
