from django import forms
from .models import User, Trade, Portfolio
from django.contrib.auth.forms import UserCreationForm
from .widgets import DollarDisplayTextInput

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
        self.fields['username'].help_text = None

class NGForm(forms.ModelForm):
    class Meta:
        model = Trade
        exclude = ('user',)
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Name'}),
            'portfolio': forms.Select(attrs={'class':'form-select'}),
            'date': forms.DateInput(attrs={'class':'form-control', 'type':'date'}),
            'DLR_TO': DollarDisplayTextInput(attrs={'class':'form-control'}),
            'DLR_U_TO': DollarDisplayTextInput(attrs={'class':'form-control'}),
            'buy_FX': DollarDisplayTextInput(attrs={'class':'form-control', 'placeholder':'1 USD = '}),
            'sell_FX': DollarDisplayTextInput(attrs={'class':'form-control', 'placeholder':'1 USD = '}),
            'initial': forms.TextInput(attrs={'class':'form-control', 'placeholder':'10,000'}),
            'initial_fx': forms.Select(attrs={'class':'form-select'}),
            'incur_buy_side_ecn': forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'incur_sell_side_ecn': forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'buy_side_ecn': DollarDisplayTextInput(attrs={'class':'form-control'}),
            'sell_side_ecn': DollarDisplayTextInput(attrs={'class':'form-control'}),
            'buy_side_comm': DollarDisplayTextInput(attrs={'class':'form-control'}),
            'sell_side_comm': DollarDisplayTextInput(attrs={'class':'form-control'}),
            'lower_bound': DollarDisplayTextInput(attrs={'class':'form-control'}),
            'upper_bound': DollarDisplayTextInput(attrs={'class':'form-control'}),
            'brokers_spread': DollarDisplayTextInput(attrs={'class':'form-control', 'placeholder':'%'}),
            'dealers_rate': DollarDisplayTextInput(attrs={'class':'form-control', 'placeholder':'1 USD = '}),
            'cad_ticker': forms.TextInput(attrs={'class':'form-control'}),
            'usd_ticker': forms.TextInput(attrs={'class':'form-control'}),
            'closed': forms.CheckboxInput(attrs={'class':'form-check-input mt-0'})
        }

    def clean(self):
        cleaned_data = super().clean()

        #Quantity of shares must be a whole number
        if cleaned_data.get("initial") and cleaned_data.get("initial_fx") in ["TO", "U"] and int(cleaned_data.get("initial")) != cleaned_data.get("initial"):
            self.add_error('initial', "Quantity of shares must be a whole number.")

        if self.user.is_authenticated:
            self.instance.user = self.user
            #Setting default name
            if not cleaned_data.get("name"):
                cleaned_data["name"] = f"Trade {Trade.objects.filter(user=self.user).count() + 1}"

        #Tickers must be uppercase
        for field in ['cad_ticker', 'usd_ticker']:
            if field in cleaned_data:
                cleaned_data[field] = cleaned_data[field].upper()
                
        return cleaned_data

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(NGForm, self).__init__(*args, **kwargs)
        self.user = user
        self.fields["portfolio"].queryset = Portfolio.objects.filter(user=self.user) if self.user.is_authenticated else Portfolio.objects.none()
        if len(self.fields["portfolio"].choices) == 1:
            self.fields["portfolio"].widget.attrs.update({"disabled": True})
            #self.fields["portfolio"].empty_label = "No Portfolio"

        #Initialize labels
        self.fields["DLR_TO"].label = self["cad_ticker"].value()
        self.fields["DLR_U_TO"].label = self["usd_ticker"].value()
        self.fields["initial"].label = 'Cash' if self["initial_fx"].value() in ["CAD", "USD"] else 'Shares'

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        exclude = ('user',)
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Portfolio Name'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        self.instance.user = self.user

        #Duplicate name detection
        queryset = Portfolio.objects.filter(user=self.user, name=cleaned_data.get("name"))
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            self.add_error('name', f'Portfolio named {cleaned_data.get("name")} already exists.')   

        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PortfolioForm, self).__init__(*args, **kwargs)
        self.user = user