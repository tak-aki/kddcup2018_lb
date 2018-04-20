from django.contrib import admin
from submit.models import SubmitModel, ScoreModel

class SubmitAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'filename', 'submit_timestamp',
                    'score_date_start', 'score_date_end', 'score_avg', 'for_score_simulation')

class ScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'submit', 'score_date', 'score')

admin.site.register(SubmitModel, SubmitAdmin)
admin.site.register(ScoreModel, ScoreAdmin)

