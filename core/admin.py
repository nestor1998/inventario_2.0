


from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
import uuid

from .models import (
    Producto, Marca, Estado, Ubicacion, Solicitante, Solicitud,
    Proveedor, Cotizacion, ItemCotizacion, OrdenCompra, ItemOrdenCompra,
    Elemento,ItemSolicitud
)

# ==========================================================
#  ADMIN ELEMENTO
# ==========================================================
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError






class ItemSolicitudInline(admin.TabularInline):
    model = ItemSolicitud
    extra = 1
    fields = ['producto', 'cantidad']
# ==========================================================
#  INLINE PARA ELEMENTOS (solo para kits)
# ==========================================================
class ElementoInline(admin.TabularInline):
    model = Elemento
    extra = 1
    fields = ['nombre', 'cantidad_real', 'cantidad_actual']
    verbose_name = "Elemento del Kit"
    verbose_name_plural = "Elementos del Kit"

# ==========================================================
#  ADMIN PRODUCTO
# ==========================================================
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['name', 'barcode', 'stock', 'tipo', 'tipo_item', 'location', 'estados', 'created', 'updated']
    search_fields = ['name', 'barcode']
    list_filter = ['tipo', 'tipo_item', 'brand', 'state', 'location']
    readonly_fields = ['created', 'updated']
    filter_horizontal = ['brand', 'state']

    fieldsets = [
        ('InformaciÃ³n Principal', {
            'fields': ['name', 'tipo_item', 'tipo', 'barcode', 'photo', 'stock']
        }),
        ('UbicaciÃ³n y Estado', {
            'fields': ['brand', 'state', 'location']
        }),
        ('InformaciÃ³n Adicional', {
            'fields': ['author'],
            'classes': ['collapse']
        }),
        ('Fechas', {
            'fields': ['created', 'updated'],
            'classes': ['collapse']
        }),
    ]

#####

####
        
        
        
    # Mostrar los estados (ManyToMany) como texto en el admin
    def estados(self, obj):
        return ", ".join([estado.name for estado in obj.state.all()])
    estados.short_description = "Estado"

    # Mostrar inline de elementos SOLO en kits
    def get_inline_instances(self, request, obj=None):
        if obj and obj.tipo_item == 'kit':
            return [ElementoInline(self.model, self.admin_site)]
        return []

    # Cuando creas un kit, al guardar te manda a la pantalla de ediciÃ³n del mismo
    def response_add(self, request, obj, post_url_continue=None):
        if obj.tipo_item == 'kit':
            return HttpResponseRedirect(f"/admin/core/producto/{obj.id}/change/")
        return super().response_add(request, obj, post_url_continue)

    # AquÃ­ clonamos despuÃ©s de guardar M2M e inlines
    def save_related(self, request, form, formsets, change):

        super().save_related(request, form, formsets, change)

        producto = form.instance

        # Solo cortar edición si NO es kit
        if change and producto.tipo_item != 'kit':
            return

        # ============================================
        # KITS
        # ============================================
        if (
            producto.tipo_item == 'kit'
            and producto.stock > 1
            and producto.elementos.exists()
            and not producto.kits_generados
        ):

            cantidad = producto.stock

            producto.stock = 1
            producto.save(update_fields=['stock'])

            estado_disp, _ = Estado.objects.get_or_create(
                name="DISPONIBLE"
            )

            for _ in range(cantidad - 1):

                nuevo = Producto.objects.create(
                    name=producto.name,
                    tipo_item='kit',
                    tipo=producto.tipo,
                    stock=1,
                    location=producto.location,
                    author=producto.author,
                    kits_generados=True,
                    photo=producto.photo,
                    
                )

                nuevo.brand.set(producto.brand.all())
                nuevo.state.set([estado_disp])

                for elem in producto.elementos.all():
                    Elemento.objects.create(
                        kit=nuevo,
                        nombre=elem.nombre,
                        cantidad_real=elem.cantidad_real,
                        cantidad_actual=elem.cantidad_actual,
                    )

            producto.kits_generados = True
            producto.save(update_fields=['kits_generados'])

            return

        # ============================================
        # CONSUMIBLES
        # ============================================
        # NO se clonan.
        # El stock representa la cantidad disponible.
        if producto.tipo == 'consumible':
            return

        # ============================================
        # HERRAMIENTAS Y DISPOSITIVOS
        # ============================================
        if (
            producto.tipo in ['herramienta', 'dispositivo']
            and producto.tipo_item == 'individual'
            and producto.stock > 1
        ):

            cantidad = producto.stock

            # El original queda como una unidad
            producto.stock = 1
            producto.save(update_fields=['stock'])

            for _ in range(cantidad - 1):

                nuevo = Producto.objects.create(
                    name=producto.name,
                    tipo_item='individual',
                    tipo=producto.tipo,
                    stock=1,
                    location=producto.location,
                    author=producto.author,
                    photo=producto.photo,
                )

                nuevo.brand.set(producto.brand.all())
                nuevo.state.set(producto.state.all())
                    
                    
    def get_readonly_fields(self, request, obj=None):

        readonly = list(self.readonly_fields)

        # Al editar productos serializados
        if obj and obj.tipo != 'consumible':

            readonly.extend([
                'stock',
                
            ])

        return readonly                  
                        
    
# ==========================================================
#  ADMIN MARCA / ESTADO / UBICACIÃ“N / SOLICITANTE
# ==========================================================
@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ['name', 'created', 'updated']
    search_fields = ['name']

@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ['name', 'created', 'updated']
    search_fields = ['name']

@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ['name', 'created', 'updated']
    search_fields = ['name']

@admin.register(Solicitante)
class SolicitanteAdmin(admin.ModelAdmin):
    list_display = ['name', 'rut', 'phone', 'mail']
    search_fields = ['name', 'rut', 'mail']

# ==========================================================
#  ADMIN PROVEEDOR
# ==========================================================
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'rut', 'telefono', 'email', 'fecha_despacho', 'created', 'updated']
    search_fields = ['nombre', 'rut', 'email']
    list_filter = ['fecha_despacho']
    readonly_fields = ['created', 'updated']

# ==========================================================
#  ADMIN SOLICITUD (1 Ã­tem por solicitud)
# ==========================================================
class ItemSolicitudInline(admin.TabularInline):
    model = ItemSolicitud
    extra = 1
    fields = ['producto', 'cantidad']




@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):

    list_display = [
        'requestor',

        'estado',
        'requested',
        'returned'
    ]

    search_fields = [
        'requestor__name',
        'requestor__rut',
        'productos__name'
    ]

    list_filter = [
        'estado',
        'requested',
        'returned'
    ]

    readonly_fields = [
        'created',
        'updated'
    ]

    inlines = [ItemSolicitudInline]

    autocomplete_fields = ['requestor']

    fieldsets = [
        

        ('Datos del Solicitante', {
            'fields': ['requestor']
        }),

        ('Fechas y Estado', {
            'fields': [
                'estado',
                'requested',
                'returned'
            ]
        }),

        ('Observaciones', {
            'fields': ['observaciones'],
            'classes': ['collapse']
        }),

        ('AuditorÃ­a', {
            'fields': ['created', 'updated'],
            'classes': ['collapse']
        }),
    ]

    def mostrar_productos(self, obj):
        return ", ".join([p.name for p in obj.productos.all()])

    mostrar_productos.short_description = "Productos"

    def save_related(self, request, form, formsets, change):

        super().save_related(request, form, formsets, change)

        solicitud = form.instance

        en_uso, _ = Estado.objects.get_or_create(name="EN USO")
        disponible, _ = Estado.objects.get_or_create(name="DISPONIBLE")

        for item in solicitud.itemsolicitud_set.all():

            producto = item.producto

            # ENTREGAR
            if solicitud.estado == "entregada" and not item.procesado:

                if producto.tipo == "consumible" and producto.tipo_item == "individual":

                    if item.cantidad > producto.stock:
                        messages.error(
                            request,
                            f"No hay stock suficiente de {producto.name}. Stock actual: {producto.stock}"
                        )
                        continue

                    producto.stock -= item.cantidad
                    producto.save(update_fields=["stock"])

                else:
                    producto.state.set([en_uso])

                item.procesado = True
                item.save(update_fields=["procesado"])

            # DEVOLVER
            elif solicitud.estado == "devuelta" and item.procesado:

                if producto.tipo == "consumible" and producto.tipo_item == "individual":
                    producto.stock += item.cantidad
                    producto.save(update_fields=["stock"])

                else:
                    producto.state.set([disponible])

                item.procesado = False
                item.save(update_fields=["procesado"])

# ==========================================================
#  ADMIN COTIZACIÃ“N
# ==========================================================
class ItemCotizacionInline(admin.TabularInline):
    model = ItemCotizacion
    extra = 1
    readonly_fields = ['total']
    fields = ['nombre_producto', 'cantidad', 'precio_unitario', 'total']

@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    inlines = [ItemCotizacionInline]
    list_display = ['id','nombre_cotizacion', 'proveedor', 'fecha', 'estado', 'total_cotizacion']
    list_filter = ['estado', 'proveedor', 'fecha']
    search_fields = ['proveedor__nombre']
    readonly_fields = ['created', 'updated']

    def total_cotizacion(self, obj):
        return obj.calcular_total()

@admin.register(ItemCotizacion)
class ItemCotizacionAdmin(admin.ModelAdmin):
    list_display = ['cotizacion_info', 'nombre_producto', 'cantidad', 'precio_unitario', 'total']
    search_fields = ['nombre_producto', 'cotizacion__nombre_cotizacion']
    readonly_fields = ['total']

    def cotizacion_info(self, obj):
        return f"#{obj.cotizacion.id} - {obj.cotizacion.nombre_cotizacion}"
    cotizacion_info.short_description = "CotizaciÃ³n"


# ==========================================================
#  ADMIN ORDEN COMPRA
# ==========================================================
class ItemOrdenCompraInline(admin.TabularInline):
    model = ItemOrdenCompra
    extra = 1
    fields = ['nombre_producto', 'cantidad', 'precio_unitario', 'total']
    readonly_fields = ['total']



@admin.register(ItemOrdenCompra)
class ItemOrdenCompraAdmin(admin.ModelAdmin):
    list_display = ['orden_compra', 'nombre_producto', 'cantidad', 'precio_unitario', 'total']
    search_fields = ['nombre_producto', 'orden_compra__numero_factura']
    readonly_fields = ['total']



@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = [
        'numero_factura', 'proveedor', 'cotizacion',
        'fecha', 'estado', 'monto_total'
    ]
    list_filter = ['fecha', 'estado', 'proveedor']
    search_fields = ['numero_factura', 'proveedor__nombre']
    readonly_fields = ['created', 'updated', 'monto_total']


    inlines = [ItemOrdenCompraInline]

    #  Ocultar Inline si la orden NO estÃ¡ guardada aÃºn
    def get_inline_instances(self, request, obj=None):
        if obj is None:  #  Al crear una nueva: NO mostrar productos
            return []
        return super().get_inline_instances(request, obj)

    #  Recalcular total cada vez que cambien los items
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        orden = form.instance
        orden.monto_total = orden.calcular_monto_total()
        orden.save(update_fields=['monto_total'])

    def save_model(self, request, obj, form, change):
    # Autocompletar proveedor desde la cotizaciÃ³n seleccionada
        if obj.cotizacion:
            obj.proveedor = obj.cotizacion.proveedor

        super().save_model(request, obj, form, change)



        