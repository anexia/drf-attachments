# DRF Attachments

Django module to manage any model's file up-/downloads by relating an Attachment model to it.

The module can be used for extending the Django Admin or for exposing the attachment via Django REST Framework (DRF).
If used with DRF, `django-filter` is an additional requirement.

## Installation and Setup

1. Install using pip:

```shell
pip install git+https://github.com/anexia/drf-attachments@main
```

2. Integrate `drf_attachments` into your `settings.py`

```python
INSTALLED_APPS = [
    # ...
    'drf_attachments',
    # ...
]
```

3. Configure attachment settings

```python
# Attachments Configuration

ATTACHMENT_MAX_UPLOAD_SIZE = 1024 * 1024 * 25

# Custom context choices to distinguish attachment types
# (must start with `ATTACHMENT_CONTEXT_` to be found automatically)
# Examples contexts: Drivers License Front, Drivers License Back
ATTACHMENT_CONTEXT_FOO = "foo"
ATTACHMENT_CONTEXT_BAR = "bar"
# ...

# Default in case no context is given
ATTACHMENT_DEFAULT_CONTEXT = "attachment"

# Directory where attachments will be stored by default
PRIVATE_ROOT = "media/private"

# Permissions that should be created for all models (optional)
GLOBAL_MODEL_PERMISSIONS = []
```

## Usage with Django Admin

Add `AttachmentInlineAdmin` or `ReadOnlyAttachmentInlineAdmin` to each model that needs attachments

```python
from django.contrib import admin
from drf_attachments.admin import AttachmentInlineAdmin
from testapp.models import PhotoAlbum

@admin.register(PhotoAlbum)
class PhotoAlbumAdmin(admin.ModelAdmin):
    inlines = [
        AttachmentInlineAdmin,
    ]
```

`ReadOnlyAttachmentInlineAdmin` is useful when attachments should be provided only by REST API. You may consider
extending the classes in order to handle additional permission checks.

## Usage with DRF (ToDo: API needs to be simplified)


1. Add a helper/utils file to your project's source code (e.g. `attachments.py`) and prepare the methods `attachment_content_object_field`, `attachment_context_translations`, `filter_viewable_content_types`, `filter_editable_content_types` and `filter_deletable_content_types` there.

```python
# within app/your_app_name/attachments.py

def attachment_content_object_field():
    """
    Manually define all relations using a GenericRelatedField to Attachment (teach the package how to map the relation)
    """
    pass


def attachment_context_translations():
    """
    Manually define context type translations
    (defined in settings.py via "ATTACHMENT_CONTEXT_x" and "ATTACHMENT_DEFAULT_CONTEXT"
    """
    return {}
    

def filter_viewable_content_types(queryset):
    """
    Override to return viewable related content_types.
    """
    return queryset


def filter_editable_content_types(queryset):
    """
    Override to return editable related content_types.
    """
    return queryset


def filter_deletable_content_types(queryset):
    """
    Override to return deletable related content_types.
    """
    return queryset
    
```

2. Define the helper/utils methods' paths within your `settings.py` as `ATTACHMENT_CONTENT_OBJECT_FIELD_CALLABLE` and `ATTACHMENT_CONTEXT_TRANSLATIONS_CALLABLE`:
```python
# within settings.py

ATTACHMENT_CONTENT_OBJECT_FIELD_CALLABLE = "your_app_name.attachments.attachment_content_object_field"
ATTACHMENT_CONTEXT_TRANSLATIONS_CALLABLE = "your_app_name.attachments.attachment_context_translations"
```

3. Add all possible context choices (and the default value, if defined) to the `attachment_context_translations` method to make them detectable via the `makemessages` command, e.g.:
```python
# within app/your_app_name/attachments.py

from django.utils.translation import gettext_lazy as _
from django.conf import settings

def attachment_context_translations():
    """
    Manually define all context type translations
    (defined in settings.py via "ATTACHMENT_CONTEXT_x" and "ATTACHMENT_DEFAULT_CONTEXT"
    """
    return {
        settings.ATTACHMENT_CONTEXT_DRIVERS_LICENSE: _("Driver's license"),
        settings.ATTACHMENT_CONTEXT_OFFER: _("Offer"),
        settings.ATTACHMENT_CONTEXT_CONTRACT: _("Contract"),
        settings.ATTACHMENT_CONTEXT_OTHER: _("Other"),
        settings.ATTACHMENT_DEFAULT_CONTEXT: _("Attachment"),
    }
```

## Usage

Attachments accept any other Model as content_object and store the uploaded files in their respective directories
(if not defined otherwise in attachment_upload_path)

To manage file uploads for any existing model you must create a one-to-many "attachments" relation to it, via following these steps:
1. Add a generic relation in the model class that is supposed to manage file uploads, e.g. users.UserVehicle:
   ```python
   # within app/your_app_name/users/models/models.py UserVehicle class
   from drf_attachments.models.fields import AttachmentRelation
   
   # NOTE: since Attachment.object_id is of type CharField, filters for user-related attachments will need to look for its content_type and pk, e.g.:
   # user_vehicle_attachments = AttachmentQuerySet.filter(content_type=user_vehicle_content_type, object_id=user_vehicle_pk) 
   attachments = AttachmentRelation()
   ```
2. Add the AttachmentMeta class with the relevant restrictions to the newly referenced model class (e.g. users.UserVehicle). If not defined otherwise, the default settings will be used for validation:
   ```python
   # within app/your_app_name/users/models/models.py UserVehicle class
   from django.conf import settings
   
   class AttachmentMeta:
       valid_mime_types = []  # allow all mime types
       valid_extensions = []  # allow all extensions
       min_size = 0  # no min size required
       max_size = settings.ATTACHMENT_MAX_UPLOAD_SIZE  # default and max (higher max_size values will be ignored)
       unique_upload = False  # if set to True, the related model will only have one Attachment at a time (when adding any further Attachments, previous ones will be deleted permanently); unique_upload=True trumps unique_upload_per_context=True, so with unique_upload=True the unique_upload_per_context config will be ignored
       unique_upload_per_context = False  # if set to True, the related model will only have one Attachment per context at a time (when adding any further Attachments, previous ones with the same context will be deleted permanently); unique_upload=True trumps unique_upload_per_context=True, so if you want this config, make sure to have unique_upload=False
   ```
   E.g. in users.UserVehicle model class to allow only a single Attachment (driver's license) that must be an image
   (jpg/png):
   ```python
   # within app/your_app_name/users/models/models.py UserVehicle class

   class AttachmentMeta:
       valid_mime_types = ['image/jpeg', 'image/png']
       valid_extensions = ['.jpg', '.jpeg', '.jpe', '.png']
       unique_upload = True
   ```

3. Add the newly referenced model (e.g. users.UserVehicle) as HyperlinkedRelatedField to the helper/util file's `attachment_content_object_field` method, e.g.:
   ```python
   # within app/your_app_name/attachments.py
   from generic_relations.relations import GenericRelatedField
   from rest_framework import serializers
   
   from testapp.models import PhotoAlbum
   
   def attachment_content_object_field():
       """
       Manually define all relations using a GenericRelatedField to Attachment (teach the package how to map the relation)
       """
       return GenericRelatedField({
           PhotoAlbum: serializers.HyperlinkedRelatedField(
               queryset=PhotoAlbum.objects.all(),
               view_name='photoalbum-detail',
           ),
           # ...
       })
   ```
   
4. Optional: Add the newly referenced model (e.g. testapp.PhotoAlbum) as OR-filter to any relevant queryset filter method within the helper/utils file, e.g.:
   ```python
   # within app/your_app_name/attachments.py
    
   from django.contrib.contenttypes.models import ContentType
   from django.db.models import Q
   from django_userforeignkey.request import get_current_user
    
   from testapp.models import PhotoAlbum
    
   def filter_viewable_content_types(queryset):
       """
       Return only attachments related to PhotoAlbums belonging to the currently logged-in user.
       """
       user = get_current_user()
       content_type = ContentType.objects.get_for_model(PhotoAlbum)
       viewable_ids = list(PhotoAlbum.objects.filter(user=user).values_list('pk', flat=True))
       queryset = queryset.filter(
           Q(
               content_type=content_type,
               object_id__in=viewable_ids,  # user's own attachments
           ),
       )
   
       return queryset
    
   
   def filter_editable_content_types(queryset):
       """
       No attachments are editable
       """
       return queryset.none()
   
   
   def filter_deletable_content_types(queryset):
       """
       Attachments are only deletable for admin (superuser)
       """
       user = get_current_user()
       if user.is_superuser:
           return queryset
   
       return queryset.none()
   ```

5. Add attachment DRF route
   ```python
   # app/your_app_name/within urls.py
   
   from drf_attachments.rest.views import AttachmentViewSet
   from rest_framework import routers
   
   router = routers.DefaultRouter()
   router.register(r"attachment", AttachmentViewSet)
   ```

## Storage settings
Change the directory where attachments will be stored by setting the `storage_location` in `AttachmentMeta` within the model class:
   ```python
   from django.conf import settings
   
   class AttachmentMeta:
     storage_location = 'path/to/another/directory' # default is settings.PRIVATE_ROOT
   ```

## Auto-formatter setup
We use isort (https://github.com/pycqa/isort) and black (https://github.com/psf/black) for local auto-formatting and for linting in the CI pipeline.
The pre-commit framework (https://pre-commit.com) provides GIT hooks for these tools, so they are automatically applied before every commit.

Steps to activate:
* Install the pre-commit framework: `pip install pre-commit` (for alternative installation options see https://pre-commit.com/#install)
* Activate the framework (from the root directory of the repository): `pre-commit install`

Hint: You can also run the formatters manually at any time with the following command: `pre-commit run --all-files`

## Download endpoint

By default, a generic download endpoint is provided to authenticated users, e.g. `http://0.0.0.0:8000/api/attachment/5b948d37-dcfb-4e54-998c-5add35701c53/download/`.

You can customize the authentication requirements e.g. by subclassing `AttachmentViewSet` and providing custom `permission_classes`.

If you use a custom `AttachmentViewSet`, make sure that there still is a registered `attachment-download` URL. 
This URL is used by the `download_url` property in the API and the download link in the admin panel.

## TestApp Setup

```shell
cd tests
python manage.py migrate
python manage.py createsuperuser
# ... enter credentials ...
python manage.py runserver
# The app should now be served on http://localhost:8000
# Browsable API: http://localhost:8000/api
# Admin Panel: http://localhost:8000/admin
```

## Unit Tests

See folder [tests/](tests/). Basically, all endpoints are covered with multiple
unit tests.

Follow below instructions to run the tests.
You may exchange the installed Django and DRF versions according to your requirements. 
:warning: Depending on your local environment settings you might need to explicitly call `python3` instead of `python`.
```bash
# install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# setup environment
pip install -e .

# run tests
cd tests && python manage.py test
```

## ToDos

* Simplify configuration (maybe a default configuration class that can be subclasses for customizations?)
* Remove settings.GLOBAL_MODEL_PERMISSIONS handling (not really related to attachments)?
* Provide default Storage but support custom Storage class
  * => automatically correct file link in admin panel instead of custom "Download" link
* Make context optional or remove default context (currently a context is required by `ChoiceField` in the serializer)
* Remove dependency on `django_userforeignkey`
* Integrate black + isort via pre-commit
* Remove dot from `valid_extensions` definition / make optional
* Change `Attachment.get_*` methods to dynamic properties
* Split into a separate Django and DRF package 
* Allow different attachment configurations per model (e.g. MyModel.photos and MyModel.docs with different constraints)
