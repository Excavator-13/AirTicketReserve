from django.db import migrations


def backfill_passenger_flight_cabin(apps, schema_editor):
    Passenger = apps.get_model('orders', 'Passenger')
    RescheduleRequest = apps.get_model('reschedules', 'RescheduleRequest')

    for passenger in Passenger.objects.select_related('order', 'order__flight', 'order__cabin_class').all():
        if passenger.status == 'RESCHEDULED':
            reschedule = RescheduleRequest.objects.filter(passenger=passenger).order_by('-id').first()
            if reschedule:
                passenger.flight_id = reschedule.new_flight_id
                passenger.cabin_class_id = reschedule.new_cabin_id
            else:
                passenger.flight_id = passenger.order.flight_id
                passenger.cabin_class_id = passenger.order.cabin_class_id
        else:
            passenger.flight_id = passenger.order.flight_id
            passenger.cabin_class_id = passenger.order.cabin_class_id
        passenger.save(update_fields=['flight_id', 'cabin_class_id'])


def reverse_backfill(apps, schema_editor):
    Passenger = apps.get_model('orders', 'Passenger')
    Passenger.objects.all().update(flight_id=None, cabin_class_id=None)


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_passenger_flight_cabin'),
        ('reschedules', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(backfill_passenger_flight_cabin, reverse_backfill),
    ]