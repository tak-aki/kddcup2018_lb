from django.contrib import admin
from submit.models import SubmitModel

class SubmitAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'filename', 'submit_timestamp', 'score_date_start', 'score_date_end', 'score_avg')
    #list_display_links = ('id')

admin.site.register(SubmitModel, SubmitAdmin)

