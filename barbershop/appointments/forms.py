from django import forms
from django.contrib.auth.models import User
from .models import Barberos
from django.core.exceptions import ValidationError

class UserBarberoForm(forms.ModelForm):
    # Campos del modelo User
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput, required=False)  # password no es obligatorio al editar

    class Meta:
        model = Barberos
        fields = ['nombre', 'apellido_paterno', 'apellido_materno', 'telefono']

    def __init__(self, *args, **kwargs):
        super(UserBarberoForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Prellenar los campos de usuario relacionados si el barbero ya existe
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email

    def clean_username(self):
        """Validar que el username sea único"""
        username = self.cleaned_data['username']
        # Comprobar si el username ya está en uso
        user_qs = User.objects.filter(username=username)

        if self.instance.pk:  # Solo verifica si la instancia existe
            if self.instance.user:  # Asegúrate de que el barbero ya tiene un usuario
                user_qs = user_qs.exclude(pk=self.instance.user.pk)


        if user_qs.exists():
            raise ValidationError("El nombre de usuario ya está en uso. Por favor, elige otro.")

        return username

    def save(self, commit=True):
        # Si no hay un usuario asignado al barbero, creamos uno nuevo
        user = getattr(self.instance, 'user', None)
        if not user:
            user = User()  # Crear un nuevo usuario si no existe

        # Actualizar los campos del usuario
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']

        # Si el administrador quiere cambiar la contraseña
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)

        # Guardar el usuario antes de asignarlo al barbero
        user.save()

        # Asignar el usuario al barbero y guardar el barbero
        barbero = super().save(commit=False)
        barbero.user = user

        if commit:
            barbero.save()  # Guardar el barbero

        return self.instance
