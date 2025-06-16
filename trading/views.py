from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from datetime import datetime, timedelta
import pandas as pd
import io

from .models import TradingAccount, Trade, PerformanceMetrics, DailyMetrics, AssetPosition
from .serializers import (
    TradingAccountSerializer, TradeSerializer, TradeCreateSerializer,
    PerformanceMetricsSerializer, DailyMetricsSerializer, AssetPositionSerializer,
    CSVUploadSerializer, LiveMetricsSerializer
)

from .services import AlpacaService
from .utils import PerformanceCalculator
from authentication.permissions import IsAccountOwner

class TradingAccountViewSet(viewsets.ModelViewSet):
    serializer_class = TradingAccountSerializer
    permission_classes = [IsAuthenticated, IsAccountOwner]

    def get_queryset(self):
        return TradingAccount.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def sync_alpaca(self, request, pk=None):
        """Sync trades from Alpaca API"""
        account = self.get_object()
        try:
            alpaca_service = AlpacaService(account)
            trades_synced = alpaca_service.sync_trades()

            # Update performance metrics
            calculator = PerformanceCalculator(account)
            calculator.update_metrics()

            return Response({
                'message': f'Successfully synced {trades_synced} trades',
                'last_sync': timezone.now()
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def live_metrics(self, request, pk=None):
        """Get live account metrics from Alpaca"""
        account = self.get_object()
        try:
            alpaca_service = AlpacaService(account)
            metrics = alpaca_service.get_account_info()
            serializer = LiveMetricsSerializer(metrics)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class TradeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['symbol', 'side', 'status', 'strategy']
    ordering_fields = ['timestamp', 'profit_loss', 'quantity']
    ordering = ['-timestamp']

    def get_queryset(self):
        queryset = Trade.objects.filter(account__user=self.request.user)
        days_back = int(self.request.query_params.get('days_back', 30))

        # Filter by account_id if provided
        account_id = self.request.query_params.get('account_id')
        if account_id:
            queryset = queryset.filter(account_id=account_id)

        # Filter by date range
        days_back = self.request.query_params.get('days_back')
        if days_back:
            try:
                days = int(days_back)
                # Calculate the date 'days' ago from now
                cutoff_date = timezone.now() - timezone.timedelta(days=days)
                queryset = queryset.filter(timestamp__gte=cutoff_date)
            except ValueError:
                # Invalid days_back value, ignore the filter
                pass

        # Filter by specific date if provided
        date = self.request.query_params.get('date')
        if date:
            # Parse the date and filter for that specific day
            date_obj = parse_datetime(date)
            if date_obj:
                # Filter for the entire day
                start_of_day = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
                end_of_day = date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
                queryset = queryset.filter(timestamp__range=[start_of_day, end_of_day])

        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return TradeCreateSerializer
        return TradeSerializer

    def perform_create(self, serializer):
        account_id = self.request.data.get('account_id')
        account = get_object_or_404(TradingAccount, id=account_id, user=self.request.user)
        serializer.save(account=account)

        # Update performance metrics after creating trade
        calculator = PerformanceCalculator(account)
        calculator.update_metrics()

    def perform_destroy(self, instance):
        # Custom logic before deletion
        print(f"Deleting trade: {instance}")
        instance.delete()

    @action(detail=False, methods=['get'])
    def daily_summary(self, request):
        """Get daily trading summary"""
        account_id = request.query_params.get('account_id')
        days = int(request.query_params.get('days', 30))

        if not account_id:
            return Response({'error': 'account_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        account = get_object_or_404(TradingAccount, id=account_id, user=request.user)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)

        daily_metrics = DailyMetrics.objects.filter(
            account=account,
            date__range=[start_date, end_date]
        ).order_by('date')

        serializer = DailyMetricsSerializer(daily_metrics, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def upload_csv(self, request):
        """Upload trades from CSV file"""
        serializer = CSVUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        csv_file = serializer.validated_data['file']
        account_id = serializer.validated_data['account_id']
        account = get_object_or_404(TradingAccount, id=account_id, user=request.user)

        try:
            # Read CSV file
            df = pd.read_csv(io.StringIO(csv_file.read().decode('utf-8')))

            # Validate required columns
            required_columns = ['symbol', 'side', 'quantity', 'price', 'timestamp']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response(
                    {'error': f'Missing required columns: {missing_columns}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Process trades
            trades_created = 0
            for _, row in df.iterrows():
                trade_data = {
                    'symbol': row['symbol'],
                    'side': row['side'].lower(),
                    'quantity': row['quantity'],
                    'price': row['price'],
                    'timestamp': pd.to_datetime(row['timestamp']),
                    'commission': row.get('commission', 0),
                    'strategy': row.get('strategy', ''),
                    'notes': row.get('notes', ''),
                }

                # Create trade if it doesn't exist
                trade_id = f"csv_{account.id}_{trades_created}_{timezone.now().timestamp()}"
                trade, created = Trade.objects.get_or_create(
                    trade_id=trade_id,
                    defaults={**trade_data, 'account': account}
                )
                if created:
                    trades_created += 1

            # Update performance metrics
            calculator = PerformanceCalculator(account)
            calculator.update_metrics()

            return Response({
                'message': f'Successfully imported {trades_created} trades',
                'trades_created': trades_created
            })

        except Exception as e:
            return Response(
                {'error': f'Error processing CSV: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

class PerformanceMetricsView(generics.RetrieveAPIView):
    serializer_class = PerformanceMetricsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        account_id = self.kwargs['account_id']
        account = get_object_or_404(TradingAccount, id=account_id, user=self.request.user)
        performance, created = PerformanceMetrics.objects.get_or_create(account=account)

        if created or not performance.updated_at or \
           (timezone.now() - performance.updated_at).seconds > 300:  # Update every 5 minutes
            calculator = PerformanceCalculator(account)
            calculator.update_metrics()
            performance.refresh_from_db()

        return performance


class AssetPositionListView(generics.ListAPIView):
    serializer_class = AssetPositionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        account_id = self.kwargs['account_id']
        account = get_object_or_404(TradingAccount, id=account_id, user=self.request.user)
        return AssetPosition.objects.filter(account=account)
