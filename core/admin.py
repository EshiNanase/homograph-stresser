from django.contrib import admin
from .models import Homograph, QuasiSynonym
from django.contrib.auth.models import Group, User

admin.site.unregister(Group)
admin.site.unregister(User)


class QuasiSynonymInline(admin.TabularInline):
    model = QuasiSynonym
    fields = ['synonyms', 'initial_weight', 'stress', 'quasi_synonyms']
    extra = 0


@admin.register(Homograph)
class HomographAdmin(admin.ModelAdmin):
    inlines = [QuasiSynonymInline]
    ordering = ['homograph']

    class Meta:
        model = Homograph
