from django.contrib import admin
from .models import Evento,Bitacora

class EventoAdmin(admin.ModelAdmin):
    list_display=('type',)

class BitacoraAdmin(admin.ModelAdmin):
    readonly_fields=('created',)


admin.site.register(Evento,EventoAdmin)
admin.site.register(Bitacora,BitacoraAdmin)
