from django import forms

class SSHCommandForm(forms.Form):
    command = forms.CharField(
        label='',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': True,
            'placeholder': 'Enter your command here...',
            'autocomplete': 'off',
            'spellcheck': 'false'
        })
    ) 