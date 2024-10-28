class Servicio:
    def __init__(self, nombre):
        self.nombre = nombre
        self.alias = []
        self.totales_por_fecha = {}

    def agregar_alias(self, alias):
        self.alias.append(alias)

    def obtener_alias(self):
        return self.alias

    def agregar_totales_por_fecha(self, fecha, positivos, negativos, neutros):
        if fecha not in self.totales_por_fecha:
            self.totales_por_fecha[fecha] = {
                "positivos": 0,
                "negativos": 0,
                "neutros": 0,
            }
        self.totales_por_fecha[fecha]["positivos"] += positivos
        self.totales_por_fecha[fecha]["negativos"] += negativos
        self.totales_por_fecha[fecha]["neutros"] += neutros

    def obtener_totales_por_fecha(self, fecha):
        return self.totales_por_fecha.get(
            fecha, {"positivos": 0, "negativos": 0, "neutros": 0}
        )
