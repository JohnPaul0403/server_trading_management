from . import (
    TradingAccountSerializer, TradingAccount, IsAccountOwner, 
    IsAuthenticated, status, viewsets, action, Response,
    AccountMetricsSerializer, AccountDailyPerformanceSerializer,
    OpenAssetSerializer, calculate_metrics, PerformanceCalculator,
    GetOpenAssets, import_trades_from_dataframe, AccountMetrics, SymbolPosition)

from rest_framework.parsers import MultiPartParser

class TradingAccountViewSet(viewsets.ModelViewSet):
    serializer_class = TradingAccountSerializer
    permission_classes = [IsAuthenticated, IsAccountOwner]

    def get_queryset(self):
        return TradingAccount.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['get', 'post'])
    def metrics(self, request, pk=None):
        account = self.get_object()

        if request.method == 'POST':
            # recalculate metrics and save
            metrics = calculate_metrics(account)
            account_metrics, _ = AccountMetrics.objects.update_or_create(
                account=account,
                defaults={
                    'total_trades': metrics['total_trades'],
                    'total_buy_qty': metrics['total_buy_qty'],
                    'total_sell_qty': metrics['total_sell_qty'],
                    'total_buy_cost': metrics['total_buy_cost'],
                    'total_sell_revenue': metrics['total_sell_revenue'],
                    'net_profit_loss': metrics['net_profit_loss'],
                    'symbols_traded': list(metrics['symbols_traded'])
                }
            )
            # update symbol positions
            for symbol, pos in metrics['symbol_positions'].items():
                SymbolPosition.objects.update_or_create(
                    account_metrics=account_metrics,
                    symbol=symbol,
                    defaults={
                        'buy_qty': pos['buy_qty'],
                        'sell_qty': pos['sell_qty'],
                        'position': pos['position'],
                        'avg_buy_price': pos['avg_buy_price'],
                        'avg_sell_price': pos['avg_sell_price'],
                        'open_position': pos['open_position'],
                    }
                )
            return Response({"message": "Metrics recalculated and saved."})

        elif request.method == 'GET':
            try:
                metrics = AccountMetrics.objects.get(account=account)
                serializer = AccountMetricsSerializer(metrics)
                return Response(serializer.data)
            except AccountMetrics.DoesNotExist:
                return Response({"error": "Metrics not calculated yet."}, status=404)

    @action(detail=True, methods=['get'])
    def daily_performance(self, request, pk=None):
        account = self.get_object()
        calculator = PerformanceCalculator(0, account)
        data = calculator.calculate()
        serializer = AccountDailyPerformanceSerializer(data, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def open_assets(self, request, pk=None):
        account = self.get_object()
        open_assets_service = GetOpenAssets(0, account)
        data = open_assets_service.get()
        serializer = OpenAssetSerializer(data, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser])
    def import_trades(self, request, pk=None):
        account = self.get_object()
        file = request.FILES.get('file')

        if not file:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            response = import_trades_from_dataframe(file, account)
            return Response({"message": "Trades imported successfully.", "response": response}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)