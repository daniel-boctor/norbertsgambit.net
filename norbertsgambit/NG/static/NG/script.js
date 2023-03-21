document.addEventListener('DOMContentLoaded', function() {

    if (window.location.pathname != "/") {
        document.querySelectorAll('.nav-link').forEach(function(nav_link) {
            if (window.location.pathname.includes(nav_link.getAttribute("href"))) {
                nav_link.className += " active";
                nav_link.setAttribute("aria-current", "page");
                nav_link.style.textDecoration = "underline"; 
            }
        });
    }
    
});

theme_selector({update_selector: false})

$(document).ready(function() {
    $('[data-bs-toggle="popover"]').popover({html:true});
    $('.toast').toast('show');
    theme_selector({update_theme: false})
});

function theme_selector({theme=localStorage.getItem('theme') ?? 'default', update_theme=true, update_selector=true}={}) {
    if (update_theme) {
        if (theme === 'default') {
            document.getElementById("glass_css").disabled = true
        } else if (theme === 'glass') {
            document.getElementById("glass_css").disabled = false
        }
    }
    if (update_selector) {
        var selected = document.getElementById(theme)
        $(selected).addClass('active');
        $('.dropdown-item').not(selected).removeClass('active')
        localStorage.setItem("theme", selected.id)
    }
}