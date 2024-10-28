class TotalesPorFecha:
    def __init__(self):
        self.totales = {}

    def agregar_totales(self, fecha, positivos, negativos, neutros):
        if fecha not in self.totales:
            self.totales[fecha] = {"positivos": 0, "negativos": 0, "neutros": 0}
        self.totales[fecha]["positivos"] += positivos
        self.totales[fecha]["negativos"] += negativos
        self.totales[fecha]["neutros"] += neutros

    def obtener_totales(self, fecha):
        return self.totales.get(fecha, {"positivos": 0, "negativos": 0, "neutros": 0})

    def reset(self):
        self.totales = {}
