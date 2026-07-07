

from django.db import models
from django.contrib.auth.models import User
import uuid
from core.validators import validar_rut
from django.core.exceptions import ValidationError


    
# GENERADOR DE CÓDIGOS DE BARRA
def generate_barcode(name, is_consumible=True):
    if is_consumible:
        return f"*C{uuid.uuid4().hex[:12].upper()}*"
    else:
        return f"*NC{uuid.uuid4().hex[:12].upper()}*"

# CLASIFICACIÓN
class Clasificacion(models.Model):
    TIPO_CHOICES = [
        ('dispositivo', 'Dispositivo'),
        ('consumible', 'Consumible'),
        ('herramienta', 'Herramienta'),
    ]

    name = models.CharField("Nombre de la categoría", max_length=100)
    tipo = models.CharField("Tipo", max_length=20, choices=TIPO_CHOICES, default='dispositivo')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.name

# MARCA
class Marca(models.Model):
    name = models.CharField("Marca", max_length=100, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"

    def clean(self):
        # Normalizar antes de validar
        nombre_normalizado = self.name.upper().strip()

        # Buscar si ya existe otra marca con ese nombre
        if Marca.objects.filter(name=nombre_normalizado).exclude(pk=self.pk).exists():
            raise ValidationError({"name": f"La marca '{nombre_normalizado}' ya existe."})

    def save(self, *args, **kwargs):
        # Validar ANTES de guardar
        self.full_clean()

        # Normalizar
        if self.name:
            self.name = self.name.upper().strip()

        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# ESTADO
class Estado(models.Model):
    name = models.CharField("Estado", max_length=100, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Estado"
        verbose_name_plural = "Estados"

    def clean(self):
        nombre_normalizado = self.name.upper().strip()

        if Estado.objects.filter(name=nombre_normalizado).exclude(pk=self.pk).exists():
            raise ValidationError({"name": f"El estado '{nombre_normalizado}' ya existe."})

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.name:
            self.name = self.name.upper().strip()

        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# SOLICITANTE
class Solicitante(models.Model):
    name = models.CharField("Nombre",max_length=100)
    rut = models.CharField(
        max_length=12,
        unique=True,
        validators=[validar_rut],
        verbose_name="RUT",
        help_text="Formato: 12345678-9"
        )
    phone = models.CharField("Telefono",max_length=12)
    mail = models.EmailField("Correo Electronico",max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Solicitante"
        verbose_name_plural = "Solicitantes"

    def __str__(self):
        return self.name

# UBICACIÓN
class Ubicacion(models.Model):
    name = models.CharField("Ubicación", max_length=100, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ubicación"
        verbose_name_plural = "Ubicaciones"

    def clean(self):
        nombre_normalizado = self.name.upper().strip()

        if Ubicacion.objects.filter(name=nombre_normalizado).exclude(pk=self.pk).exists():
            raise ValidationError({"name": f"La ubicación '{nombre_normalizado}' ya existe."})

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.name:
            self.name = self.name.upper().strip()

        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# PRODUCTO / KIT
class Producto(models.Model):
    TIPO_CHOICES = [
        ('dispositivo', 'Dispositivo'),
        ('consumible', 'Consumible'),
        ('herramienta', 'Herramienta'),
    ]

    TIPO_ITEM_CHOICES = [
        ('kit', 'Kit'),
        ('individual', 'Individual'),
    ]




    name = models.CharField("Producto", max_length=100)
    barcode = models.CharField("Codigo de barras", max_length=100, unique=True, blank=True, null=True)
    tipo = models.CharField("Tipo de producto", max_length=20, choices=TIPO_CHOICES)
    tipo_item = models.CharField("Kit/Individual", max_length=20, choices=TIPO_ITEM_CHOICES, default='individual')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    photo = models.ImageField("Foto", default='no_image.png')
    brand = models.ManyToManyField(Marca, verbose_name="Marca")
    state = models.ManyToManyField(Estado, verbose_name="Estado")
    location = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, verbose_name="Ubicación")
    stock = models.PositiveIntegerField(default=1)
    kits_generados = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.name} - ({self.barcode})"

    def save(self, *args, **kwargs):
        # Validar antes
        self.full_clean()

        # Códigos de barra
        if self.tipo == 'consumible':
            if not self.barcode:
                base_code = self.name[:6].upper()
                self.barcode = f"C{uuid.uuid4().hex[:10].upper()}"
        else:
            if not self.barcode:
                self.barcode = f"NC{uuid.uuid4().hex[:10]}"


        super().save(*args, **kwargs)




class Solicitud(models.Model):

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('entregada', 'Entregada'),
        ('devuelta', 'Devuelta'),
    ]

    productos = models.ManyToManyField(
        Producto,
        verbose_name="Productos"
    )


    requestor = models.ForeignKey(
        Solicitante,
        on_delete=models.CASCADE,
        verbose_name="Solicitante"
    )
    requested = models.DateTimeField(verbose_name="Fecha de Solicitud")
    returned = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Fecha de Devolución"
    )
    observaciones = models.TextField(null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Solicitud"
        verbose_name_plural = "Solicitudes"

    def __str__(self):
        return f"Solicitud #{self.id} - {self.requestor.name}"

    # ===========================
    # VALIDACIONES
    # ===========================
    def clean(self):

        from django.core.exceptions import ValidationError

        # fecha devolución
        if self.returned and self.requested and self.returned < self.requested:
            raise ValidationError({
                "returned": "La fecha de devolución debe ser posterior a la fecha solicitada."
            })

        # IMPORTANTE:
        # solo validar productos si el objeto YA existe
        if self.pk and self.estado == "entregada":

            for producto in self.productos.all():

                estados = producto.state.values_list("name", flat=True)

                if "EN USO" in estados:
                    raise ValidationError({
                        'productos': f"El producto '{producto.name}' ya está en uso."
                    })

        # devolución requiere fecha
        if self.estado == "devuelta" and not self.returned:
            raise ValidationError({
                'returned': "Debes ingresar la fecha de devolución."
            })

    # ===========================
    # MARCAR COMO EN USO
    # ===========================
    def marcar_en_uso(self):

        en_uso, _ = Estado.objects.get_or_create(name="EN USO")

        for producto in self.productos.all():
            producto.state.set([en_uso])
            producto.save()

    # ===========================
    # MARCAR COMO DISPONIBLE
    # ===========================
    def marcar_disponible(self):

        disponible, _ = Estado.objects.get_or_create(name="DISPONIBLE")

        for producto in self.productos.all():
            producto.state.set([disponible])
            producto.save()

    # ===========================
    # SAVE FINAL
    # ===========================
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

# PROVEEDOR
class Proveedor(models.Model):
    nombre = models.CharField("Nombre Proveedor", max_length=100)
    rut = models.CharField("RUT", max_length=20, unique=True,help_text="Formato: 12345678-9")
    telefono = models.CharField("Teléfono", max_length=20)
    email = models.EmailField("Correo Electrónico")
    direccion = models.CharField("Dirección", max_length=200)
    fecha_despacho = models.DateField("Fecha de Despacho")
    created = models.DateTimeField("Creado",auto_now_add=True)
    updated = models.DateTimeField("Modificado",auto_now=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

    def clean(self):
        from core.validators import validar_rut

        # 1. Normalizar RUT (sin espacios)
        rut_normalizado = self.rut.upper().replace(" ", "").replace(".", "")

        # Validación de formato
        try:
            validar_rut(rut_normalizado)
        except ValidationError:
            raise ValidationError({"rut": "El RUT ingresado no es válido."})

        # Duplicado (mostrar error)
        if Proveedor.objects.filter(rut=rut_normalizado).exclude(pk=self.pk).exists():
            raise ValidationError({"rut": f"El proveedor con RUT '{rut_normalizado}' ya existe."})

        # Guardar el RUT normalizado
        self.rut = rut_normalizado

    def save(self, *args, **kwargs):
        self.full_clean()  # Ejecuta clean() y clean_fields()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.rut})"

# COTIZACIÓN
class Cotizacion(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]
    nombre_cotizacion = models.CharField(max_length=100)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='cotizaciones')
    fecha = models.DateField()
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    created = models.DateTimeField("Creado",auto_now_add=True)
    updated = models.DateTimeField("Modificado",auto_now=True)





    class Meta:
        verbose_name = "Cotización"
        verbose_name_plural = "Cotizaciones"

    def __str__(self):
        return f"{self.nombre_cotizacion}"

    def calcular_total(self):
        return sum(item.total for item in self.itemcotizacion_set.all())
    
# ITEM COTIZACIÓN
class ItemCotizacion(models.Model):
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE)
    nombre_producto = models.CharField("Producto", max_length=25)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=0)
    total = models.DecimalField(max_digits=12, decimal_places=0)

    def save(self, *args, **kwargs):
        self.total = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Item Cotización"
        verbose_name_plural = "Items Cotizaciones"


# ORDEN DE COMPRA
class OrdenCompra(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')



    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE,
        related_name='ordenes_compra',
        null=True,       # NECESARIO
        blank=True,      # NECESARIO
        editable=False   # NO editable en admin
    )

    cotizacion = models.ForeignKey(
        Cotizacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Cotización"
    )

    fecha = models.DateField()
    numero_factura = models.CharField(max_length=50,unique=True,   error_messages={
        'unique': "Este número de factura ya está registrado."
    })
    monto_total = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    observaciones = models.TextField(blank=True, null=True)

    created = models.DateTimeField("Creado",auto_now_add=True)
    updated = models.DateTimeField("Modificado",auto_now=True)


    referencia = models.ImageField("Imagen Orden de Compra",
    upload_to="orden_compra/",
    null=True,
    blank=True)


    def __str__(self):
        if self.pk and self.proveedor:
            return f"Orden {self.numero_factura} - {self.proveedor.nombre}"
        return f"Orden nueva"

    def clean(self):
        if OrdenCompra.objects.filter(
            numero_factura=self.numero_factura
        ).exclude(pk=self.pk).exists():
            raise ValidationError({
                'numero_factura': "Este número de factura ya existe en otra orden de compra."
            })

    def calcular_monto_total(self):
        return sum(item.total for item in self.itemordencompra_set.all())

    def save(self, *args, **kwargs):

        # Saber si es nueva OC
        es_nueva = self.pk is None

        # Asignar proveedor automáticamente si la OC tiene cotización
        if es_nueva and self.cotizacion:
            self.proveedor = self.cotizacion.proveedor

        # Guardamos primero para obtener el PK
        super().save(*args, **kwargs)

        # ----------------------------------------------
        #  COPIAR ITEMS DESDE LA COTIZACIÓN (solo si es nueva)
        # ----------------------------------------------
        if es_nueva and self.cotizacion:
            for item in self.cotizacion.itemcotizacion_set.all():
                ItemOrdenCompra.objects.create(
                    orden_compra=self,
                    nombre_producto=item.nombre_producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.precio_unitario,
                    total=item.total
                )

        # ----------------------------------------------
        #  RE-CALCULAR MONTO TOTAL
        # ----------------------------------------------
        self.monto_total = self.calcular_monto_total()
        super().save(update_fields=['monto_total'])


# ITEM ORDEN DE COMPRA
class ItemOrdenCompra(models.Model):
    orden_compra = models.ForeignKey(OrdenCompra, on_delete=models.CASCADE)

    nombre_producto = models.CharField("Producto", max_length=200)  # texto libre
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=0)
    total = models.DecimalField(max_digits=12, decimal_places=0)

    def save(self, *args, **kwargs):
        self.total = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Item Orden de Compra"
        verbose_name_plural = "Items Órdenes de Compra"

class ItemSolicitud(models.Model):
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    procesado = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Item Solicitud"
        verbose_name_plural = "Items Solicitud"

    def clean(self):

        if not self.producto:
            return
        
        

        # Consumible individual: puede pedir varias unidades
        if self.producto.tipo == "consumible" and self.producto.tipo_item == "individual":
            if self.cantidad > self.producto.stock:
                
                raise ValidationError({
                    "cantidad": f"Stock disponible: {self.producto.stock}"
                })

        # Herramienta, dispositivo o kit: solo cantidad 1
        else:
            if self.cantidad != 1:
                raise ValidationError({
                    "cantidad": f"Stock Disponible: {self.producto.stock}"
                })

            if self.producto.stock < 1:
                raise ValidationError({
                    "cantidad": f"Stock insuficiente. Stock disponible: {self.producto.stock}"
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto.name} x {self.cantidad}"