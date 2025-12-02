from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Server, Metric
from django.utils import timezone

@api_view(['POST'])
def register_node(request):
    hostname = request.data['hostname']
    ip = request.data['ip']
    server, created = Server.objects.get_or_create(hostname=hostname, defaults={'ip': ip, 'status': 'online'})
    if not created:
        server.last_check_in = timezone.now()
        server.status = 'online'
        server.save()
    return Response({'message': 'registered', 'hostname': hostname})

@api_view(['POST'])
def report_metrics(request):
    hostname = request.data['hostname']
    server = Server.objects.get(hostname=hostname)
    Metric.objects.create(
        server=server,
        cpu=request.data['cpu'],
        memory=request.data['memory'],
        disk=request.data['disk']
    )
    server.last_check_in = timezone.now()
    server.save()
    return Response({'message': 'metrics recorded'})
