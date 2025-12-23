from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
def index(request):
    """View function for home page of site"""
    num_books = Book.objects.all().count()
    num_instaces = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instaces_available = BookInstance.objects.filter(status__exact='a').count()

    # genre count
    num_genres = Genre.objects.all().count()

    # Filtering books by a specific genre
    fantasy_books = Book.objects.filter(genre__name__icontains='fantasy')
    fantasy_books_count = fantasy_books.count()

    # The 'all()' is implied by default
    num_authors = Author.objects.count()

    num_visits = request.session.get('num_visits', 0)
    num_visits += 1
    request.session['num_visits'] = num_visits

    context = {
        'num_books': num_books,
        'fantasy_books_count': fantasy_books_count,
        'num_instances': num_instaces, 
        'num_instances_available': num_instaces_available, 
        'num_authors': num_authors,
        'fantasy_books': fantasy_books, 
        'num_genres': num_genres, 
        'num_visits': num_visits,
    }

    print(type(fantasy_books))
    return render(request, 'index.html', context=context)   

class BookListView(ListView):
    model = Book
    context_object_name = 'book_list'
    paginate_by = 2

class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book

class AuthorListView(ListView):
    model = Author 
    context_object_name = 'author_list'
    # paginate_by = 2

class AuthorDetailView(DetailView):
    model = Author