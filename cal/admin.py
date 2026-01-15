from django.contrib import admin
from cal.models import Event, Hospital, Setor, TipoPlantao, Enfermeiro

admin.site.register(Hospital)
admin.site.register(Setor)
admin.site.register(TipoPlantao)
admin.site.register(Enfermeiro)
admin.site.register(Event)
