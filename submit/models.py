from django.db import models

class SubmitModel(models.Model):
    username = models.CharField(max_length = 20)
    filename = models.CharField(max_length = 50)
    submit_timestamp = models.DateTimeField()
    score_date_start = models.DateField()
    score_date_end = models.DateField()
    score_avg = models.FloatField()


class ScoreModel(models.Model):
    submit = models.ForeignKey(SubmitModel, on_delete=models.CASCADE)
    score_date = models.DateField()
    score = models.FloatField()