from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from .models import RoomImage


class RoomUploadTests(TestCase):
    def test_upload_saves_photo_and_analysis(self):
        image_buffer = BytesIO()
        Image.new("RGB", (2, 2), color="blue").save(image_buffer, format="PNG")
        image_bytes = image_buffer.getvalue()
        upload = SimpleUploadedFile("room.png", image_bytes, content_type="image/png")
        gemini_client = Mock()
        gemini_client.models.generate_content.return_value = SimpleNamespace(
            text="Mock room analysis"
        )

        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=Path(media_root)):
                with patch("rooms.views.genai.Client", return_value=gemini_client):
                    response = self.client.post("/", {"room_image": upload})

                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["success"])
                self.assertEqual(response.context["analysis"], "Mock room analysis")

                room = RoomImage.objects.get()
                self.assertEqual(room.analysis, "Mock room analysis")
                self.assertTrue(room.image.storage.exists(room.image.name))
                with room.image.open("rb") as saved_image:
                    self.assertEqual(saved_image.read(), image_bytes)

        gemini_client.models.generate_content.assert_called_once()

    def test_upload_uses_cloudinary_storage_and_gemini(self):
        image_buffer = BytesIO()
        Image.new("RGB", (2, 2), color="blue").save(image_buffer, format="PNG")
        image_bytes = image_buffer.getvalue()
        upload = SimpleUploadedFile("room.png", image_bytes, content_type="image/png")
        gemini_client = Mock()
        gemini_client.models.generate_content.return_value = SimpleNamespace(
            text="Mock room analysis"
        )
        cloudinary_payloads = []

        def upload_to_cloudinary(file, **kwargs):
            cloudinary_payloads.append(file.read())
            return {"public_id": "rooms/room"}

        cloudinary_storages = {
            "default": {
                "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
            },
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
            },
        }

        with patch.dict(
            "os.environ",
            {"CLOUDINARY_URL": "cloudinary://test:test@test"},
        ):
            with override_settings(
                STORAGES=cloudinary_storages,
                CLOUDINARY_STORAGE={
                    "CLOUD_NAME": "test",
                    "API_KEY": "test",
                    "API_SECRET": "test",
                },
            ):
                with patch(
                    "cloudinary.uploader.upload",
                    side_effect=upload_to_cloudinary,
                ) as cloudinary_upload:
                    with patch(
                        "cloudinary_storage.storage.MediaCloudinaryStorage._get_url",
                        return_value="https://media.example/rooms/room",
                    ):
                        with patch(
                            "rooms.views.genai.Client",
                            return_value=gemini_client,
                        ):
                            response = self.client.post("/", {"room_image": upload})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["analysis"], "Mock room analysis")
        self.assertEqual(
            response.context["uploaded_image"],
            "https://media.example/rooms/room",
        )
        self.assertEqual(RoomImage.objects.get().image.name, "rooms/room")

        cloudinary_upload.assert_called_once()
        self.assertEqual(cloudinary_payloads, [image_bytes])
        gemini_client.models.generate_content.assert_called_once()
