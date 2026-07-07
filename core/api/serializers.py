from rest_framework import serializers   # Importa las herramientas de Django REST Framework
from core.models import Cotizacion, ItemCotizacion, Proveedor  # Modelos que vamos a serializar



#   SERIALIZER DE ITEMS DE COTIZACIÓN

class ItemCotizacionSerializer(serializers.ModelSerializer):
    """
    Serializa cada ítem (producto) dentro de una cotización.
    Convierte el modelo ItemCotizacion → JSON.
    """
    class Meta:
        model = ItemCotizacion          # Modelo asociado
        fields = [                      # Campos que se enviarán al API
            'nombre_producto',
            'cantidad',
            'precio_unitario',
            'total'
        ]



#   SERIALIZER PRINCIPAL DE COTIZACIÓN

class CotizacionSerializer(serializers.ModelSerializer):

    # -------------------- Campos extra NO presentes directamente en el modelo --------------------

    # Trae el nombre del proveedor usando "source"
    # proveedor_nombre = proveedor.nombre
    proveedor_nombre = serializers.CharField(
        source="proveedor.nombre",      # Indica de dónde sacar el valor
        read_only=True                  # Solo lectura (no se usa en POST)
    )

    # Campo calculado → suma total de los productos
    total_cotizacion = serializers.SerializerMethodField()

    # Serializa los items relacionados (itemcotizacion_set)
    items = ItemCotizacionSerializer(
        source="itemcotizacion_set",    # Nombre del reverse relation (Django lo crea automático)
        many=True,                      # Una cotización tiene varios items
        read_only=True                  # No se crean desde este serializer
    )


    # -------------------- Configuración de la clase Meta --------------------
    class Meta:
        model = Cotizacion              # Modelo de base
        fields = [                      # Campos que aparecerán en JSON
            'id',
            'nombre_cotizacion',
            'proveedor',                # ID del proveedor
            'proveedor_nombre',         # Nombre del proveedor (campo extra)
            'fecha',
            'descripcion',
            'estado',
            'items',                    # Lista de productos
            'total_cotizacion',         # Suma total calculada
        ]



    #   MÉTODO QUE CALCULA EL TOTAL DE LA COTIZACIÓN

    def get_total_cotizacion(self, obj):
        """
        Suma el total de cada ítem dentro de la cotización.
        Ejemplo: 3 productos → suma item.total de cada uno.
        """
        return sum(item.total for item in obj.itemcotizacion_set.all())
