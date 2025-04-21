from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Adresse e-mail", required=True)

    # On peut ajouter une traduction pour les messages d'erreur ici si nécessaire
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput,
        help_text="Votre mot de passe doit être composé d'au moins 8 caractères.",
    )
    
    password2 = forms.CharField(
        label="Confirmation du mot de passe",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'last_name', 'first_name', 'password1', 'password2']
        labels = {
            'username': 'Nom d\'utilisateur',
        }

        help_texts = {
            'username': None,  # Ici tu peux aussi enlever certains textes d'aide
            'email': "Entrez une adresse e-mail valide.",
        }

        error_messages = {
            'password1': {
                'required': "Le mot de passe est obligatoire.",
                'min_length': "Le mot de passe doit contenir au moins 8 caractères.",
            },
            'email': {
                'required': "L'email est obligatoire.",
                'invalid': "Entrez une adresse e-mail valide.",
            },
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return password2
