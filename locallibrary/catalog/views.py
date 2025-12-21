from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views.generic import ListView, DetailView

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

    context = {
        'num_books': num_books,
        'fantasy_books_count': fantasy_books_count,
        'num_instances': num_instaces, 
        'num_instances_available': num_instaces_available, 
        'num_authors': num_authors,
        'fantasy_books': fantasy_books, 
        'num_genres': num_genres
    }

    print(type(fantasy_books))
    return render(request, 'index.html', context=context)   

class BookListView(ListView):
    model = Book
    context_object_name = 'book_list'

class BookDetailView(DetailView):
    model = Book