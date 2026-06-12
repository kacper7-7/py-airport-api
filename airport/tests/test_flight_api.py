from datetime import datetime
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from airport.models import (
    Route,
    AirplaneType,
    Airplane,
    Airport,
    Flight,
    Order,
    Ticket
)

URL_LIST = reverse("airport:flight-list")


class FlightApiTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="password"
        )

        self.client.force_authenticate(self.user)

        self.airport_1 = Airport.objects.create(
            name="Kraków-Balice",
            closest_big_city="Kraków"
        )

        self.airport_2 = Airport.objects.create(
            name="Warszawa-Chopin",
            closest_big_city="Warszawa"
        )

        self.route = Route.objects.create(
            source=self.airport_1,
            destination=self.airport_2,
            distance=400
        )

        self.airplane_type = AirplaneType.objects.create(
            name="Boeing 737-800"
        )

        self.airplane = Airplane.objects.create(
            name="Boeing 737-800",
            rows=30,
            seats_in_row=6,
            airplane_type=self.airplane_type
        )

        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timedelta(hours=2)
        )

        self.flight_1 = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timedelta(hours=2)
        )

        self.order = Order.objects.create(user=self.user)

        Ticket.objects.create(
            row=1,
            seat=1,
            flight=self.flight,
            order=self.order
        )

        Ticket.objects.create(
            row=1,
            seat=2,
            flight=self.flight,
            order=self.order
        )

        self.airport_3 = Airport.objects.create(
            name="Wroclaw",
            closest_big_city="Wroclaw"
        )

        self.airport_4 = Airport.objects.create(
            name="Gdańsk",
            closest_big_city="Gdańsk"
        )

        self.route_2 = Route.objects.create(
            source=self.airport_3,
            destination=self.airport_4,
            distance=400
        )

        self.flight_2 = Flight.objects.create(
            route=self.route_2,
            airplane=self.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timedelta(hours=2)
        )

    def test_list_flights(self):

        response = self.client.get(URL_LIST)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Flight.objects.count(), 3)
        self.assertEqual(
            response.data["results"][0]["source"],
            self.flight.route.source.name
        )
        self.assertEqual(
            response.data["results"][0]["available_tickets"],
            178
        )

    def test_retrieve_flights(self):

        URL_RETRIEVE = reverse(
            "airport:flight-detail",
            kwargs={"pk": self.flight.id}
        )
        response = self.client.get(URL_RETRIEVE)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.data["available_tickets"],
            178
        )
        self.assertEqual(
            response.data["route"]["source"],
            self.flight.route.source.name
        )
        self.assertEqual(
            response.data["route"]["destination"],
            self.flight.route.destination.name)
        self.assertEqual(
            response.data["airplane"]["name"],
            self.flight.airplane.name)

    def test_filter_flights_by_source(self):

        response = self.client.get(
            URL_LIST,
            {"source": self.airport_3.id}
        )

        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["source"],
            self.flight_2.route.source.name
        )

    def test_filter_flights_by_destination(self):

        response = self.client.get(
            URL_LIST,
            {"destination": self.airport_4.id}
        )

        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["destination"],
            self.flight_2.route.destination.name
        )

    def test_filter_flights_by_airplane(self):

        response = self.client.get(
            URL_LIST,
            {"airplane": self.airplane.id}
        )

        self.assertEqual(len(response.data["results"]), 3)
        self.assertEqual(
            response.data["results"][0]["airplane"],
            self.flight_2.airplane.name
        )

    def test_filter_flights_by_date(self):
        departure_1 = timezone.make_aware(
            datetime(
                2025,
                9,
                25,
                12,
                0
            )
        )
        arrival_1 = departure_1 + timedelta(hours=2)

        departure_2 = timezone.make_aware(
            datetime(
                2025,
                10,
                25,
                12,
                0
            )
        )
        arrival_2 = departure_2 + timedelta(hours=2)

        self.flight_1.departure_time = departure_1
        self.flight_1.arrival_time = arrival_1
        self.flight_1.save()

        self.flight_2.departure_time = departure_2
        self.flight_2.arrival_time = arrival_2
        self.flight_2.save()

        response = self.client.get(
            URL_LIST,
            {"date": "2025-09-25"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.flight_1.id)

    def test_filter_flights_combined(self):
        departure_1 = timezone.make_aware(
            datetime(
                2025,
                9,
                25,
                12,
                0
            )
        )
        arrival_1 = departure_1 + timedelta(hours=2)

        departure_2 = timezone.make_aware(
            datetime(
                2025,
                10,
                25,
                12,
                0
            )
        )
        arrival_2 = departure_2 + timedelta(hours=2)

        # Flight 1
        self.flight_1.departure_time = departure_1
        self.flight_1.arrival_time = arrival_1
        self.flight_1.save()

        # Flight 2
        self.flight_2.departure_time = departure_2
        self.flight_2.arrival_time = arrival_2
        self.flight_2.save()

        response = self.client.get(
            URL_LIST,
            {
                "date": "2025-09-25",
                "source": self.airport_1.id,
                "destination": self.airport_2.id,
                "airplane": self.airplane.id
            }
        )

        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.flight_1.id)
        self.assertEqual(
            response.data["results"][0]["source"],
            self.flight_1.route.source.name
        )

        response = self.client.get(
            URL_LIST,
            {
                "date": "2025-10-25",
                "source": self.airport_3.id,
                "destination": self.airport_4.id,
                "airplane": self.airplane.id
            }
        )

        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.flight_2.id)
        self.assertEqual(
            response.data["results"][0]["source"],
            self.flight_2.route.source.name
        )
