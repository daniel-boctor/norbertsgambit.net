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
    DLR_TO = forms.DecimalField(decimal_places=4, min_value=0.01, max_value=99999.99, widget=forms.TextInput(attrs={'class':'form-control'}))
    DLR_U_TO = forms.DecimalField(decimal_places=4, min_value=0.01, max_value=99999.99, widget=forms.TextInput(attrs={'class':'form-control'}))
    buy_FX = forms.DecimalField(decimal_places=4, min_value=0.01, max_value=999.99, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'1 USD = '}))
    sell_FX = forms.DecimalField(decimal_places=4, min_value=0.01, max_value=999.99, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'1 USD = '}))
    initial = forms.DecimalField(decimal_places=2, min_value=0.01, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'10,000'}))
    #initial_fx = forms.ChoiceField(choices=(("CAD", "CAD"), ("USD", "USD")), initial="CAD", widget=forms.Select(attrs={'class':'form-select'}))
    incur_buy_side_ecn = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class':'form-check-input'}))
    incur_sell_side_ecn = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class':'form-check-input'}))
    buy_side_ecn = forms.DecimalField(decimal_places=4, initial=0.0035, min_value=0.00, max_value=999.99, widget=forms.TextInput(attrs={'class':'form-control'}))
    sell_side_ecn = forms.DecimalField(decimal_places=4, initial=0.0035, min_value=0.00, max_value=999.99, widget=forms.TextInput(attrs={'class':'form-control'}))
    buy_side_comm = forms.DecimalField(decimal_places=4, initial=0.00, min_value=0.00, max_value=999.99, widget=forms.TextInput(attrs={'class':'form-control'}))
    sell_side_comm = forms.DecimalField(decimal_places=4, initial=0.01, min_value=0.00, max_value=999.99, widget=forms.TextInput(attrs={'class':'form-control'}))
    lower_bound = forms.DecimalField(decimal_places=4, initial=4.95, min_value=0.00, max_value=999.99, widget=forms.TextInput(attrs={'class':'form-control'}))
    upper_bound = forms.DecimalField(decimal_places=4, initial=9.95, min_value=0.00, max_value=999.99, widget=forms.TextInput(attrs={'class':'form-control'}))
    brokers_spread = forms.DecimalField(decimal_places=4, required=False, min_value=0.00, max_value=100, widget=forms.TextInput(attrs={'class':'form-control'}))

    class Meta:
        model = Trade
        exclude = ('user',)
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Name'}),
            'date': forms.DateInput(attrs={'class':'form-control', 'type':'date'}),
            'initial_fx': forms.Select(attrs={'class':'form-select'}),
            'closed': forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'cad_ticker': forms.TextInput(attrs={'class':'form-control'}),
            'usd_ticker': forms.TextInput(attrs={'class':'form-control'})
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