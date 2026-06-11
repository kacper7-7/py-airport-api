from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from airport.models import AirplaneType, Airplane


class AirplaneImageApiTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="password",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.airplane_type = AirplaneType.objects.create(
            name="Boeing"
        )

        self.airplane = Airplane.objects.create(
            name="Boeing 737",
            rows=30,
            seats_in_row=6,
            airplane_type=self.airplane_type
        )

    def test_upload_image_to_airplane(self):
        url = reverse(
            "airport:airplane-upload-image",
            kwargs={"pk":self.airplane.pk}
        )

        image = SimpleUploadedFile(
            name="airplane.jpg",
            content=(
                b"\x47\x49\x46\x38\x39\x61\x01\x00"
                b"\x01\x00\x80\x00\x00\x00\x00\x00"
                b"\xff\xff\xff\x21\xf9\x04\x01\x00"
                b"\x00\x00\x00\x2c\x00\x00\x00\x00"
                b"\x01\x00\x01\x00\x00\x02\x02\x44"
                b"\x01\x00\x3b"
            ),
            content_type="image/gif"
        )

        response_1 = self.client.post(
            url,
            data={"image":image},
            format="multipart"
        )

        self.airplane.refresh_from_db()

        self.assertEqual(response_1.status_code, status.HTTP_200_OK)
        self.assertTrue(self.airplane.image)

    def test_regular_user_cannot_upload_image_to_airplane(self):
        regular_user = get_user_model().objects.create_user(
            email="regular@test.com",
            password="password"
        )
        self.client.force_authenticate(regular_user)

        url = reverse(
            "airport:airplane-upload-image",
            kwargs={"pk": self.airplane.id}
        )

        image = SimpleUploadedFile(
            name="airport.jpg",
            content=(
                b"\x47\x49\x46\x38\x39\x61\x01\x00"
                b"\x01\x00\x80\x00\x00\x00\x00\x00"
                b"\xff\xff\xff\x21\xf9\x04\x01\x00"
                b"\x00\x00\x00\x2c\x00\x00\x00\x00"
                b"\x01\x00\x01\x00\x00\x02\x02\x44"
                b"\x01\x00\x3b"
            ),
            content_type="image/gif"
        )

        response = self.client.post(
            url,
            data={"image": image},
            format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)