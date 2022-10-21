import importlib
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from django.conf import settings
from generic_relations.relations import GenericRelatedField

__all__ = [
    # only export the Config "singleton" object
    "config",
]

DEFAULT_CONTEXT_SETTING = "ATTACHMENT_DEFAULT_CONTEXT"


# TODO: Load configuration only once instead of separate on-demand loading
class Config:
    @classmethod
    def get_filter_callable_for_viewable_content_objects(cls) -> Optional[Callable]:
        return cls.get_callable("ATTACHMENT_FILTER_VIEWABLE_CONTENT_OBJECTS_CALLABLE")

    @classmethod
    def get_filter_callable_for_editable_content_objects(cls) -> Optional[Callable]:
        return cls.get_callable("ATTACHMENT_FILTER_EDITABLE_CONTENT_OBJECTS_CALLABLE")

    @classmethod
    def get_filter_callable_for_deletable_content_objects(cls) -> Optional[Callable]:
        return cls.get_callable("ATTACHMENT_FILTER_DELETABLE_CONTENT_OBJECTS_CALLABLE")

    @classmethod
    def get_callable(cls, setting_key) -> Optional[Callable]:
        setting = cls.get_optional_setting(setting_key)
        if not setting:
            return None

        module_name, callable_name = setting.rsplit(".", maxsplit=1)
        module = importlib.import_module(module_name)
        return getattr(module, callable_name)

    @staticmethod
    def get_optional_setting(key, default=None) -> Optional[Any]:
        return getattr(settings, key, default)

    @staticmethod
    def get_setting(key) -> Any:
        return getattr(settings, key)

    @classmethod
    def get_content_object_field(cls) -> GenericRelatedField:
        callable_ = cls.get_callable("ATTACHMENT_CONTENT_OBJECT_FIELD_CALLABLE")
        return callable_()

    @classmethod
    def context_choices(
        cls,
        include_default=True,
        values_list=True,
        translated=True,
    ) -> Union[List[str], Tuple[Tuple[Any, Any]]]:
        """
        Extract all unique context definitions from settings "ATTACHMENT_CONTEXT_*" + "ATTACHMENT_DEFAULT_CONTEXT"
        """

        translations = cls.get_context_translations() if translated else {}

        contexts = cls.get_contexts(include_default)
        context_translation_map = {
            context: translations.get(context, context) for context in contexts
        }

        if values_list:
            return list(set(context_translation_map.values()))
        else:
            return tuple((key, value) for key, value in context_translation_map.items())

    @classmethod
    def get_contexts(cls, include_default) -> Set[str]:
        settings_keys = dir(settings)
        return {
            getattr(settings, key)
            for key in settings_keys
            if cls.__is_context_setting(key, include_default)
        }

    @staticmethod
    def __is_context_setting(key, include_default) -> bool:
        return (
            key.startswith("ATTACHMENT_CONTEXT_") and not key.endswith("_CALLABLE")
        ) or (include_default and key == DEFAULT_CONTEXT_SETTING)

    @classmethod
    def translate_context(cls, context):
        """
        Return only a single context's translation from the manually defined translation dict
        """
        translations = cls.get_context_translations()
        return translations.get(context, context)

    @classmethod
    def get_context_translations(cls) -> Dict[str, str]:
        callable_ = cls.get_callable("ATTACHMENT_CONTEXT_TRANSLATIONS_CALLABLE")
        if callable_:
            return callable_()
        else:
            return {}

    @classmethod
    def default_context(cls) -> str:
        """
        Extract ATTACHMENT_DEFAULT_CONTEXT from the settings (if defined)
        """
        return cls.get_optional_setting(DEFAULT_CONTEXT_SETTING)


config = Config()
