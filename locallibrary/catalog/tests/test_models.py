from django.test import TestCase
from catalog.models import Author

class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Author.objects.create(first_name='John', last_name='Doe')

    def setUp(self):
        self.author = Author.objects.get(id=1)

    def test_first_name_label(self):
        # author = Author.objects.get(id=1)
        field_label = self.author._meta.get_field('first_name').verbose_name
        self.assertEqual(field_label, 'first name')

    # fail:
    def test_date_of_death_label(self):
        # author = Author.objects.get(id=1)
        field_label = self.author._meta.get_field('date_of_death').verbose_name
        self.assertEqual(field_label, 'died')

    def test_first_name_max_length(self):
        # author = Author.objects.get(id=1)
        max_length = self.author._meta.get_field('first_name').max_length
        self.assertEqual(max_length, 100)
    
    def test_object_name_is_last_name_comma_first_name(self):
        # author = Author.objects.get(id=1)
        expected_object_name = f'{self.author.last_name}, {self.author.first_name}'
        self.assertEqual(str(self.author), expected_object_name)

    def test_get_absolute_url(self):
        # author = Author.objects.get(id=1)
        self.assertEqual(self.author.get_absolute_url(), '/catalog/author/1')