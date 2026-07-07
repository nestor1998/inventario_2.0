from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.utils.timezone import now
from django.contrib import messages
from .models import Producto, Clasificacion, Marca, Estado, Ubicacion
from bitacora.models import Bitacora
import pandas as pd
from io import BytesIO
import uuid

# Vista de inicio del sistema
def home(request):
    return render(request, "core/home.html")

# Diccionario para mapear categorías visibles en UI a valores guardados en base de datos
TIPO_MAPPING = {
    'Consumibles': 'consumible',
    'Dispositivos': 'dispositivo',
    'Herramientas': 'herramienta'
}

# Vista principal de productos con búsqueda y paginación
def producto(request):
    # Captura parámetros GET del navegador
    busqueda = request.GET.get('busqueda', '').strip()
    tipo = request.GET.get('tipo', '').strip().lower()

    productos = Producto.objects.all()  # Obtiene todos los productos

    # Filtro de búsqueda por nombre o código de barras
    if busqueda:
        productos = productos.filter(
            Q(name__icontains=busqueda) | Q(barcode__icontains=busqueda)
        )

    # Filtro por tipo de producto (categoría)
    if tipo:
        productos = productos.filter(tipo__iexact=tipo)

    # Ordenar por fecha de creación (más recientes primero)
    productos = productos.order_by('-created')

    # Paginación: 12 productos por página
    paginator = Paginator(productos, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Renderiza la vista enviando datos al template
    return render(request, 'core/productos.html', {
        "page_obj": page_obj,
        "busqueda": busqueda,
        "tipo": tipo,
        "category": None
    })

# Vista filtrada por categorías (Consumibles, Herramientas, Dispositivos)
def categoria(request, category_name):
    busqueda = request.GET.get('busqueda', '').strip()

    tipo_mapping = {'Consumibles': 'consumible', 'Dispositivos': 'dispositivo', 'Herramientas': 'herramienta'}
    tipo = tipo_mapping.get(category_name, None)

    productos = Producto.objects.all()

    # Filtra por categoría seleccionada
    if tipo:
        productos = productos.filter(tipo__iexact=tipo)

    # Búsqueda dentro de esa categoría
    if busqueda:
        productos = productos.filter(
            Q(name__icontains=busqueda) | Q(barcode__icontains=busqueda)
        )

    productos = productos.order_by('-created')

    paginator = Paginator(productos, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/categorias.html', {
        "page_obj": page_obj,
        "category": category_name,
        "busqueda": busqueda,
        "tipo": tipo,
        "nav": [{'name': k} for k in tipo_mapping.keys()]
    })

# Genera códigos de barras usando UUID
def generate_barcode(name, is_consumible=True):
    if is_consumible:
        return f"*C{uuid.uuid4().hex[:12].upper()}*"
    else:
        return f"*NC{uuid.uuid4().hex[:12].upper()}*"

# Manejo de stock: crear copias nuevas o aumentar stock según tipo de producto
def actualizar_stock(producto, quantity=1, action='add'):
    if action == 'add':
        if producto.tipo != 'consumible':
            estado_cerrado, _ = Estado.objects.get_or_create(name='CERRADO')

            # Para productos no consumibles, crea copias individuales con códigos distintos
            for _ in range(quantity):
                nuevo_producto = Producto.objects.create(
                    name=producto.name,
                    tipo=producto.tipo,
                    location=producto.location,
                    author=producto.author,
                    stock=1,
                    barcode=generate_barcode(producto.name, is_consumible=False)
                )
                nuevo_producto.brand.set(producto.brand.all())
                nuevo_producto.state.set([estado_cerrado])
            return f'Se crearon {quantity} copias nuevas de {producto.name}'
        else:
            # Para consumibles solo se aumenta stock
            producto.stock += quantity
            producto.save()
            return f'Stock aumentado en {quantity} unidades para {producto.name}. Nuevo stock: {producto.stock}'
    
    elif action == 'subtract':
        # Verifica stock suficiente antes de descontar
        if producto.stock >= quantity:
            producto.stock -= quantity
            producto.save()
            return f'Stock disminuido en {quantity} unidades para {producto.name}. Nuevo stock: {producto.stock}'
        else:
            return f'No hay suficiente stock de {producto.name}. Stock actual: {producto.stock}'

# Vista para escanear código y agregar stock
def scan_product(request):
    if request.method == 'POST':
        barcode = request.POST.get('barcode', '').strip().strip('*')
        quantity = int(request.POST.get('quantity', 1))

        producto = Producto.objects.filter(barcode__iexact=barcode).first()

        if producto:
            msg = actualizar_stock(producto, quantity, 'add')
            messages.success(request, msg)
        else:
            messages.error(request, 'Producto no encontrado')

        return redirect('scan_product')

    return render(request, 'core/scan_product.html')

# Vista para gestionar inventario manualmente (sumar o restar stock)
def gestionar_stock(request):
    if request.method == 'POST':
        barcode = request.POST.get('barcode', '').strip().strip('*')
        action = request.POST.get('action')

        try:
            quantity = max(int(request.POST.get('quantity', 1)), 1)
        except ValueError:
            quantity = 1
        
        producto = Producto.objects.filter(barcode__iexact=barcode).first()

        if producto:
            msg = actualizar_stock(producto, quantity, action)

            if action == 'add':
                messages.success(request, msg)
            else:
                if 'No hay suficiente' in msg:
                    messages.error(request, msg)
                else:
                    messages.success(request, msg)
        else:
            messages.error(request, f'Producto no encontrado con código: {barcode}')
        
        return redirect(f'/gestionar-stock/?active_form={action}')
    
    active_form = request.GET.get('active_form', 'add')
    return render(request, 'core/gestionar_stock.html', {'active_form': active_form})

# Exporta inventario a Excel con pandas y BytesIO
def excel_productos(request):
    categoria = request.GET.get('categoria')
    busqueda = request.GET.get('busqueda', '')
    productos = Producto.objects.all()
    
    if categoria:
        tipo = TIPO_MAPPING.get(categoria)
        if tipo:
            productos = productos.filter(tipo=tipo)

    if busqueda:
        productos = productos.filter(Q(name__icontains=busqueda) | Q(barcode__icontains=busqueda))
    
    data = []
    for producto in productos:
        data.append({
            'Nombre': producto.name,
            'Categoría': producto.tipo.title(),
            'Marca': ', '.join([m.name for m in producto.brand.all()]),
            'Ubicación': producto.location.name,
            'Estado': ', '.join([e.name for e in producto.state.all()]),
            'Stock': producto.stock,
            'Código de Barras': producto.barcode,
            'Fecha de Creación': producto.created.strftime('%d-%m-%Y %H:%M:%S'),
            'Última Actualización': producto.updated.strftime('%d-%m-%Y %H:%M:%S'),
        })
    
    df = pd.DataFrame(data)
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    df.to_excel(writer, sheet_name='Productos', index=False)

    workbook = writer.book
    worksheet = writer.sheets['Productos']

    # Formato encabezado
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#CCE5FF',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })

    for idx, col in enumerate(df.columns):
        max_length = max(df[col].astype(str).apply(len).max(), len(col)) + 2
        worksheet.set_column(idx, idx, max_length)

    worksheet.add_table(
        0, 0, len(df), len(df.columns)-1,
        {'columns':[{'header':c} for c in df.columns], 'style':'Table Style Medium 2'}
    )
    
    writer.close()
    output.seek(0)

    response = HttpResponse(
        output, 
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=Inventario_Productos_{now().strftime("%d-%m-%Y_%H-%M-%S")}.xlsx'
    return response

# Importa productos desde archivo Excel
def import_products(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']

        try:
            df = pd.read_excel(excel_file)
            expected_columns = ['Nombre', 'Marca', 'Estado', 'Categoria', 'Ubicación', 'Cantidad']
            missing_columns = [col for col in expected_columns if col not in df.columns]

            if missing_columns:
                messages.error(request, f'Faltan las columnas: {", ".join(missing_columns)}')
                return redirect('import_products')

            # Renombrado interno de columnas
            df = df.rename(columns={
                'Nombre':'nombre',
                'Marca':'marca',
                'Estado':'estado',
                'Categoria':'tipo',
                'Ubicación':'ubicacion',
                'Cantidad':'cantidad'
            })

            for idx, row in df.iterrows():
                try:
                    location, _ = Ubicacion.objects.get_or_create(name=row['ubicacion'].strip())
                    brand, _ = Marca.objects.get_or_create(name=row['marca'].strip())
                    state, _ = Estado.objects.get_or_create(name=row['estado'].strip())
                    tipo = TIPO_MAPPING.get(row['tipo'].strip())

                    if not tipo:
                        messages.error(request, f'Tipo de producto inválido en fila {idx+2}: {row["tipo"]}')
                        continue

                    cantidad = int(row['cantidad'])

                    # Si el producto no es consumible y hay más de uno, crear productos independientes
                    if tipo != 'consumible' and cantidad > 1:
                        for _ in range(cantidad):
                            producto = Producto.objects.create(
                                name=row['nombre'].strip(),
                                tipo=tipo,
                                location=location,
                                author=request.user,
                                stock=1,
                                barcode=generate_barcode(row['nombre'], is_consumible=False)
                            )
                            producto.brand.set([brand])
                            producto.state.set([state])
                    else:
                        producto = Producto.objects.create(
                            name=row['nombre'].strip(),
                            tipo=tipo,
                            location=location,
                            author=request.user,
                            stock=cantidad
                        )
                        producto.barcode = generate_barcode(row['nombre'], is_consumible=(tipo=='consumible'))
                        producto.save()
                        producto.brand.set([brand])
                        producto.state.set([state])

                except Exception as e:
                    messages.error(request, f'Error fila {idx+2}: {str(e)}')
                    continue

            messages.success(request, 'Productos importados correctamente')

        except Exception as e:
            messages.error(request, f'Error al importar: {str(e)}')

        return redirect('import_products')

    return render(request, 'core/import_products.html')

# Muestra registros de la bitácora con paginación
def bitacora(request):
    registros = Bitacora.objects.all().order_by('-created')
    paginator = Paginator(registros, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'bitacora/bitacora.html', {'registros': page_obj})


def cotizaciones_web(request):
    return render(request, "core/cotizaciones_web.html")
