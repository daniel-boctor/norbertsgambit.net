function fetch_spreads(suffix="TO", ticker="DLR") {
    fetch(`/scrape_spreads/${ticker}`)
    .then(response => {
        if (response.ok) return response.json()
        document.querySelector('#form-container').insertAdjacentHTML('afterbegin', 
        `<div class="alert alert-danger alert-dismissible sticky-top fade show" role="alert">
            <strong>Error:</strong> ${ticker} could not be found.
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>`);
        throw new Error('Network response was not ok.')
    })
    .then(data => {
        document.querySelector(`#${suffix}-BID`).innerHTML = data["BID"]
        document.querySelector(`#${suffix}-ASK`).innerHTML = data["ASK"]
        document.querySelector(`#td_${suffix}_label`).innerHTML = ticker
        document.querySelector(`#id_initial_fx option[value=${suffix}]`).innerHTML = ticker
    });
}

function refresh() {
    fetch_spreads(suffix="TO", ticker=document.querySelector("#id_cad_ticker").value)
    fetch_spreads(suffix="U", ticker=document.querySelector("#id_usd_ticker").value)
}

function message_system(type, header, body, form_alert="") {
    document.querySelector('#form-container').insertAdjacentHTML('afterbegin', 
    `<div class="alert alert-${type}${form_alert} alert-dismissible sticky-top fade show" role="alert">
        <strong>${header}:</strong> ${body}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>`);
}

function crud_api_call(year="") {
    if (!year) {valid_years.clear()}
    $.get(`/api?${new URLSearchParams({year: year})}`, function(data){
        $("#trades-container").empty();
        $("#trades-container").append('<div id="open"></div>');
        $("#trades-container").append('<br><hr><br>');
        $("#trades-container").append('<div id="closed"></div>');
        if ($.isEmptyObject(data) === true) {
            $("#trades-container").append('You have no trades saved. Select the dropdown menu next to submit to get started!');
        } else {
            for (let [name, info] of Object.entries(data)) {
                if (info[3] === 'closed') {color = 'muted'} else {color = 'primary'}
                $(`#${info[3]}`).append(`
                <table class="table table-hover table-striped">
                <thead><tr><th colspan="2">${name}<small class="text-${color}"> ${info[3]}</small></th></tr></thead>
                <tbody><tr>
                    <td style="width: 50%;">${info[0]}</td>
                    <td style="width: 50%;">${info[1]} ${info[2]}</td></tr>
                    <tr><td><a href="/delete/${name}" class="link-danger delete" data-name="${name}">Delete</a></td>
                    <td><a href="/trade/${name}" class="link-primary">Populate</a></td></tr>
                    <tr><td colspan="2"><a href="/?${new URLSearchParams({name: name, year: '',})}" class="link-success tax_link" data-name="${name}">Generate Tax Information</a></td></tr>
                </tbody></table>`
                );
                if (!year) {
                    valid_years.add(parseInt(info[0]))
                }
            }
        }
        //valid_years.sort()
        $("#filter-dropdown-menu").empty();
        $("#filter-dropdown-menu").append(`<li><button class="dropdown-item" onclick="crud_api_call()">All</button></li>`)
        $("#filter-dropdown-menu").append(`<li><hr class="dropdown-divider"></li>`)
        $("#tax-dropdown-menu").empty();
        valid_years.forEach(year => {
            $("#filter-dropdown-menu").append(`<li><button class="dropdown-item" onclick="crud_api_call(year=${year})">${year}</button></li>`)
            $("#tax-dropdown-menu").append(`<li><button class="dropdown-item" onclick="load_tax(undefined, year=${year})">${year}</button></li>`)
        });
        jQuery(".delete").click(function(event){
            event.preventDefault()
            $.get(event.currentTarget.href, function(response){
                message_system(response["MESSAGE"][0], response["MESSAGE"][1], response["MESSAGE"][2])
                crud_api_call()
            });
        });
        jQuery(".tax_link").click(function(event){
            event.preventDefault()
            load_tax(name=event.currentTarget.dataset.name)
        });
    });
}

function load_tax(name="", year="") {
    if (name) {tax_table_title.innerHTML = `${name}`}
    else if (year) {tax_table_title.innerHTML = `Trades from ${year}`}
    else {tax_table_title.innerHTML = `All Trades`}
    body.style.display = "none";
    info.style.display = "none";
    tax_container.style.display = null;
    cached_url = window.location.pathname
    window.history.replaceState('', '', `/?${new URLSearchParams({name: name, year: year,})}`);
    $.get(`/tax?${new URLSearchParams({name: name, year: year})}`, function(response){
        tax_table_container.innerHTML = response[Object.keys(response)[0]];
        tax_df.childNodes[3].childNodes.forEach(function(elem) {
            if (elem.tagName === "TR") {
                if (elem.childNodes[11].innerHTML.substring(1, 2) === "-") {elem.childNodes[11].style.color = "red"}
                else {elem.childNodes[11].style.color = "green"}
            }
        })
    });
}

function back_to_body(back=false) {
    window.history.replaceState('', '', cached_url);
    body.style.display = null;
    if (id_0.innerHTML) {info.style.display = null}
    tax_container.style.display = 'none';
}

$(document).ready(function() {
    var url = new URL(window.location.href);
    if (url.searchParams.get("name")) {name=url.searchParams.get("name")} else {name=""}
    if (url.searchParams.get("year")) {year=url.searchParams.get("year")} else {year=""}
    if (url.search) {load_tax(name, year)}
    refresh()
    valid_years = new Set()
    fetch(`https://www.bankofcanada.ca/valet/observations/FXUSDCAD?recent=1`)
    .then(response => {
        if (response.ok) return response.json()
        throw new Error('Network response was not ok.')
    })
    .then(data => {
        present_fx_info = [data.observations[0].d, data.observations[0].FXUSDCAD.v]
    });
    document.querySelector("#id_buy_FX").required = false;
    document.querySelector("#id_sell_FX").required = false;
    document.querySelector("#id_initial").required = false;

    //api call to backend
    if (auth === 'True') {
        if ($("#id_name").val()) {
            order_trades()
            var myOffcanvas = document.getElementById('offcanvasScrolling')
            var bsOffcanvas = new bootstrap.Offcanvas(myOffcanvas)
            bsOffcanvas.show()
        }
        var myCollapse = document.getElementById('crud_collapse')
        var bsCollapse = new bootstrap.Collapse(myCollapse)
        bsCollapse.show()
        crud_api_call()
    }
    $('#post-form').submit(function(event) {
        event.preventDefault()
        document.querySelectorAll(".FX_lookup").forEach(function (elem) {
            if (document.querySelector(`#id_${elem.id}`).value === "") {
                document.querySelector(`#id_${elem.id}`).value = present_fx_info[1]
                elem.value = present_fx_info[0]
            }
        })
        if (document.querySelector("#id_initial").value === "") {document.querySelector("#id_initial").value = 10000}
        crudop = event.originalEvent.submitter.dataset.crudop
        $.ajax({
            data: $(this).serialize(),
            type: 'POST',
            url: crudop,
            headers: {
                'X-CSRFToken': getCookie("csrftoken")
            },
            success: function(response) {
                if (auth === 'True' && crudop) {crud_api_call()}
                if (Object.keys(response)[0] === "MESSAGE" && response["MESSAGE"] instanceof Array) {
                    message_system(response["MESSAGE"][0], response["MESSAGE"][1], response["MESSAGE"][2])
                }
                delete response["MESSAGE"];
                if (Object.keys(response)[0] === "ERROR") {
                    response = response["ERROR"];
                    for (i=0; i<Object.keys(response).length; i++) {
                        message_system('danger', Object.keys(response)[i], response[Object.keys(response)[i]], form_alert=" form-alert")
                    }
                } else {
                    document.querySelectorAll(".form-alert").forEach(function (elem) {elem.remove()})
                    document.querySelector("#info").style.display = "block";
                    for (i=0; i<Object.keys(response).length; i++) {
                        document.querySelector(`#id_${i}`).innerHTML = response[Object.keys(response)[i]]
                    }
                    //coloring
                    document.querySelector("#id_1").firstChild.childNodes[3].childNodes.forEach(function(elem) {
                        if (elem.tagName === "TR") {
                            if (elem.childNodes[1].innerHTML != "Explicit Costs Incurred") {
                                if (elem.childNodes[3].innerHTML.substring(0, 1) === "-" || elem.childNodes[3].innerHTML.substring(1, 2) === "-") {
                                    elem.childNodes[3].style.color = "red"
                                } else {
                                    elem.childNodes[3].style.color = "green"
                                }
                                if (elem.childNodes.length > 5) {elem.childNodes[5].style.color = "red"}
                            }
                        }
                    })
                    var cap = document.querySelector("#id_5").firstChild.childNodes[3].childNodes[1];
                    if (cap.childNodes[9].innerHTML.substring(1, 2) === "-") {cap.childNodes[9].style.color = "red"}
                    else {cap.childNodes[9].style.color = "green"}
                }
            }
        });
    });

    document.querySelectorAll(".spread").forEach(function (elem) {
        elem.addEventListener("click", function(event) {
            if (event.currentTarget.childNodes[2].id.substring(0, 1) === "T") {
                document.querySelector(`#id_DLR_TO`).value = event.currentTarget.childNodes[2].innerHTML.replace(',', '')
            } else {
                document.querySelector(`#id_DLR_U_TO`).value = event.currentTarget.childNodes[2].innerHTML.replace(',', '')
            }
        })
    })

    document.querySelectorAll(".FX_lookup").forEach(function (elem) {
        elem.addEventListener("change", function(event) {
            if (event.currentTarget.value != "") {
                fx(event.currentTarget.id, event.currentTarget.value)
            }
        })
    })
    document.querySelector("#id_initial_fx").addEventListener("change", function(event) {
        order_trades()
    })
    document.querySelector("#toggle_descriptions").addEventListener("click", function(event) {
        if (event.currentTarget.checked) {
            var checked = 'block'
        } else {
            var checked = 'none'
        }
        document.querySelectorAll(".description").forEach(function (elem) {
            elem.style.display = checked
        })
    })
});

function order_trades() {
    var value = document.querySelector("#id_initial_fx").value;
    if (["CAD", "USD"].includes(value)) {
        document.querySelector("#initial-type").innerHTML = "$";
        document.querySelector("#to-convert").innerHTML = "Cash to convert";
    } else {
        document.querySelector("#initial-type").innerHTML = "#";
        document.querySelector("#to-convert").innerHTML = "Shares to convert";
    }
    if (document.querySelector("#td_cad").parentElement.childNodes[1].id.substring(3, 7).toUpperCase() != value) {
        if (document.querySelector("#td_cad").parentElement.childNodes[1].childNodes[2].id.split('_')[1]  != value) {
            td_cad = document.querySelector("#td_cad")
            td_usd = document.querySelector("#td_usd")
            var temp = document.createElement("div");
            td_cad.parentNode.insertBefore(temp, td_cad);
            td_usd.parentNode.insertBefore(td_cad, td_usd);
            temp.parentNode.insertBefore(td_usd, temp);
            temp.parentNode.removeChild(temp);
        }
    }
}

function fx(target, date) {
    fetch(`https://www.bankofcanada.ca/valet/observations/FXUSDCAD?start_date=${date}&end_date=${date}`)
    .then(response => {
        if (response.ok) return response.json()
        throw new Error('Network response was not ok.')
    })
    .then(data => {
        if (data.observations.length == 0) {
            alert("No data available for the selected date. Data available Jan 2017 - most recent business day. Please see https://www.bankofcanada.ca/ for more info.")
        } else {
            document.querySelector(`#id_${target}`).value = data.observations[0].FXUSDCAD.v
        }
    });
}

function getCookie(name) {
let cookieValue = null;
if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
        }
    }
}
return cookieValue;
}