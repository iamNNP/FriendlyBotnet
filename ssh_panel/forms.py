from django import forms

class SSHCommandForm(forms.Form):
    command = forms.CharField(
        label='',
        max_length=200,
        required=False,  # Allow empty command for upload
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your command here...',
            'autocomplete': 'off',
            'spellcheck': 'false'
        })
    )
    ssh_file = forms.FileField(
        label='',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.txt'})
    )