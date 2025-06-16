from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['get'])
@permission_classes([AllowAny])
def get_status_app(request):
    try:
        return Response({
            "status" : "200",
            "message" : "App is running normally"
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "status" : "404",
            "message" : "There is a problem with the app"
        }, status=status.HTTP_404_NOT_FOUND)
