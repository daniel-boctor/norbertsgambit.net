from django.shortcuts import render
from .models import Trade
from .forms import MyUserCreationForm, UserUpdateForm, NGForm
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import requests
from .NBlib import *

# Create your views here.

def norberts_gambit(request, crudop=None, name=None):
    if request.method == "GET":
        if not crudop or not request.user.is_authenticated:
            return render(request, "NG/norberts_gambit.html", {"form": NGForm})

        instance = Trade.objects.filter(user=request.user, name=name)
        if crudop == "trade":
            if instance.exists():
                return render(request, "NG/norberts_gambit.html", {"form": NGForm(instance=instance[0])})
            return HttpResponseRedirect(reverse("index")) 
        if crudop == "delete":
            if instance.exists():
                instance[0].delete()
                return JsonResponse({"MESSAGE": ['secondary', 'Alert', f'{name} has been deleted!']})
            return JsonResponse({"MESSAGE": ['danger', 'Alert', f'{name} was not found!']})

    if request.method == "POST":
        if crudop == "update" and Trade.objects.filter(user=request.user, name=name).exists():
            form = NGForm(request.POST, instance=Trade.objects.filter(user=request.user, name=name)[0])
        else:
            form = NGForm(request.POST, user=request.user)

        if form.is_valid():
            message = None
            if crudop:
                if request.user.is_authenticated:
                    instance = form.save(commit=False)
                    instance.user = request.user
                    if Trade.objects.filter(user=request.user, name=instance.name).exists() and Trade.objects.get(user=request.user, name=instance.name).id != instance.id:
                        message = ['danger', 'Alert', f'Trade named {instance.name} already exists.']
                    else:
                        instance.save()
                        message = ['success', 'Alert', f'{instance.name} has been {crudop}d!']
                else:
                    message = ['warning', 'Alert', 'You must be logged in to save instances to your account.']

            params = {k: float(form.cleaned_data[k]) for k in list(form.cleaned_data)[8:-3] if form.cleaned_data[k] != None}
            output_transactions, output_total, output_explicit_costs, output_ECN, output_commissions, output_tax  = \
            norbits_gambit_cost_calc(params, float(form.cleaned_data["DLR_TO"]), float(form.cleaned_data["DLR_U_TO"]), form.cleaned_data["buy_FX"], form.cleaned_data["sell_FX"], float(form.cleaned_data["initial"]), form.cleaned_data["initial_fx"], form.cleaned_data["incur_buy_side_ecn"], form.cleaned_data["incur_sell_side_ecn"])

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
            return JsonResponse({
                "ERROR": form.errors
            })

def scrape_spreads(request, ticker):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    r = requests.get(f"https://finance.yahoo.com/quote/{ticker}", headers=headers)
    if r.text.find("BID-value") == -1: return JsonResponse({'status': 'false','message': f'{ticker} not found'}, status=400)
    return JsonResponse({
        "BID": r.text[r.text.find("BID-value")+11:].split()[0],
        "ASK": r.text[r.text.find("ASK-value")+11:].split()[0]
    })

def norberts_gambit_api(request):
    year = request.GET.get("year", None)
    if year: queryset = Trade.objects.filter(user=request.user, date__year=year)
    else: queryset = Trade.objects.filter(user=request.user)
    return JsonResponse({trade[0]: [trade[1], trade[2], trade[3] if trade[3] in ["CAD", "USD"] else trade[5] if trade[3] == "TO" else trade[6], 'closed' if trade[4] else 'open'] for trade in queryset.order_by('-date').values_list('name', 'date', 'initial', 'initial_fx', 'closed', 'cad_ticker', 'usd_ticker')})

def norberts_gambit_tax(request):
    name = request.GET.get("name", None)
    year = request.GET.get("year", None)
    if name:
        queryset = Trade.objects.filter(user=request.user, name=name).order_by('-date').values()
    elif year:
        queryset = Trade.objects.filter(user=request.user, date__year=year).order_by('-date').values()
    else:
        queryset = Trade.objects.filter(user=request.user).order_by('-date').values()
    output = pd.DataFrame()
    for data in queryset:
        params = {k: float(data[k]) for k in list(data)[10:-3] if data[k] != None}
        _, _, _, _, _, output_tax  = norbits_gambit_cost_calc(params, float(data["DLR_TO"]), float(data["DLR_U_TO"]), data["buy_FX"], data["sell_FX"], float(data["initial"]), data["initial_fx"], data["incur_buy_side_ecn"], data["incur_sell_side_ecn"])
        output_tax.index = [data["name"]]
        output_tax.insert(0, "Ticker", data["cad_ticker"])
        output = pd.concat([output, output_tax])
    
    return JsonResponse({"output_tax": output.to_html(classes=["table table-hover table-fit-center"], border=0,  justify="unset")})

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
def user(request, username):
    if request.user.username == username:
        if request.method == "POST":
            form = UserUpdateForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, f"Info saved.", extra_tags="Success!")
                return HttpResponseRedirect(reverse("user", args=[request.user.username]))
        else:
            form = UserUpdateForm(instance=request.user)
        return render(request, "NG/user/user.html", {"form": form})