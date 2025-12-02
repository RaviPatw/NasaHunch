from django.db import models

class Server(models.Model):
    hostname = models.CharField(max_length=200)
    ip = models.GenericIPAddressField()
    last_check_in = models.DateTimeField(null=True)
    status = models.CharField(max_length=20)

class Metric(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    cpu = models.FloatField()
    memory = models.FloatField()
    disk = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
