import os

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

from drf_attachments.models import Attachment
from testapp.models import Contract, PhotoAlbum, Receipt
from testapp.tests.demo_files import DemoFile


class TestStorageLocation(TestCase):
    """
    Attachments of content objects with different AttachmentMeta.storage_location settings must not
    interfere with each other, no matter which content object was uploaded to last.
    """

    def setUp(self):
        super().setUp()
        self.superuser = User.objects.create_superuser(username="superuser")
        self.client.force_login(self.superuser)

        self.contract = Contract.objects.create(name="contract1")
        self.receipt = Receipt.objects.create(name="receipt1")
        self.photo_album = PhotoAlbum.objects.create(name="album1")

    def test_download_still_works_after_upload_to_other_storage_location(self):
        contract_attachment = self.upload_attachment(
            name="Contract",
            content_object_path=f"contract/{self.contract.pk}",
            file_name=DemoFile.PDF,
        )
        receipt_attachment = self.upload_attachment(
            name="Receipt",
            content_object_path=f"receipt/{self.receipt.pk}",
            file_name=DemoFile.JPG,
        )

        self.assert_download(contract_attachment, DemoFile.PDF)
        self.assert_download(receipt_attachment, DemoFile.JPG)

    def test_download_still_works_after_upload_to_other_storage_location_reversed(self):
        receipt_attachment = self.upload_attachment(
            name="Receipt",
            content_object_path=f"receipt/{self.receipt.pk}",
            file_name=DemoFile.JPG,
        )
        contract_attachment = self.upload_attachment(
            name="Contract",
            content_object_path=f"contract/{self.contract.pk}",
            file_name=DemoFile.PDF,
        )

        self.assert_download(receipt_attachment, DemoFile.JPG)
        self.assert_download(contract_attachment, DemoFile.PDF)

    def test_file_path_resolves_against_own_storage_location(self):
        contract_attachment = self.create_attachment(self.contract, DemoFile.PDF)
        receipt_attachment = self.create_attachment(self.receipt, DemoFile.JPG)
        album_attachment = self.create_attachment(self.photo_album, DemoFile.JPG)

        self.assert_stored_in(contract_attachment, settings.CONTRACT_ROOT)
        self.assert_stored_in(receipt_attachment, settings.RECEIPT_ROOT)
        self.assert_stored_in(album_attachment, settings.PRIVATE_ROOT)

    def test_resaving_attachment_after_upload_to_other_storage_location(self):
        contract_attachment = self.create_attachment(self.contract, DemoFile.PDF)
        self.create_attachment(self.receipt, DemoFile.JPG)

        # re-saving must not fail because the file is looked up in the receipt's storage location
        contract_attachment.name = "renamed"
        contract_attachment.save()

        contract_attachment.refresh_from_db()
        self.assertEqual("renamed", contract_attachment.name)
        self.assertEqual("application/pdf", contract_attachment.get_mime_type())
        self.assert_stored_in(contract_attachment, settings.CONTRACT_ROOT)

    def test_unique_upload_deletes_previous_file_from_own_storage_location(self):
        first_attachment = self.upload_attachment(
            name="First Contract",
            content_object_path=f"contract/{self.contract.pk}",
            file_name=DemoFile.PDF,
        )
        first_file_path = self.stored_path(first_attachment, settings.CONTRACT_ROOT)
        self.assertTrue(os.path.isfile(first_file_path))

        # upload to another storage location in between (Contract defines unique_upload=True)
        self.upload_attachment(
            name="Receipt",
            content_object_path=f"receipt/{self.receipt.pk}",
            file_name=DemoFile.JPG,
        )
        second_attachment = self.upload_attachment(
            name="Second Contract",
            content_object_path=f"contract/{self.contract.pk}",
            file_name=DemoFile.PDF,
        )

        self.assertEqual([second_attachment], list(self.contract.attachments.all()))
        self.assertFalse(os.path.isfile(first_file_path))
        self.assert_stored_in(second_attachment, settings.CONTRACT_ROOT)

    def test_replacing_file_removes_previous_file_from_own_storage_location(self):
        receipt_attachment = self.create_attachment(self.receipt, DemoFile.JPG)
        previous_file_path = self.stored_path(receipt_attachment, settings.RECEIPT_ROOT)

        # upload to another storage location in between
        self.create_attachment(self.contract, DemoFile.PDF)

        with DemoFile(DemoFile.PDF, as_django_file=True) as file:
            receipt_attachment.file = file
            receipt_attachment.save()

        self.assertFalse(os.path.isfile(previous_file_path))
        self.assert_stored_in(receipt_attachment, settings.RECEIPT_ROOT)

    def test_deleting_attachment_removes_file_from_own_storage_location(self):
        contract_attachment = self.create_attachment(self.contract, DemoFile.PDF)
        file_path = self.stored_path(contract_attachment, settings.CONTRACT_ROOT)

        # upload to another storage location in between
        self.create_attachment(self.receipt, DemoFile.JPG)

        contract_attachment.delete()

        self.assertFalse(os.path.isfile(file_path))

    def test_deleting_content_object_removes_file_from_own_storage_location(self):
        contract_attachment = self.create_attachment(self.contract, DemoFile.PDF)
        file_path = self.stored_path(contract_attachment, settings.CONTRACT_ROOT)

        self.contract.delete()

        self.assertEqual(0, Attachment.objects.count())
        self.assertFalse(os.path.isfile(file_path))

    def assert_download(self, attachment: Attachment, file_name: str):
        response = self.client.get(reverse("attachment-download", kwargs={"pk": attachment.pk}))
        self.assertEqual(HTTP_200_OK, response.status_code)

        with DemoFile(file_name) as demo_file:
            expected_content = demo_file.read()
        self.assertEqual(expected_content, response.getvalue())

    def assert_stored_in(self, attachment: Attachment, storage_location: str):
        expected_path = self.stored_path(attachment, storage_location)
        self.assertEqual(expected_path, attachment.file.path)
        self.assertTrue(os.path.isfile(expected_path))

    @staticmethod
    def stored_path(attachment: Attachment, storage_location: str) -> str:
        return os.path.abspath(os.path.join(storage_location, attachment.file.name))

    def upload_attachment(self, name: str, content_object_path: str, file_name: str) -> Attachment:
        with DemoFile(file_name) as file:
            response = self.client.post(
                path="/api/attachment/",
                data={
                    "name": name,
                    "context": settings.ATTACHMENT_DEFAULT_CONTEXT,
                    "content_object": f"http://any.domain/api/{content_object_path}/",
                    "file": file,
                },
            )
        self.assertEqual(HTTP_201_CREATED, response.status_code, response.content)
        return Attachment.objects.get(pk=response.json()["pk"])

    @staticmethod
    def create_attachment(content_object: object, file_name: str) -> Attachment:
        with DemoFile(file_name, as_django_file=True) as file:
            return Attachment.objects.create(
                name=file_name,
                context=settings.ATTACHMENT_DEFAULT_CONTEXT,
                content_object=content_object,
                file=file,
            )
