from . import (
    APIView, IsAuthenticated, Response,
    UserDailyPerformanceSerializer, UserOpenAssetSerializer,
    PerformanceCalculator, GetOpenAssets
)


class UserDailyPerformanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        performance = PerformanceCalculator(request.user, 0)
        data = performance.calculate_metrics()
        if not data:
            return Response({"detail": "No daily performance data available."}, status=404)
        serializer = UserDailyPerformanceSerializer(data, many=True)
        return Response(serializer.data)


class UserOpenAssetsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        open_assets_service = GetOpenAssets(request.user, 0)
        data = open_assets_service.get_all()
        serializer = UserOpenAssetSerializer(data, many=True)
        return Response(serializer.data)