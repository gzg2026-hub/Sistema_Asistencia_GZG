from datetime import time

class AttendanceConfig:
    def __init__(
        self,
        hora_inicio_dia: time = time(7, 0),
        hora_fin_dia: time = time(19, 0),
        hora_inicio_noche: time = time(19, 0),
        hora_fin_noche: time = time(7, 0),
        tolerancia_entrada_min: int = 10,
        tolerancia_salida_min: int = 10,
        max_exceso_jornada_min: int = 60,
        horas_minimas: float = 12.0,
        jornada_estandar_horas: float = 12.0
    ):
        self.hora_inicio_dia = hora_inicio_dia
        self.hora_fin_dia = hora_fin_dia
        self.hora_inicio_noche = hora_inicio_noche
        self.hora_fin_noche = hora_fin_noche
        self.tolerancia_entrada_min = tolerancia_entrada_min
        self.tolerancia_salida_min = tolerancia_salida_min
        self.max_exceso_jornada_min = max_exceso_jornada_min
        self.horas_minimas = horas_minimas
        self.jornada_estandar_horas = jornada_estandar_horas

