from django.contrib import admin
from submit.models import SubmitFileModel

class SubmitFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'filename', 'submit_timestamp')
    list_display_links = ('id', 'filename')

admin.site.register(SubmitFileModel, SubmitFileAdmin)

