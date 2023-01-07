from django import forms
from .models import User, Trade
from django.contrib.auth.forms import UserCreationForm

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(MyUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs = {'class': 'form-control', 'placeholder':'Username'}
        self.fields['email'] = forms.EmailField(max_length=64, required=True, help_text='Required. Enter a valid email address.', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Email'}))
        self.fields['password1'].widget.attrs = {'class': 'form-control', 'placeholder':'Password'}
        self.fields['password2'].widget.attrs = {'class': 'form-control', 'placeholder':'Password Confirmation'}

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email')
    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs = {'class': 'form-control', 'placeholder':'Username'}
        self.fields['email'].widget.attrs = {'class': 'form-control', 'placeholder':'Email'}

class NGForm(forms.ModelForm):
    class Meta:
        model = Trade
        exclude = ('user',)
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Name'}),
            'date': forms.DateInput(attrs={'class':'form-control', 'type':'date'}),
            'DLR_TO': forms.TextInput(attrs={'class':'form-control'}),
            'DLR_U_TO': forms.TextInput(attrs={'class':'form-control'}),
            'buy_FX': forms.TextInput(attrs={'class':'form-control', 'placeholder':'1 USD = '}),
            'sell_FX': forms.TextInput(attrs={'class':'form-control', 'placeholder':'1 USD = '}),
            'initial': forms.TextInput(attrs={'class':'form-control', 'placeholder':'10,000'}),
            'initial_fx': forms.Select(attrs={'class':'form-select'}),
            'incur_buy_side_ecn': forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'incur_sell_side_ecn': forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'buy_side_ecn': forms.TextInput(attrs={'class':'form-control'}),
            'sell_side_ecn': forms.TextInput(attrs={'class':'form-control'}),
            'buy_side_comm': forms.TextInput(attrs={'class':'form-control'}),
            'sell_side_comm': forms.TextInput(attrs={'class':'form-control'}),
            'lower_bound': forms.TextInput(attrs={'class':'form-control'}),
            'upper_bound': forms.TextInput(attrs={'class':'form-control'}),
            'brokers_spread': forms.TextInput(attrs={'class':'form-control', 'placeholder':'%'}),
            'dealers_rate': forms.TextInput(attrs={'class':'form-control', 'placeholder':'1 USD = '}),
            'cad_ticker': forms.TextInput(attrs={'class':'form-control'}),
            'usd_ticker': forms.TextInput(attrs={'class':'form-control'}),
            'closed': forms.CheckboxInput(attrs={'class':'form-check-input'})
        }

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data["name"] and self.user.is_authenticated:
            cleaned_data["name"] = f"Trade {Trade.objects.filter(user=self.user).count() + 1}"
        if cleaned_data.get("initial") and cleaned_data["initial_fx"] in ["TO", "U"] and int(cleaned_data["initial"]) != cleaned_data["initial"]:
            self.add_error('initial', "Quantity of shares must be a whole number.")
        return cleaned_data

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(NGForm, self).__init__(*args, **kwargs)
        self.user = user