from django.shortcuts import render
from .models import Trade, Portfolio
from .forms import MyUserCreationForm, UserUpdateForm, NGForm, PortfolioForm
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
import requests
from .NBlib import *

# Create your views here.

def norberts_gambit(request, crudop=None, name=None):
    if request.method == "GET":
        if not crudop or not request.user.is_authenticated:
            return render(request, "NG/norberts_gambit.html", {"form": NGForm(user=request.user)})

        instance = Trade.objects.filter(user=request.user, name=name)
        if crudop == "trade":
            if instance.exists():
                return render(request, "NG/norberts_gambit.html", {"form": NGForm(instance=instance[0], user=request.user)})
            return HttpResponseRedirect(reverse("index")) 
        if crudop == "delete":
            if instance.exists():
                instance[0].delete()
                return JsonResponse({"MESSAGE": ['info', 'Alert', f'{name} has been deleted!']})
            return JsonResponse({"MESSAGE": ['danger', 'Alert', f'{name} was not found!']})

    if request.method == "POST":
        if crudop == "update" and Trade.objects.filter(user=request.user, name=name).exists():
            form = NGForm(request.POST, instance=Trade.objects.filter(user=request.user, name=name)[0], user=request.user)
        else:
            form = NGForm(request.POST, user=request.user)

        if form.is_valid():
            message = None
            if crudop:
                if request.user.is_authenticated:
                    instance = form.save(commit=False)
                    #Duplicate name detection
                    queryset = Trade.objects.filter(user=request.user, name=instance.name)
                    if instance.pk:
                        queryset = queryset.exclude(pk=instance.pk)
                    if queryset.exists():
                        message = ['danger', 'Alert', f'Trade named {instance.name} already exists.']
                    else:
                        instance.save()
                        message = ['success', 'Alert', f'{instance.name} has been {crudop}d!']
                else:
                    message = ['warning', 'Alert', 'You must be logged in to save instances to your account.']

            params = {k: form.cleaned_data[k] for k in list(form.cleaned_data)[11:-3] if form.cleaned_data[k] != None}
            output_transactions, output_total, output_explicit_costs, output_ECN, output_commissions, output_tax  = \
            norbits_gambit_cost_calc(params, form.cleaned_data["DLR_TO"], form.cleaned_data["DLR_U_TO"], form.cleaned_data["buy_FX"], form.cleaned_data["sell_FX"], form.cleaned_data["initial"], form.cleaned_data["initial_fx"], form.cleaned_data["incur_buy_side_ecn"], form.cleaned_data["incur_sell_side_ecn"])

            return JsonResponse({
                "MESSAGE": message,
                "output_transactions": output_transactions.to_html(classes=["table table-hover table-fit-center"], border=0,  justify="unset"),
                "output_total": output_total.to_html(classes=["table table-hover table-fit-center"], border=0,  justify="unset"),
                "output_costs": output_explicit_costs.to_html(classes=["table table-hover table-fit-center"], border=0,  justify="unset"),
                "output_ECN": output_ECN.to_html(classes=["table table-hover table-fit-center"], border=0,  justify="unset"),
                "output_commissions": output_commissions.to_html(classes=["table table-hover table-fit-center"], border=0,  justify="unset"),
                "output_tax": output_tax.to_html(classes=["table table-hover table-fit-center"], border=0,  justify="unset"),
            })
        else:
            errors = {}
            for error in form.non_field_errors():
                errors["Error"] = error
            for field in form:
                for error in field.errors:
                    errors[field.label] = error
            return JsonResponse({
                "ERROR": errors
            })

def scrape_spreads(request, ticker):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    r = requests.get(f"https://finance.yahoo.com/quote/{ticker}", headers=headers)
    if r.text.find("BID-value") == -1: return JsonResponse({'status': 'false','message': f'{ticker} not found'}, status=400)
    return JsonResponse({
        "BID": r.text[r.text.find("BID-value")+11:].split()[0],
        "ASK": r.text[r.text.find("ASK-value")+11:].split()[0]
    })

def filter(querydict, user, allowed_filters):
    params = {k: v for k, v in querydict if v and k in allowed_filters}
    map = {"year": "date__year", "portfolio": "portfolio__name"}
    params = {map.get(k, k): v for k, v in params.items()}
    queryset = Trade.objects.filter(user=user, **params).order_by('-date')
    return queryset

@login_required
def norberts_gambit_api(request):
    queryset = filter(request.GET.items(), request.user, ['year', 'portfolio'])
    return JsonResponse({trade.name: [trade.date, trade.initial, trade.initial_fx if trade.initial_fx in ["CAD", "USD"] else trade.cad_ticker if trade.initial_fx == "TO" else trade.usd_ticker, 'closed' if trade.closed else 'open', trade.portfolio.name if trade.portfolio else ''] for trade in queryset})

@login_required
def norberts_gambit_tax(request):
    queryset = filter(request.GET.items(), request.user, ['name', 'year', 'portfolio'])
    output = pd.DataFrame()
    for data in queryset.values():
        params = {k: data[k] for k in list(data)[13:-3] if data[k] != None}
        _, _, _, _, _, output_tax  = norbits_gambit_cost_calc(params, data["DLR_TO"], data["DLR_U_TO"], data["buy_FX"], data["sell_FX"], data["initial"], data["initial_fx"], data["incur_buy_side_ecn"], data["incur_sell_side_ecn"])
        output_tax.index = [data["name"]]
        output_tax.insert(0, "Ticker", data["cad_ticker"])
        output = pd.concat([output, output_tax])
    
    return JsonResponse({"output_tax": output.to_html(classes=["table table-hover table-fit-center"], table_id="tax_df", border=0,  justify="unset")})

def register(request):
    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Account created for {username}", extra_tags="Success!")
            return HttpResponseRedirect(reverse("index"))
    else:
        form = MyUserCreationForm()
    return render(request, "NG/user/register.html", {"form": form})

@login_required
def user(request, username, portfolio=False):
    if request.user.username == username:
        #User
        if request.method == "POST" and not portfolio:
            form = UserUpdateForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, f"Info saved.", extra_tags="Success!")
                return HttpResponseRedirect(reverse("user", args=[request.user.username]))
        else:
            form = UserUpdateForm(instance=request.user)

        #Portfolio
        PortfolioFormSet = modelformset_factory(Portfolio, form=PortfolioForm, extra=1, max_num=20, absolute_max=20, can_delete=True)
        if request.method == "POST" and portfolio:
            portfolioformset = PortfolioFormSet(request.POST, queryset=Portfolio.objects.filter(user=request.user), form_kwargs={'user': request.user})
            if portfolioformset.is_valid():
                instances = portfolioformset.save(commit=False)
                for obj in portfolioformset.deleted_objects:
                    obj.delete()
                    messages.success(request, f"{obj.name} was successfully deleted.", extra_tags="Success!")
                for instance in instances:
                    instance.save()
                    messages.success(request, f"{instance.name} was successfully saved.", extra_tags="Success!")
                return HttpResponseRedirect(reverse("portfolio", args=[request.user.username]))
        else:
            portfolioformset = PortfolioFormSet(queryset=Portfolio.objects.filter(user=request.user), form_kwargs={'user': request.user})
            
        return render(request, "NG/user/user.html", {"form": form, "portfolioformset": portfolioformset})