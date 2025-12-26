from django.shortcuts import render, get_object_or_404
from .models import Book, Author, BookInstance, Genre
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect # Http404
from django.urls import reverse 
from catalog.forms import RenewBookForm
import datetime

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

class LoanedBooksByUserListView(LoginRequiredMixin, ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
        )
    
class LoanedBooksAllListView(PermissionRequiredMixin, ListView):
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')
    
def renew_book_librarian(request, pk):
    # try:
    #     book_instance = BookInstance.objects.get(pk=pk)
    # except BookInstance.DoesNotExist:
    #     raise Http404("Copy not found")
    # or we can use the get_object_or_404 method for simplicity
    book_instance = get_object_or_404(BookInstance, pk=pk)
    if request.method == 'POST':
        # create form instance and populate it with data from the request (binding)
        form = RenewBookForm(request.POST)
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()
            return HttpResponseRedirect(reverse('all_borrowed'))
    # if this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})
    
    context = {
        'form': form, 
        'book_instance': book_instance
    }
    
    return render(request, 'catalog/book_renew_librarian.html', context)

