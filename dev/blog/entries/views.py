from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import Http404
from django.views import View
from django.views.generic import UpdateView
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from .models import Entry, Wishlist, WishlistItem
from django.views.decorators.http import require_POST
from django.contrib.messages import get_messages

class HomeView(LoginRequiredMixin, ListView):
    model = Entry
    template_name = "entries/index.html"
    context_object_name = "blog_entries"
    ordering = ['-entry_date']
    paginate_by = 3

    def dispatch(self, request, *args, **kwargs):
        # Vide les anciens messages
        list(messages.get_messages(request))
        return super().dispatch(request, *args, **kwargs)
    
class EntryView(DetailView):
    model = Entry
    template_name = "entries/entry_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Vérifie si la variable de session existe
        context['from_user_entries'] = self.request.session.get('from_user_entries', False)
        return context

class CreateEntryView(LoginRequiredMixin, CreateView):
    model = Entry
    template_name = "entries/create_entry.html"
    fields = ['entry_title', 'entry_text']

    def form_valid(self, form):
        form.instance.entry_author = self.request.user
        return super().form_valid(form)

class UserEntriesView(LoginRequiredMixin, ListView):
    model = Entry
    template_name = 'entries/user_entries.html'
    context_object_name = 'blog_entries'
    ordering = ['-entry_date']
    paginate_by = 3

    def dispatch(self, request, *args, **kwargs):
        # Vide les anciens messages
        list(messages.get_messages(request))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        self.request.session['from_user_entries'] = True
        return Entry.objects.filter(entry_author=self.request.user)


class EditEntryView(LoginRequiredMixin, UpdateView):
    model = Entry
    fields = ['entry_title', 'entry_text']
    template_name = 'entries/edit_entry.html'

    def get_object(self, queryset=None):
        """
        S'assurer que l'utilisateur ne modifie que ses propres articles.
        """
        obj = super().get_object(queryset)
        if obj.entry_author != self.request.user:
            raise PermissionDenied
        return obj   
    
    def form_valid(self, form):
        """
        Réassocier l'auteur et ajouter un message de succès avant de rediriger.
        """
        form.instance.entry_author = self.request.user
        # Sauvegarder l'article (cela effectue bien la mise à jour)
        response = super().form_valid(form)
        
        # Ajouter un message de succès après la mise à jour
        messages.success(self.request, f'L\'article "{form.instance.entry_title}" a bien été modifié.')
        
        # Rediriger vers la liste des articles de l'utilisateur
        return redirect('user-entries')

    def get_success_url(self):
        """
        Retourner l'URL de redirection après la mise à jour. 
        On ne l'utilise pas dans ce cas car on redirige manuellement dans form_valid().
        """
        return reverse_lazy('user-entries')
    
class DeleteEntryView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            entry = Entry.objects.get(pk=pk)
            if entry.entry_author != request.user:
                raise PermissionDenied
            entry_title = entry.entry_title  # On garde le titre pour l'affichage dans le message
            entry.delete()
            messages.success(request, f'L\'article "{entry_title}" a bien été supprimé.')
            return redirect('user-entries')  # Redirige vers la liste des articles de l'utilisateur
        except Entry.DoesNotExist:
            raise Http404("Discussion non trouvée")

class ToggleWishlistView(View):
    def get(self, request, pk):
        try:
            entry = Entry.objects.get(pk=pk)
            wishlists = Wishlist.objects.filter(user=request.user)
            creating_new = not wishlists.exists()

            return render(request, 'entries/create_wishlist.html', {
                'entry': entry,
                'user_wishlists': wishlists,
                'creating_new': creating_new
            })

        except Entry.DoesNotExist:
            messages.error(request, "L'article n'existe pas.")
            return redirect('blog-home')  # Redirection vers l'accueil si l'article n'est pas trouvé

    def post(self, request, pk):
        try:
            entry = Entry.objects.get(pk=pk)
            wishlists = Wishlist.objects.filter(user=request.user)
            creating_new = not wishlists.exists()

            # Si la wishlist est nouvelle, on la crée
            if creating_new:
                wishlist_name = request.POST.get("wishlist_name")
                if wishlist_name:
                    # Création de la nouvelle wishlist
                    wishlist = Wishlist.objects.create(name=wishlist_name, user=request.user)
                    WishlistItem.objects.create(wishlist=wishlist, entry=entry)
                    messages.success(request, f'La wishlist "{wishlist.name}" a été créée et l\'article y a été ajouté.')
                else:
                    messages.error(request, "Veuillez entrer un nom pour la wishlist.")
                    return redirect('toggle-wishlist', pk=pk)  # Si nom vide, on reste sur la page actuelle

            else:
                wishlist_id = request.POST.get("wishlist")
                try:
                    # Ajout de l'article à une wishlist existante
                    wishlist = Wishlist.objects.get(id=wishlist_id, user=request.user)
                    WishlistItem.objects.create(wishlist=wishlist, entry=entry)
                    messages.success(request, f'L\'article a été ajouté à la wishlist "{wishlist.name}".')
                except Wishlist.DoesNotExist:
                    messages.error(request, "La wishlist sélectionnée n'existe pas.")
                    return redirect('toggle-wishlist', pk=pk)  # Si wishlist inexistante, on reste sur la page actuelle

            # **Redirection vers la page d'accueil** après le traitement
            return redirect('blog-home')  # Redirige vers la page d'accueil après ajout à wishlist

        except Entry.DoesNotExist:
            messages.error(request, "L'article n'existe pas.")
            return redirect('blog-home')  # Si l'article n'existe pas, redirection vers la page d'accueil


class CreateWishlistView(LoginRequiredMixin, CreateView):
    model = Wishlist
    template_name = 'entries/create_wishlist.html'
    fields = ['name']

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Votre nouvelle liste d'envies a été créée avec succès.")
        return super().form_valid(form)

    def get_success_url(self):
        # Redirige l'utilisateur vers la page des listes de souhaits après la création
        return reverse_lazy('wishlist-list')  

class WishlistListView(ListView):
    model = Wishlist
    template_name = 'entries/wishlist_list.html'
    context_object_name = 'wishlists'

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).prefetch_related('items__entry')
    
class DeleteItemView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            item = WishlistItem.objects.get(pk=pk)
            # Vérifie que l'utilisateur a le droit de supprimer cet item (l'élément doit être dans sa wishlist)
            if item.wishlist.user != request.user:
                raise PermissionDenied
            
            entry_title = item.entry.entry_title  # On garde le titre de l'article pour l'affichage
            item.delete()
            
            # Message de succès
            messages.success(request, f'L\'article "{entry_title}" a bien été supprimé de la wishlist.')
            
            # Redirection après la suppression
            return redirect('wishlist-list')  # Redirige vers la liste des wishlists de l'utilisateur
            
        except WishlistItem.DoesNotExist:
            raise Http404("Article dans la wishlist non trouvé")