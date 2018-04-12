from django.db import models
from datetime import datetime
import time

class SubmitFileModel(models.Model):
    username = models.CharField(max_length = 20)
    filename = models.CharField(max_length = 50)
    submit_timestamp = models.DateTimeField(default = datetime.now)

class CalculateScoreModel(models.Model):

    username = models.CharField(max_length = 20)
    filename = models.CharField(max_length = 50)
    submit_timestamp = models.DateTimeField()

    def calc(self):
        time.sleep(3)
        return
