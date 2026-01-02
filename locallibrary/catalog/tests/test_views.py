from django.test import TestCase
from django.urls import reverse 
from catalog.models import Author, BookInstance, Book, Genre, Language
from django.utils import timezone
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect

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

import datetime 
from django.contrib.auth import get_user_model

User = get_user_model()

class LoanedBookInstancesByUserListViewTest(TestCase):
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        test_author = Author.objects.create(first_name='Dominique', last_name='Rousseau')   
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='My Book', 
            summary= 'My summary',
            isbn= 'ABCDEFG',
            author=test_author, 
            language=test_language
        )

        # test_genres = ['Fantasy', 'Novel', 'Chivalry']
        # for genre in range(genres):
        #      Genre.objects.create(
        #          name=f'{genre}'
        #     )
        
        genre_objects_for_book = Genre.objects.all()
        # Direct assignment of many-to-many is not allowed
        test_book.genre.set(genre_objects_for_book)
        
        test_book.save()

        # Create 30 BookInstance objects
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.localtime() + datetime.timedelta(days=book_copy%5)
            the_borrower = test_user1 if book_copy % 2 else test_user2
            status = 'm'
            BookInstance.objects.create(
                book=test_book, 
                imprint='Unlikely imprint 2016',
                due_back=return_date, 
                borrower=the_borrower, 
                status=status
            )
        
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('my_borrowed'))
        self.assertRedirects(response, f'/accounts/login/?next={reverse("my_borrowed")}')
    
    def test_logged_in_uses_correct_templete(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my_borrowed'))
        # check the user is logged in 
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/bookinstance_list_borrowed_user.html')

    def test_only_borrowed_books_in_list(self):
        # log in the user   
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        # get borrowed path
        response = self.client.get(reverse('my_borrowed'))
        # check the user is logged in   
        self.assertEqual(str(response.context['user']), 'testuser1')
        # check response success
        self.assertEqual(response.status_code, 200)
        # Check that initially we don't have any books in list (none on loan)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']), 0)

        books = BookInstance.objects.all()[:10]

        for book in books:
            book.status = 'o'
            book.save()

        response = self.client.get(reverse('my_borrowed'))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('bookinstance_list' in response.context)

        for book_item in response.context['bookinstance_list']:
            self.assertEqual(response.context['user'], book_item.borrower)
            self.assertEqual(book_item.status, 'o')

    def test_pages_ordered_by_due_date(self):
        # Change all books to be on loan
        for book in BookInstance.objects.all():
            book.status='o'
            book.save()

        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my_borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Confirm that of the items, only 10 are displayed due to pagination.
        self.assertEqual(len(response.context['bookinstance_list']), 10)

        last_date = 0

        for book in response.context['bookinstance_list']:
            if last_date == 0:
                last_date = book.due_back
            else:
                self.assertTrue(last_date <= book.due_back)
                last_date = book.due_back        

# REVIEW FROM HERE - VIEW DJANGO TEST TUTORIAL. 
from catalog.forms import RenewBookForm

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        book_renewal_form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if book_renewal_form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = book_renewal_form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all_borrowed'))

    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        book_renewal_form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'book_renewal_form': book_renewal_form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

