from . import (
    TradeSerializer, viewsets, IsAuthenticated, 
    IsAccountOwner, Trade, action, Response,
    TradingAccount)
from django.utils.dateparse import parse_date

class TradeViewSet(viewsets.ModelViewSet):
    serializer_class = TradeSerializer
    permission_classes = [IsAuthenticated, IsAccountOwner]

    def get_queryset(self):
        return Trade.objects.filter(
            account__user=self.request.user,
            account_id=self.kwargs['account_pk']
        )

    def perform_create(self, serializer):
        account = TradingAccount.objects.get(
            id=self.kwargs['account_pk'],
            user=self.request.user
        )
        return serializer.save(account=account)
    
    @action(detail=False, methods=['get'])
    def ordered(self, request, **kwargs):
        account_id = self.kwargs['account_pk']
        trades = self.get_queryset().order_by('-timestamp')
        serializer = self.get_serializer(trades, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def filter_by(self, request, **kwargs):
        symbol = request.query_params.get('symbol')
        side = request.query_params.get('side')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # this queryset is already filtered for the right account/user
        qs = self.get_queryset()

        if symbol:
            qs = qs.filter(symbol__icontains=symbol)

        if side:
            qs = qs.filter(side=side)

        if start_date:
            try:
                start_date_obj = parse_date(start_date)
                if start_date_obj:
                    qs = qs.filter(timestamp__date__gte=start_date_obj)
            except Exception:
                pass

        if end_date:
            try:
                end_date_obj = parse_date(end_date)
                if end_date_obj:
                    qs = qs.filter(timestamp__date__lte=end_date_obj)
            except Exception:
                pass

        serializer = self.get_serializer(qs.order_by('-timestamp'), many=True)
        return Response(serializer.data)