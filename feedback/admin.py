from django.contrib import admin
from .models import Feedback, FeedbackWithoutHomograph


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

