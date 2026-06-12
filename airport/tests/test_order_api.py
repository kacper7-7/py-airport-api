from datetime import timedelta
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from airport.models import (Order,
                            Ticket,
                            Airport,
                            Route,
                            Airplane,
                            AirplaneType,
                            Flight)


URL_ORDER = reverse("airport:orders-list")


class CreateOrderTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test_password"
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

    def test_create_order(self):
        response = self.client.post(
            URL_ORDER, data={

                "tickets": [
                    {
                        "row": 2,
                        "seat": 2,
                        "flight": self.flight.id
                    }
                ]
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ticket.objects.count(), 1)
        self.assertEqual(Order.objects.count(), 1)

        order = Order.objects.latest("id")
        ticket = order.tickets.first()

        self.assertEqual(order.user, self.user)
        self.assertEqual(ticket.row, 2)
        self.assertEqual(ticket.seat, 2)
        self.assertEqual(ticket.flight, self.flight)

    def test_create_duplicate_ticket(self):
        response = self.client.post(
            URL_ORDER,
            {
                "tickets": [
                    {
                        "row": 2,
                        "seat": 2,
                        "flight": self.flight.id
                    },
                    {
                        "row": 2,
                        "seat": 2,
                        "flight": self.flight.id
                    }
                ]
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(Ticket.objects.count(), 0)

    def test_create_order_with_invalid_row(self):
        response = self.client.post(
            URL_ORDER, data={
                "tickets": [
                    {
                        "row": 999,
                        "seat": 2,
                        "flight": self.flight.id

                    }
                ]
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(Ticket.objects.count(), 0)

    def test_create_order_with_invalid_seat(self):
        response = self.client.post(
            URL_ORDER, data={
                "tickets": [
                    {
                        "row": 1,
                        "seat": 999,
                        "flight": self.flight.id

                    }
                ]
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(Ticket.objects.count(), 0)

    def test_create_order_with_exists_ticket(self):
        order = Order.objects.create(
            user=self.user
        )

        ticket = Ticket.objects.create(
            row=1,
            seat=1,
            flight=self.flight,
            order=order
        )
        response = self.client.post(
            URL_ORDER, data={
                "tickets": [
                    {
                        "row": 1,
                        "seat": 1,
                        "flight": self.flight.id

                    }
                ]
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Ticket.objects.count(), 1)

    def test_create_order_with_empty_tickets_list(self):
        response = self.client.post(
            URL_ORDER,
            {"tickets": []},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(Ticket.objects.count(), 0)

    def test_create_order_without_tickets_field(self):
        response = self.client.post(
            URL_ORDER,
            {},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(Ticket.objects.count(), 0)
