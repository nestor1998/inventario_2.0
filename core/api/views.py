from rest_framework.views import APIView          # Clase base para crear endpoints tipo vista
from rest_framework.response import Response       # Permite devolver respuestas HTTP con JSON
from rest_framework import status                  # Códigos de estado HTTP (200, 201, 400, etc.)
from core.models import Cotizacion                 # Modelo principal de cotizaciones
from .serializers import CotizacionSerializer      # Serializer que convierte Modelo <-> JSON


#   API PARA LISTAR Y CREAR COTIZACIONES
class CotizacionesApi(APIView):
    """
    Vista API que permite dos operaciones:
    - GET  → Listar todas las cotizaciones
    - POST → Crear una nueva cotización desde JSON
    """

    
    #   GET → devuelve todas las cotizaciones en formato JSON
    def get(self, request, *args, **kwargs):
        # Obtener todas las cotizaciones desde la base de datos
        cotizaciones = Cotizacion.objects.all()
        # Serializarlas para convertirlas en JSON
        serializer = CotizacionSerializer(cotizaciones, many=True)
        # Devolver la respuesta con código HTTP 200 (OK)
        return Response(serializer.data, status=status.HTTP_200_OK)
    #   POST → recibe datos y crea una nueva cotización

    def post(self, request, *args, **kwargs):

        # Intentar convertir el JSON recibido a un objeto Cotizacion
        serializer = CotizacionSerializer(data=request.data)

        # Validar los datos recibidos
        if serializer.is_valid():
            # Guardar la nueva cotización en la BD
            cotizacion = serializer.save()
            # Devolver la cotización creada (ya guardada)
            return Response(
                CotizacionSerializer(cotizacion).data,   # Cotización recién creada
                status=status.HTTP_201_CREATED           # Código: creado correctamente
            )
        # Si los datos NO son válidos → devolver errores
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
