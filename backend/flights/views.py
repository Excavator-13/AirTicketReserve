from datetime import datetime

from django.db.models import Q
from rest_framework.views import APIView
from rest_framework import permissions

from common.responses import UnifiedResponse
from common.business_exceptions import BusinessValidationError
from flights.models import Airport, Flight
from flights.serializers import AirportSerializer, FlightListSerializer, FlightDetailSerializer


class CityListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        keyword = request.query_params.get('keyword', '').strip()
        if not keyword:
            airports = Airport.objects.all().order_by('city', 'code')[:20]
        else:
            airports = Airport.objects.filter(
                Q(city__icontains=keyword)
                | Q(name__icontains=keyword)
                | Q(code__icontains=keyword)
            ).order_by('city', 'code')
        serializer = AirportSerializer(airports, many=True)
        return UnifiedResponse.success(data=serializer.data)


class FlightSearchView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        departure_city = request.query_params.get('departure_city', '').strip()
        arrival_city = request.query_params.get('arrival_city', '').strip()
        date_str = request.query_params.get('date', '').strip()
        flight_no = request.query_params.get('flight_no', '').strip()
        is_round_trip = request.query_params.get('is_round_trip', 'false').lower() == 'true'
        return_date_str = request.query_params.get('return_date', '').strip()
        adults = int(request.query_params.get('adults', 1))
        children = int(request.query_params.get('children', 0))
        infants = int(request.query_params.get('infants', 0))

        if adults < 1:
            raise BusinessValidationError(detail='成人数量至少为1', data={'adults': adults})
        if infants > adults:
            raise BusinessValidationError(
                detail='婴儿数量不能超过成人数量',
                data={'infants': infants, 'adults': adults},
            )

        if not departure_city or not arrival_city or not date_str:
            return UnifiedResponse.error(msg='出发城市、到达城市和出发日期为必填项', code=400)

        try:
            departure_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return UnifiedResponse.error(msg='出发日期格式不正确，应为 YYYY-MM-DD', code=400)

        departure_airport_ids = Airport.objects.filter(city__icontains=departure_city).values_list('id', flat=True)
        arrival_airport_ids = Airport.objects.filter(city__icontains=arrival_city).values_list('id', flat=True)

        if not departure_airport_ids or not arrival_airport_ids:
            return UnifiedResponse.success(data={'outbound': [], 'return': []})

        outbound_flights = Flight.objects.filter(
            departure_airport_id__in=departure_airport_ids,
            arrival_airport_id__in=arrival_airport_ids,
            departure_time__date=departure_date,
        ).select_related('departure_airport', 'arrival_airport').prefetch_related('cabin_classes')

        if flight_no:
            outbound_flights = outbound_flights.filter(flight_no__icontains=flight_no)

        outbound_serializer = FlightListSerializer(outbound_flights, many=True)

        result = {
            'outbound': outbound_serializer.data,
        }

        if is_round_trip and return_date_str:
            try:
                ret_date = datetime.strptime(return_date_str, '%Y-%m-%d').date()
            except ValueError:
                return UnifiedResponse.error(msg='返程日期格式不正确，应为 YYYY-MM-DD', code=400)

            return_flights = Flight.objects.filter(
                departure_airport_id__in=arrival_airport_ids,
                arrival_airport_id__in=departure_airport_ids,
                departure_time__date=ret_date,
            ).select_related('departure_airport', 'arrival_airport').prefetch_related('cabin_classes')

            return_serializer = FlightListSerializer(return_flights, many=True)
            result['return'] = return_serializer.data
        elif is_round_trip:
            result['return'] = []

        return UnifiedResponse.success(data=result)


class FlightDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        try:
            flight = Flight.objects.select_related(
                'departure_airport', 'arrival_airport'
            ).prefetch_related('cabin_classes').get(pk=pk)
        except Flight.DoesNotExist:
            return UnifiedResponse.error(msg='航班不存在', code=404)

        serializer = FlightDetailSerializer(flight)
        return UnifiedResponse.success(data=serializer.data)