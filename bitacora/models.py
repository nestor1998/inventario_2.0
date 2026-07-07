from django.db import models
from django.contrib.auth.models import User

class Evento(models.Model):
    type=models.CharField(max_length=40,verbose_name="Tipo")
    class Meta:
        verbose_name="Evento"
        verbose_name_plural="Eventos"

    def __str__(self):
        return self.type

class Bitacora(models.Model):
    title=models.CharField(max_length=40,verbose_name="Título")
    created=models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    event=models.ForeignKey(Evento,on_delete=models.CASCADE,verbose_name="Evento")
    description=models.TextField(verbose_name="Descripción")
    photo=models.ImageField(verbose_name="Foto",null=True,blank=True)
    author=models.ForeignKey(User,default=1,on_delete=models.CASCADE,verbose_name="Autor")

    class Meta:
        verbose_name="Registro"
        verbose_name_plural="Registros"
    
    def __str__(self):
        return self.title