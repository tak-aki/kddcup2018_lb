from django.db import models

class SubmitModel(models.Model):
    username = models.CharField(max_length = 20)
    filename = models.CharField(max_length = 50)
    submit_timestamp = models.DateTimeField()
    score_date_start = models.DateField()
    score_date_end = models.DateField()
    score_avg = models.FloatField()
    avg_bj_pm25_score = models.FloatField(blank=True, null=True)
    avg_bj_pm10_score = models.FloatField(blank=True, null=True)
    avg_bj_o3_score = models.FloatField(blank=True, null=True)
    avg_ld_pm25_score = models.FloatField(blank=True, null=True)
    avg_ld_pm10_score = models.FloatField(blank=True, null=True)
    for_score_simulation = models.BooleanField(default=False)


class ScoreModel(models.Model):
    submit = models.ForeignKey(SubmitModel, on_delete=models.CASCADE)
    score_date = models.DateField()
    score = models.FloatField()
    bj_pm25_score = models.FloatField(blank=True, null=True)
    bj_pm10_score = models.FloatField(blank=True, null=True)
    bj_o3_score = models.FloatField(blank=True, null=True)
    ld_pm25_score = models.FloatField(blank=True, null=True)
    ld_pm10_score = models.FloatField(blank=True, null=True)