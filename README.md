# DRF Attachments

Django module to manage any model's file up-/downloads by relating an Attachment model to it.
The module can be used for extending the Django Admin or for exposing the attachment via Django REST Framework.

## Installation and Setup

1. Install using pip:

```
pip install git+https://github.com/anexia-it/drf-attachments@main
```

2. Add model_prefix to your INSTALLED_APPS list. Make sure it is the first app in the list

```
INSTALLED_APPS = [
    ...
    'drf_attachments',
    ...
]
```

## Usage with Django Admin

1. Add minimal settings

```python
# drf-attachment settings
ATTACHMENT_MAX_UPLOAD_SIZE = 1024 * 1024 * 25
ATTACHMENT_CONTEXT_CONTEXT_1 = "CONTEXT-1"
ATTACHMENT_CONTEXT_CONTEXT_2 = "CONTEXT-2"
```

2. Add `AttachmentInlineAdmin` or `ReadOnlyAttachmentInlineAdmin` to each model that needs attachment

```python
from django.contrib import admin
from drf_attachments.admin import AttachmentInlineAdmin

@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    inlines = [
        AttachmentInlineAdmin,
    ]
```

`ReadOnlyAttachmentInlineAdmin` is useful when attachments should be provided only by REST API. You may consider
extending the classes in order to handle additional permission checks.

## Usage with DRF (ToDo: API needs to be simplified)


1. Add a helper/utils file to your project's source code (e.g. `attachments.py`) and prepare the methods `attachment_content_object_field`, `attachment_context_translatables`, `filter_viewable_content_types`, `filter_editable_content_types` and `filter_deletable_content_types` there.

```
# within app/your_app_name/attachments.py

def attachment_content_object_field():
    """
    Manually define all relations using a GenericRelation to Attachment (teach the package how to map the relation)
    """
    pass


def attachment_context_translatables():
    """
    Manually define all translatable strings of all known context types
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

2. Define the helper/utils methods' paths within your `settings.py` as `ATTACHMENT_CONTENT_OBJECT_FIELD_CALLABLE` and `ATTACHMENT_CONTEXT_TRANSLATABLES_CALLABLE`:
```
# within settings.py

ATTACHMENT_CONTENT_OBJECT_FIELD_CALLABLE = "your_app_name.attachments.attachment_content_object_field"
ATTACHMENT_CONTEXT_TRANSLATABLES_CALLABLE = "your_app_name.attachments.attachment_context_translatables"
```

3. Add the `ATTACHMENT_MAX_UPLOAD_SIZE` to your `settings.py`:
```
# within settings.py

ATTACHMENT_MAX_UPLOAD_SIZE = env.int("ATTACHMENT_MAX_UPLOAD_SIZE", default=1024 * 1024 * 25)
```

4. Define any context choices your attachment files might represent (e.g. "driver's license", "offer", "contract", ...) as `ATTACHMENT_CONTEXT_CHOICES` in the `settings.py`. We recommend defining each context type as constant before adding them to the "choices" dict, e.g.:
```
# within settings.py

ATTACHMENT_CONTEXT_DRIVERS_LICENSE = 'DRIVERS_LICENSE'
ATTACHMENT_CONTEXT_OFFER = 'OFFER'
ATTACHMENT_CONTEXT_CONTRACT = 'CONTRACT'
ATTACHMENT_CONTEXT_OTHER = 'OTHER'
```

5. Optionally define a default context in the `settings.py` that will be set automatically each time you save an attachment without explicitly defining a context yourself, e.g.:
```
# within settings.py
...
ATTACHMENT_DEFAULT_CONTEXT = 'ATTACHMENT'
```

6. Add all possible context choices (and the default value, if defined) to the `attachment_context_translatables` method to make them translatable and detectable via the `makemessages` command, e.g.:
```
# within app/your_app_name/attachments.py

from django.utils.translation import ugettext_lazy as _

...

def attachment_context_translatables():
    """
    Manually define all translatable strings of all known context types
    (defined in settings.py via "ATTACHMENT_CONTEXT_x" and "ATTACHMENT_DEFAULT_CONTEXT"
    """
    return {
        settings.ATTACHMENT_CONTEXT_DRIVERS_LICENSE: _("Driver's license")
        settings.ATTACHMENT_CONTEXT_OFFER: _("Offer")
        settings.ATTACHMENT_CONTEXT_CONTRACT: _("Contract")
        settings.ATTACHMENT_CONTEXT_OTHER: _("Other")
        settings.ATTACHMENT_DEFAULT_CONTEXT: _("Attachment"),
    }
    
...
```

## Usage

Attachments accept any other Model as content_object and store the uploaded files in their respective directories
(if not defined otherwise in attachment_upload_path)

To manage file uploads for any existing model you must create a one-to-many "attachments" relation to it, via following these steps:
1. Add a generic relation in the model class that is supposed to manage file uploads, e.g. users.UserVehicle:
    ```
    # within app/your_app_name/users/models/models.py UserVehicle class
   
    # NOTE: since Attachment.object_id is of type CharField, any filters for user vehicle attachments will need to look for its content_type and pk, e.g.:
    # user_vehicle_attachments = AttachmentQuerySet.filter(content_type=user_vehicle_content_type, object_id__in=user_vehicle_pk_list) 
    attachments = GenericRelation(
        "attachments.Attachment",
    )
    ```
2. Add the AttachmentMeta class with the relevant restrictions to the newly referenced model class (e.g. users.UserVehicle). If not defined otherwise, the default settings will be used for validation:
    ```
    # within app/your_app_name/users/models/models.py UserVehicle class
   
    class AttachmentMeta:
        valid_mime_types = []  # allow all mime types
        valid_extensions = []  # allow all extensions
        min_size = 0  # no min size required
        max_size = settings.ATTACHMENT_MAX_UPLOAD_SIZE  # default and max (higher max_size values will be ignored)
        unique_upload = False  # if set to True, the related model will only have one Attachment at a time (when
            adding any further Attachments, previous ones will be deleted permanently); unique_upload=True trumps
            unique_upload_per_context=True, so with unique_upload=True the unique_upload_per_context config will
            be ignored
        unique_upload_per_context = False  # if set to True, the related model will only have one Attachment per
            context at a time (when adding any further Attachments, previous ones with the same context will be
            deleted permanently); unique_upload=True trumps unique_upload_per_context=True, so if you want this
            config, make sure to have unique_upload=False
    ```
    E.g. in users.UserVehicle model class to allow only a single Attachment (driver's license) that must be an image
    (jpg/png):
    ```
    # within app/your_app_name/users/models/models.py UserVehicle class

    class AttachmentMeta:
        valid_mime_types = ['image/jpeg', 'image/png']
        valid_extensions = ['.jpg', '.jpeg', '.jpe', '.png']
        unique_upload = True
    ```

3. Add the newly referenced model (e.g. users.UserVehicle) as HyperlinkedRelatedField to the helper/util file's `attachment_content_object_field` method, e.g.:
    ```
    # within app/your_app_name/attachments.py
   
    def attachment_content_object_field():
        """
        Manually define all relations using a GenericRelation to Attachment (teach the package how to map the relation)
        """
        return GenericRelatedField({
            UserVehicle: serializers.HyperlinkedRelatedField(
                queryset=UserVehicle.objects.all(),
                view_name='vehicle-detail',
            ),  # user-vehicle
            ...
        )

    ...
    ```
   
4. Optional: Add the newly referenced model (e.g. users.UserVehicle) as OR-filter to any relevant queryset filter method within the helper/utils file, e.g.:
    ```
    # within app/your_app_name/attachments.py
   
    from django.contrib.contenttypes.models import ContentType
    from django.db.models import Q
    from django_userforeignkey.request import get_current_user
    
    ...
    
    def filter_viewable_content_types(queryset):
        """
        Return only attachments related to uservehicles belonging to the currently logged in user.
        """
        user = get_current_user()
   
        # NOTE: since Attachment.object_id is of type CharField, we can not directly filter the UserVehicleQuerySet and need to filter for its content_type and pk instead
        user_vehicle_content_type = ContentType.objects.get_for_model(UserVehicle)
        viewable_user_vehicle_ids = list(UserVehicle.objects.filter(user=user).values_list('pk', flat=True))
        queryset = queryset.filter(
            Q(
                content_type=my_cars_content_type,
                object_id__in=viewable_user_vehicle_ids,  # user's own vehicles' attachments
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
   ```
   # app/your_app_name/within urls.py
   
   from drf_attachments.rest.views import AttachmentViewSet
   
   router = get_api_router()
   router.register(r"attachment", AttachmentViewSet)
   ```
