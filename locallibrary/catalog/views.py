from django.shortcuts import render, get_object_or_404
from .models import Book, Author, BookInstance, Genre
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect # Http404
from django.urls import reverse, reverse_lazy
from catalog.forms import RenewBookForm
from django.contrib.auth.decorators import login_required, permission_required
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
    paginate_by = 3

class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book

class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book 
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.add_book'

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book 
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.change_book'


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

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
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
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()
            return HttpResponseRedirect(reverse('all_borrowed'))
    # if this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'due_back': proposed_renewal_date})
    
    context = {
        'form': form, 
        'book_instance': book_instance
    }
    
    return render(request, 'catalog/book_renew_librarian.html', context)

class AuthorListView(ListView):
    model = Author 
    context_object_name = 'author_list'
    paginate_by = 5

class AuthorDetailView(DetailView):
    model = Author

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_birth': datetime.date.today()}
    permission_required = 'catalog.add_author'

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.change_author'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author 
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.delete_author'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            reverse('author_delete', kwargs={'pk':self.object.pk})

class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book 
    success_url = reverse_lazy('books')
    permission_required = 'catalog.delete_book'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            reverse('book_delete', kwargs={'pk':self.object.pk})

