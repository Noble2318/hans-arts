from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Jina lako'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Barua pepe (si lazima)'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Namba ya simu'}),
            'message': forms.Textarea(attrs={'placeholder': 'Ujumbe wako', 'rows': 4}),
        }