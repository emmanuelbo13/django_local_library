from django.test import TestCase
from django.urls import reverse 
from catalog.models import Author, BookInstance, Book, Genre, Language


class AuthorListView(TestCase):
    @classmethod
    def setUpTestData(cls):
        num_authors = 9 
        for author_id in range(num_authors):
            Author.objects.create(
                first_name=f'Dominique {author_id}',
                last_name=f'Surname {author_id}'
            )
    def test_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_list.html')
    
    def test_pagination_is_five(self):
        response = self.client.get(reverse('authors'))
        self.assertTrue(response.status_code, 200)
        # checking is pagination exists
        self.assertTrue('is_paginated' in response.context)
        # checking if pagination is set to True
        self.assertTrue(response.context['is_paginated'] == True)
        # checking if we have 10 items in the first page
        self.assertEqual(len(response.context['author_list']), 5)

    def test_lists_all_authors(self):
        # Get second page and confirm it has (exactly) remaining 1 items
        response = self.client.get(reverse('authors')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['author_list']), 4)

# import datetime 
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class LoanedBookInstancesByUserListViewTest(TestCase):
#     def setUp(self):
#         # Create two users
#         test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
#         test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

#         test_user1.save()
#         test_user2.save()

#         test_author = Author.objects.create(first_name='Dominique', last_name='Rousseau')   
#         test_genre = Genre.objects.create(name='Fantasy')
#         test_language = Language.objects.create(name='English')
#         test_book = Book.objects.create(
#             title='My Book', 
#             summary= 'My summary',
#             isbn= 'ABCDEFG',
#             authos=test_author, 
#             language=test_language
#         )

#         # test_genres = ['Fantasy', 'Novel', 'Chivalry']
#         # for genre in range(genres):
#         #      Genre.objects.create(
#         #          name=f'{genre}'
#         #     )
        
#         genre_objects_for_book = Genre.objects.all()





