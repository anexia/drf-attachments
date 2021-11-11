# Django Attachments

A django module to manage any model's file up-/downloads by relating an Attachment model to it.

## Installation

Install using pip:

```
pip install git+https://github.com/anexia-it/django-attachments@main
```

Add model_prefix to your INSTALLED_APPS list. Make sure it is the first app in the list

```
INSTALLED_APPS = [
    ...
    'django_attachments',
    ...
]
```

Add the `ATTACHMENT_MAX_UPLOAD_SIZE` to your `settings.py`:
```
# settings relevant for attachments app
ATTACHMENT_MAX_UPLOAD_SIZE = env.int("ATTACHMENT_MAX_UPLOAD_SIZE", default=1024 * 1024 * 25)
```

Define any context choices your attachment files might represent (e.g. "driver's license", "offer", "contract", ...)
as `ATTACHMENT_CONTEXT_CHOICES` in the `settings.py`. We recommend defining each context type as constant before 
adding them to the "choices" dict, e.g.:
```
ATTACHMENT_CONTEXT_DRIVERS_LICENSE = 'DRIVERS_LICENSE'
ATTACHMENT_CONTEXT_OFFER = 'OFFER'
ATTACHMENT_CONTEXT_CONTRACT = 'CONTRACT'
ATTACHMENT_CONTEXT_OTHER = 'OTHER'
ATTACHMENT_CONTEXT_CHOICES = (
    ("ATTACHMENT_CONTEXT_DRIVERS_LICENSE", _("Driver's license")),
    ("ATTACHMENT_CONTEXT_OFFER", _("Offer")),
    ("ATTACHMENT_CONTEXT_CONTRACT", _("Contract")),
    ("ATTACHMENT_CONTEXT_OTHER", _("Other")),
)
```

You may also define a default context in the `settings.py` that will be set automatically each time you save an 
attachment without explicitely defining a context yourself. This `ATTACHMENT_DEFAULT_CONTEXT` must then be included in
the `ATTACHMENT_CONTEXT_CHOICES`:
```
ATTACHMENT_DEFAULT_CONTEXT = 'ATTACHMENT'
...
ATTACHMENT_CONTEXT_CHOICES = (
    ...
    ("ATTACHMENT_DEFAULT_CONTEXT", _("Attachment")),
)
```

## Usage

Attachments accept any other Model as content_object and store the uploaded files in their respective directories
(if not defined otherwise in attachment_upload_path)

To manage file uploads for any existing model you must create a one-to-many "attachments" relation to it, via following these steps:
1. Add a generic relation in the model class that is supposed to manage file uploads, e.g. users.UserVehicle:
    ```
    # related_query_name enables filtering for Attachment.objects.filter(users_uservehicles=...)
    attachments = GenericRelation(
        "attachments.Attachment",
        related_query_name="%(app_label)s_%(class)ss",  # "users_uservehicles"
    )
    ```
2. Add the AttachmentMeta class with the relevant restrictions to the newly referenced model class (e.g. users.UserVehicle). If not defined otherwise, the default settings will be used for validation:
    ```
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

    E.g. in users.UserVehicle model class to allow only a single Attachment (driver's license) that must be an image
    (jpg/png):
    class AttachmentMeta:
        valid_mime_types = ['image/jpeg', 'image/png']
        valid_extensions = ['.jpg', '.jpeg', '.jpe', '.png']
        unique_upload = True
    ```

3. Add the newly referenced model (e.g. users.UserVehicle) as HyperlinkedRelatedField to the AttachmentSerializer's content_object, e.g.:
    ```
    content_object = GenericRelatedField({
        UserVehicle: serializers.HyperlinkedRelatedField(
            queryset=UserVehicle.objects.all(),
            view_name='vehicle-detail',
        ),  # user-vehicle
        ...
    )
    ```
4. Optional: Add the newly referenced model (e.g. users.UserVehicle) as OR-filter to any relevant AttachmentQuerySet methods, e.g.:
    ```
    queryset = self.filter(
        Q(
            users_uservehicles__user=user,  # user's vehicle registrations
        ),
        ...
    )
    ```

5. Add attachment DRF route
   ```
   from django_attachments.rest.views import AttachmentViewSet
   
   router = get_api_router()
   router.register(r"attachment", AttachmentViewSet)
   ```
