import re
from django.core.exceptions import ValidationError

def validar_rut(value):
    """
    Valida un RUT chileno, ya sea de persona o empresa.
    Debe venir sin puntos, con guion antes del dígito verificador.
    Ejemplo: 12345678-5 o 76543210-K
    """
    # Validar formato general
    if not re.match(r'^\d{7,9}-[\dkK]$', value):
        raise ValidationError(
            "El RUT debe estar en formato XXXXXXXX-X o XXXXXXXXX-X sin puntos."
        )

    cuerpo, dv = value.split('-')
    cuerpo = cuerpo.strip()
    dv = dv.lower()

    # Cálculo del dígito verificador (módulo 11)
    multiplicador = 2
    suma = 0

    for c in reversed(cuerpo):
        suma += int(c) * multiplicador
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2

    dv_calc = 11 - (suma % 11)

    if dv_calc == 11:
        dv_calc = '0'
    elif dv_calc == 10:
        dv_calc = 'k'
    else:
        dv_calc = str(dv_calc)

    if dv != dv_calc:
        raise ValidationError("RUT inválido.")