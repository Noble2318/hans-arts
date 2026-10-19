from django import forms
from django.core.exceptions import ValidationError

from .models import ContactMessage, Painting


class GalleryFilterForm(forms.Form):
    q = forms.CharField(required=False, max_length=200)
    category = forms.ChoiceField(required=False)
    availability = forms.ChoiceField(required=False)
    currency = forms.ChoiceField(required=False)
    min_price = forms.DecimalField(required=False, min_value=0, decimal_places=2)
    max_price = forms.DecimalField(required=False, min_value=0, decimal_places=2)

    def __init__(self, *args, labels, **kwargs):
        super().__init__(*args, **kwargs)
        self.labels = labels
        self.fields['q'].label = labels['search_placeholder']
        self.fields['q'].widget.attrs.update({
            'class': 'search-box',
            'placeholder': 'Search paintings...',
            'autocomplete': 'off',
        })
        self.fields['category'].label = labels['filter_category']
        self.fields['category'].choices = [
            ('all', labels['all']),
            *[
                (value, labels[f'category_{value}'])
                for value, _ in Painting.CATEGORY_CHOICES
            ],
        ]
        self.fields['category'].widget.attrs['class'] = 'filter-select'
        self.fields['availability'].label = labels['filter_availability']
        self.fields['availability'].choices = [
            ('all', labels['all']),
            ('available', labels['available']),
            ('sold', labels['sold']),
        ]
        self.fields['availability'].widget.attrs['class'] = 'filter-select'
        self.fields['currency'].label = labels['filter_currency']
        self.fields['currency'].choices = [
            ('all', labels['all']),
            *Painting.CURRENCY_CHOICES,
        ]
        self.fields['currency'].widget.attrs['class'] = 'filter-select'
        self.fields['min_price'].label = labels['filter_min_price']
        self.fields['max_price'].label = labels['filter_max_price']
        for field_name in ('min_price', 'max_price'):
            self.fields[field_name].widget.attrs.update({
                'class': 'filter-input',
                'min': '0',
                'step': '0.01',
                'inputmode': 'decimal',
            })
        self.fields['min_price'].error_messages['invalid'] = labels['invalid_price']
        self.fields['min_price'].error_messages['min_value'] = labels['invalid_price']
        self.fields['max_price'].error_messages['invalid'] = labels['invalid_price']
        self.fields['max_price'].error_messages['min_value'] = labels['invalid_price']

    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')
        currency = cleaned_data.get('currency')

        if min_price is not None and max_price is not None and min_price > max_price:
            raise ValidationError(self.labels['price_range_error'])
        if (min_price is not None or max_price is not None) and currency == 'all':
            raise ValidationError(self.labels['price_currency_required'])

        return cleaned_data

class ContactForm(forms.ModelForm):
    def __init__(self, *args, labels, **kwargs):
        super().__init__(*args, **kwargs)
        self.labels = labels
        placeholders = {
            'name': 'Your name',
            'email': 'Email (optional)',
            'phone': 'Phone number',
            'message': 'Your message',
        }
        for field_name, placeholder in placeholders.items():
            self.fields[field_name].widget.attrs['placeholder'] = placeholder

        self.fields['name'].label = labels['name']
        self.fields['email'].label = f"{labels['email']} ({labels['optional']})"
        self.fields['phone'].label = labels['phone']
        self.fields['message'].label = labels['message']
        self.fields['inquiry_type'].label = labels['inquiry_type']
        self.fields['inquiry_type'].choices = [
            ('general', labels['general_inquiry']),
            ('order', labels['painting_order']),
        ]
        self.fields['inquiry_type'].widget.attrs['class'] = 'form-select'
        self.fields['order_details'].label = labels['order_details']
        self.fields['order_details'].widget.attrs.update({
            'placeholder': labels['order_details_help'],
            'rows': 3,
        })

    class Meta:
        model = ContactMessage
        fields = [
            'name',
            'email',
            'phone',
            'inquiry_type',
            'order_details',
            'message',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'autocomplete': 'name'}),
            'email': forms.EmailInput(attrs={'autocomplete': 'email'}),
            'phone': forms.TextInput(attrs={'autocomplete': 'tel', 'inputmode': 'tel'}),
            'message': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if (
            cleaned_data.get('inquiry_type') == 'order'
            and not cleaned_data.get('order_details', '').strip()
        ):
            raise ValidationError({
                'order_details': self.labels['order_details_required'],
            })
        return cleaned_data