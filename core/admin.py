from django.contrib import admin
from .models import Homograph, QuasiSynonym, Feedback, FeedbackWithoutHomograph


class QuasiSynonymInline(admin.TabularInline):
    model = QuasiSynonym
    fields = ['synonyms', 'stress', 'quasi_synonyms']
    extra = 0


@admin.register(Homograph)
class HomographAdmin(admin.ModelAdmin):
    inlines = [QuasiSynonymInline]

    class Meta:
        model = Homograph


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):

    fields = ['user_id', 'homograph', 'homograph_stressed', 'text', 'text_normalized', 'probability', 'correct', 'where_stress_should_be', 'sent_at']

    class Meta:
        model = Feedback


@admin.register(FeedbackWithoutHomograph)
class FeedbackWithoutHomographAdmin(admin.ModelAdmin):

    fields = ['user_id', 'text', 'text_normalized', 'sent_at']

    class Meta:
        model = FeedbackWithoutHomograph
