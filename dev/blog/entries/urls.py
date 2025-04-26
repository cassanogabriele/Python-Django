from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import ToggleWishlistView
from .views import CreateWishlistView
from .views import WishlistListView
from .views import DeleteItemView

from .views import HomeView, EntryView, CreateEntryView, UserEntriesView, EditEntryView, DeleteEntryView, ToggleWishlistView, CreateWishlistView, WishlistListView, DeleteItemView

urlpatterns = [
    path('', HomeView.as_view(), name='blog-home'),
    path('entry/<int:pk>/', EntryView.as_view(), name='entry-detail'),
    path('create_entry/', CreateEntryView.as_view(success_url='/'), name='create_entry'),
    path('my-discussions/', UserEntriesView.as_view(), name='user-entries'),
    path('entry/<int:pk>/edit/', EditEntryView.as_view(), name='edit-entry'),  
    path('entry/<int:pk>/delete/', DeleteEntryView.as_view(), name='delete-entry'),
    path('entry/<int:pk>/wishlist/', ToggleWishlistView.as_view(), name='toggle-wishlist'),
    path('wishlist/create/', CreateWishlistView.as_view(), name='create-wishlist'),
    path('my-wishlists/', WishlistListView.as_view(), name='wishlist-list'),
    path('wishlist-item/delete/<int:pk>/', DeleteItemView.as_view(), name='delete-wishlist-item'),
]

# Servez les fichiers statiques en mode développement
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
