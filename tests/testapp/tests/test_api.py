import os

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST

from drf_attachments.models import Attachment
from testapp.models import Diagram, File, PhotoAlbum, Thumbnail
from testapp.tests.demo_files import DemoFile


# TODO: Test viewable/editable/deletable configuration
# TODO: Test context translations

class TestApi(TestCase):
    def setUp(self):
        super().setUp()
        self.superuser = User.objects.create_superuser(username="superuser")
        self.client.force_login(self.superuser)

        self.photo_album = PhotoAlbum.objects.create(name="album1")
        self.thumbnail = Thumbnail.objects.create(name="thumbnail1")
        self.diagram = Diagram.objects.create(name="diagram1")
        self.file = File.objects.create(name="file1")

    def test_get_all_attachments(self):
        # prepare data
        self.create_attachment(
            name="attach1",
            context=settings.ATTACHMENT_CONTEXT_WORK_PHOTO,
            content_object=self.photo_album,
            file_name=DemoFile.JPG,
        )
        self.create_attachment(
            name="attach2",
            context=settings.ATTACHMENT_DEFAULT_CONTEXT,
            content_object=self.diagram,
            file_name=DemoFile.SVG,
        )

        # GET all attachments
        response = self.client.get(path=f'/api/attachment/')
        self.assertEqual(HTTP_200_OK, response.status_code, response.content)

        # check response
        response_data = response.json()
        self.assertEqual(2, len(response_data))
        self.assertEqual("attach1", response_data[0]["name"])
        self.assertEqual(settings.ATTACHMENT_CONTEXT_WORK_PHOTO, response_data[0]["context"])
        self.assertEqual("attach2", response_data[1]["name"])
        self.assertEqual(settings.ATTACHMENT_DEFAULT_CONTEXT, response_data[1]["context"])

    def test_get_attachments_of_entity(self):
        # prepare data
        self.create_attachment(
            name="attach1",
            context=settings.ATTACHMENT_CONTEXT_WORK_PHOTO,
            content_object=self.photo_album,
            file_name=DemoFile.JPG,
        )
        self.create_attachment(
            name="attach2",
            context=settings.ATTACHMENT_DEFAULT_CONTEXT,
            content_object=self.diagram,
            file_name=DemoFile.SVG,
        )

        # GET all attachments of PhotoAlbum1
        response = self.client.get(path=f'/api/photo_album/{self.photo_album.pk}/')
        self.assertEqual(HTTP_200_OK, response.status_code, response.content)

        # check response
        response_data = response.json()
        attachments = response_data["attachments"]
        self.assertEqual(1, len(attachments))
        attachment = attachments[0]
        self.assertEqual("attach1", attachment["name"])
        self.assertEqual(settings.ATTACHMENT_CONTEXT_WORK_PHOTO, attachment["context"])

    def test_download(self):
        # create attachment
        attachment = self.create_attachment(
            name="attach1",
            context=settings.ATTACHMENT_CONTEXT_WORK_PHOTO,
            content_object=self.photo_album,
            file_name=DemoFile.JPG,
        )

        # get attachment from main serializer
        response = self.client.get(path=f'/api/attachment/')
        attachment_response = response.json()[0]
        # TODO: download_url is not provided by main serializer. intentional?

        # get attachment from sub-serializer
        response = self.client.get(path=f'/api/photo_album/{self.photo_album.pk}/')
        attachment_response = response.json()["attachments"][0]
        download_url = attachment_response["download_url"]
        self.assertIsNotNone(download_url)
        self.assertGreater(len(download_url), 0)

        # download
        response = self.client.get(download_url)

        # check response
        self.assertEqual(
            f'attachment; filename="{attachment.name}{attachment.get_extension()}"',
            response.get("Content-Disposition")
        )

        # check content
        with DemoFile(DemoFile.JPG) as demo_file:
            expected_content = demo_file.read()
        self.assertEqual(expected_content, response.getvalue())

    def test_invalid_file_extension_is_rejected(self):
        response = self.upload_attachment(
            name="Attachment with invalid extension",
            context=settings.ATTACHMENT_DEFAULT_CONTEXT,
            content_object_path=f"photo_album/{self.photo_album.pk}",
            file_name=DemoFile.XYZ,
        )
        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code, response.content)
        self.assertEqual(0, len(Attachment.objects.all()))

    def test_invalid_mime_type_is_rejected(self):
        response = self.upload_attachment(
            name="Attachment with invalid mime type",
            context=settings.ATTACHMENT_DEFAULT_CONTEXT,
            content_object_path=f"photo_album/{self.photo_album.pk}",
            file_name=DemoFile.EMPTY_JPG,
        )
        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code, response.content)
        self.assertEqual(0, len(Attachment.objects.all()))

    def test_basic_upload(self):
        """
        Performs a basic attachment upload and checks properties of the model and physical file.
        """
        file_size = 24_819  # Bytes

        # upload basic attachment
        response = self.upload_attachment(
            name="My Attachment",
            content_object_path=f"photo_album/{self.photo_album.pk}",
            context=settings.ATTACHMENT_DEFAULT_CONTEXT,
            file_name=DemoFile.JPG,
        )
        self.assertEqual(HTTP_201_CREATED, response.status_code, response.content)

        # check attachment model
        attachments = Attachment.objects.all()
        self.assertEqual(1, attachments.count())
        attachment = attachments.first()
        self.assertEqual("My Attachment", attachment.name)
        self.assertEqual(settings.ATTACHMENT_DEFAULT_CONTEXT, attachment.context)
        self.assertEqual("image/jpeg", attachment.get_mime_type())
        self.assertEqual(file_size, attachment.get_size())
        self.assertEqual(".jpg", attachment.get_extension())

        # check physical file
        self.assertTrue(os.path.isfile(attachment.file.path))
        self.assertEqual(file_size, os.path.getsize(attachment.file.path))

    def test_multi_attachment_upload(self):
        # upload first attachment
        response = self.upload_attachment(
            name="My First Attachment",
            context=settings.ATTACHMENT_CONTEXT_WORK_PHOTO,
            content_object_path=f"photo_album/{self.photo_album.pk}",
            file_name=DemoFile.JPG,
        )
        self.assertEqual(HTTP_201_CREATED, response.status_code, response.content)

        # check attachment model
        attachments = Attachment.objects.all()
        self.assertEqual(1, attachments.count())

        # check photo album model
        photo_album_attachments = self.photo_album.attachments.all()
        self.assertEqual(1, len(photo_album_attachments))
        self.assertEqual(attachments.first(), photo_album_attachments.first())

        # upload second attachment
        response = self.upload_attachment(
            name="My Second Attachment",
            context=settings.ATTACHMENT_CONTEXT_WORK_PHOTO,
            content_object_path=f"photo_album/{self.photo_album.pk}",
            file_name=DemoFile.PDF,
        )

        self.assertEqual(HTTP_201_CREATED, response.status_code, response.content)

        # check attachment model
        attachments = Attachment.objects.all()
        self.assertEqual(2, attachments.count())
        self.assertSetEqual({"My First Attachment", "My Second Attachment"}, {att.name for att in attachments})
        self.assertSetEqual({self.photo_album.pk}, {att.object_id for att in attachments})

        # check photo album model
        photo_album_attachments = self.photo_album.attachments.all()
        self.assertEqual(2, len(photo_album_attachments))

    def test_unique_upload(self):
        # upload first attachment
        response = self.upload_attachment(
            name="First Photo",
            context=settings.ATTACHMENT_CONTEXT_WORK_PHOTO,
            content_object_path=f"diagram/{self.diagram.pk}",
            file_name=DemoFile.SVG,
        )
        self.assertEqual(HTTP_201_CREATED, response.status_code, response.content)

        # check attachment model
        attachments = Attachment.objects.all()
        self.assertEqual(1, attachments.count())
        attachment = attachments[0]
        first_attachment_file_path = attachment.file.path

        # check diagram model
        diagram_attachments = self.diagram.attachments.all()
        self.assertEqual(1, len(diagram_attachments))
        self.assertEqual(attachments.first(), diagram_attachments.first())

        # upload second attachment with different context
        response = self.upload_attachment(
            name="Second Photo",
            context=settings.ATTACHMENT_CONTEXT_VACATION_PHOTO,
            content_object_path=f"diagram/{self.diagram.pk}",
            file_name=DemoFile.SVG,
        )
        self.assertEqual(HTTP_201_CREATED, response.status_code, response.content)

        # check attachment model
        attachments = Attachment.objects.all()
        self.assertEqual(1, attachments.count())
        attachment = attachments.first()
        self.assertEqual("Second Photo", attachment.name)
        self.assertEqual(self.diagram.pk, attachment.object_id)

        # check diagram model
        diagram_attachments = self.diagram.attachments.all()
        self.assertEqual(1, len(diagram_attachments))

        # check that the old file was deleted
        self.assertFalse(os.path.isfile(first_attachment_file_path))

    def test_unique_per_context_upload(self):
        # upload first attachment
        response = self.upload_attachment(
            name="First Work Photo",
            context=settings.ATTACHMENT_CONTEXT_WORK_PHOTO,
            content_object_path=f"thumbnail/{self.thumbnail.pk}",
            file_name=DemoFile.JPG,
        )
        self.assertEqual(HTTP_201_CREATED, response.status_code, response.content)

        # check attachment model
        attachments = Attachment.objects.all()
        self.assertEqual(1, attachments.count())

        # check diagram model
        thumbnail_attachments = self.thumbnail.attachments.all()
        self.assertEqual(1, len(thumbnail_attachments))
        self.assertEqual(attachments.first(), thumbnail_attachments.first())

        # upload second attachment with same context
        response = self.upload_attachment(
            name="Second Work Photo",
            context=settings.ATTACHMENT_CONTEXT_WORK_PHOTO,
            content_object_path=f"thumbnail/{self.thumbnail.pk}",
            file_name=DemoFile.JPG,
        )
        self.assertEqual(HTTP_201_CREATED, response.status_code, response.content)

        # check attachment model
        attachments = Attachment.objects.all()
        self.assertEqual(1, attachments.count())
        attachment = attachments.first()
        self.assertEqual("Second Work Photo", attachment.name)
        self.assertEqual(self.thumbnail.pk, attachment.object_id)

        # check diagram model
        thumbnail_attachments = self.thumbnail.attachments.all()
        self.assertEqual(1, len(thumbnail_attachments))

        # upload third attachment with different context
        response = self.upload_attachment(
            name="Vacation Photo",
            context=settings.ATTACHMENT_CONTEXT_VACATION_PHOTO,
            content_object_path=f"thumbnail/{self.thumbnail.pk}",
            file_name=DemoFile.JPG,
        )
        self.assertEqual(HTTP_201_CREATED, response.status_code, response.content)

        # check attachment model
        attachments = Attachment.objects.all()
        self.assertEqual(2, attachments.count())
        self.assertSetEqual({"Second Work Photo", "Vacation Photo"}, {att.name for att in attachments})
        self.assertSetEqual({self.thumbnail.pk}, {att.object_id for att in attachments})

        # check diagram model
        thumbnail_attachments = self.thumbnail.attachments.all()
        self.assertEqual(2, len(thumbnail_attachments))

    def test_attachment_object_is_deleted_with_content_object(self):
        # add an attachment to File model
        self.create_attachment(
            name="attach1",
            context=settings.ATTACHMENT_DEFAULT_CONTEXT,
            content_object=self.file,
            file_name=DemoFile.PDF,
        )

        # delete the File model
        response = self.client.delete(f"/api/file/{self.file.pk}/")
        self.assertEqual(HTTP_204_NO_CONTENT, response.status_code, response.content)

        # check that the attachment was deleted as well
        self.assertEqual(0, len(Attachment.objects.all()))

    def test_physical_file_is_deleted_with_content_object(self):
        # add an attachment to File model
        attachment = self.create_attachment(
            name="attach1",
            context=settings.ATTACHMENT_DEFAULT_CONTEXT,
            content_object=self.file,
            file_name=DemoFile.PDF,
        )
        file_path = attachment.file.path

        # check that the physical file was created successfully
        self.assertTrue(os.path.isfile(file_path))
        self.assertGreater(os.path.getsize(file_path), 100)

        # delete the model object
        response = self.client.delete(f"/api/file/{self.file.pk}/")
        self.assertEqual(HTTP_204_NO_CONTENT, response.status_code, response.content)

        # check that the physical file was deleted
        self.assertFalse(os.path.isfile(file_path))

    def test_min_upload_size_is_enforced(self):
        # try to upload a File < min_size
        response = self.upload_attachment(
            name="too_small",
            context=settings.ATTACHMENT_DEFAULT_CONTEXT,
            content_object_path=f"file/{self.file.pk}",
            file_name=DemoFile.SVG,  # has 703 Bytes; 1_000 Bytes are required
        )
        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code, response.content)

        # check that the attachment was not created
        self.assertEqual(0, len(Attachment.objects.all()))

    def test_max_upload_size_is_enforced(self):
        # try to upload a File > max_size
        response = self.upload_attachment(
            name="too_big",
            context=settings.ATTACHMENT_DEFAULT_CONTEXT,
            content_object_path=f"file/{self.file.pk}",
            file_name=DemoFile.JPG,  # has 24_819 Bytes; 10_000 Bytes are allowed
        )
        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code, response.content)

        # check that the attachment was not created
        self.assertEqual(0, len(Attachment.objects.all()))

    @override_settings(ATTACHMENT_MAX_UPLOAD_SIZE=702)
    def test_max_upload_size_from_settings_is_enforced(self):
        # try to upload a File > settings.ATTACHMENT_MAX_UPLOAD_SIZE
        response = self.upload_attachment(
            name="too_big_for_settings",
            context=settings.ATTACHMENT_DEFAULT_CONTEXT,
            content_object_path=f"diagram/{self.diagram.pk}",
            file_name=DemoFile.SVG,  # has 703 Bytes
        )
        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code, response.content)

        # check that the attachment was not created
        self.assertEqual(0, len(Attachment.objects.all()))

    def upload_attachment(self, name: str, content_object_path: str, file_name: str, context: str):
        with DemoFile(file_name) as file:
            return self.client.post(
                path=f'/api/attachment/',
                data={
                    "name": name,
                    "context": context,
                    "content_object": f"http://any.domain/api/{content_object_path}/",
                    "file": file,
                },
            )

    @staticmethod
    def create_attachment(name: str, context: str, content_object: object, file_name: str) -> Attachment:
        with DemoFile(file_name, as_django_file=True) as file:
            return Attachment.objects.create(
                name=name,
                context=context,
                content_object=content_object,
                file=file,
            )
