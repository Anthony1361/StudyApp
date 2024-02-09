# from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from home.models import Room

from .serializers import RoomSerializer

# this is the view that will show us all the routes in our api
# other methods can be specified here @api_view(['GET', 'PUT', 'POST'])
@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET /api',
        # an api for people to see all the rooms in our application
        'GET /api/rooms',
        # for a specific room 
        'GET /api/rooms:id'
    ]
    # the safe=False is going to allow the routes[] data, convert into json data
    # return JsonResponse(routes, safe=False)
    return Response(routes)


@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    # many=True is because we are going to serialize many objects and not just one 
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getRoom(request, pk):
    room = Room.objects.get(id=pk)
    # many=False is because we are going to serialize a single object and not many
    serializer = RoomSerializer(room, many=False)
    return Response(serializer.data)