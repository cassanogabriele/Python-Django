from django.shortcuts import redirect
from django.contrib import messages
from django.http import Http404
from django.views import View
from django.views.generic import UpdateView
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from .models import Entry

class HomeView(LoginRequiredMixin, ListView):
    model = Entry
    template_name = "entries/index.html"
    context_object_name = "blog_entries"
    ordering = ['-entry_date']
    paginate_by = 3

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

    def get_queryset(self):
        # Marque dans la session qu'on vient de la vue des discussions de l'utilisateur
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