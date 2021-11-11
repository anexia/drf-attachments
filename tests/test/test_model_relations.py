from django.db import models
from django.test import SimpleTestCase
from django.test.utils import isolate_apps


@isolate_apps('tests')
class TestModelDefinition(SimpleTestCase):
    def test_model_definition(self):
        class TestModel(models.Model):
            pass
        self.assertIs(self.apps.get_model('tests', 'TestModel'), TestModel)
