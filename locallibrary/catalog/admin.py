from django.contrib import admin
from .models import Author, Genre, Book, BookInstance, Language

# Inline class for BookInstance; to be displayed in Book admin page
class BooksInstanceInline(admin.TabularInline):
    model = BookInstance 
    classes = ('collapse',) # to make it collapsible in the admin interface

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')

    inlines = [BooksInstanceInline]

# Inline class for Book; to be displayed in Author admin page
class BookInline(admin.TabularInline):
    model = Book
    classes = ('collapse',)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death') # display columns in admin list view
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')] # layout of fields in admin detail view

    inlines = [BookInline]

admin.site.register(Genre)

@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_filter = ('status', 'due_back') # filters in the right sidebar
    list_display = ('display_book', 'status', 'due_back', 'id', 'borrower')

    # organize detail view layout
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )

admin.site.register(Language)
