from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
from django.utils.timezone import now
from .models import Evento,Bitacora
from django.contrib.auth.decorators import login_required 
from django.core.paginator import Paginator #para poder hacer paginas
from django.db.models import Q
from .forms import LogsForm


def bitacora(request):
    eventos=Evento.objects.all()
    bitacora=Bitacora.objects.all().order_by('-created')
    busqueda = request.GET.get('busqueda','')     #se obtiene el query
    fecha = request.GET.get('fecha','')     #se obtiene fecha
    if busqueda:  #metodo del formulario (para validar que se buscó algo)
        bitacora=bitacora.filter(Q(title__contains=busqueda)|Q(event__type__contains=busqueda)|Q(author__username__contains=busqueda))    #se busca por titulo, evento o autor
        
    if fecha:
        bitacora=bitacora.filter(Q(created__date=fecha))  #se busca por fecha

    paginator = Paginator(bitacora.order_by('-created'), 6)
    page_number = request.GET.get("page")   #el primer GET es de protocolo, el segundo es de capturar
    page_obj = paginator.get_page(page_number)  #lista que recibe los objetos
    return render(request, "bitacora/bitacora.html",{"page_obj":page_obj,"eventos":eventos,'busqueda':busqueda,'bitacora':bitacora,'fecha':fecha})

   
def eventos(request,evento):
    eventos=get_object_or_404(Evento,type=evento)        #para que pueda generar la vista del error 404, es para usar el nombre de la categoria en el url
    nav=Evento.objects.all()        #este es para mostrar las categorias en el nav
    bitacora=Bitacora.objects.filter(event=eventos)       #aca se hace un filtro en los registros por categoria que se recibe del request
    paginator = Paginator(bitacora.order_by('-created'), 6)
    page_number = request.GET.get("page")   #el primer GET es de protocolo, el segundo es de capturar
    page_obj = paginator.get_page(page_number)  #lista que recibe los objetos
    return render(request, 'bitacora/eventos.html',{"page_obj":page_obj,"eventos":eventos,"nav":nav})

@login_required(login_url="/accounts/login/")
def registrar(request):     #funcion para agregar nuevo registro en bitacora
    log_form=LogsForm() #instancia vacia para cargar formulario
    if request.method =='POST': #si se reciben datos:
        log_form=LogsForm(request.POST, request.FILES)  #carga datos y archivos adjuntos en formulario
        if log_form.is_valid(): #valida los datos
            log=log_form.save(commit=False) #guarda, pero no envia para agregar campos automaticos adicionales
            log.date=now()  #fecha y hora actual
            log.author=request.user #usuario logeado
            log.save()  #guarda y envia
            return redirect(reverse('bitacora')+'?ok')  #registro ok
        else:
            log_form=LogsForm() #se vacia si no es valido
    return render(request, "bitacora/nuevo.html",{'form':log_form}) 
