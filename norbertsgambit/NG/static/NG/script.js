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

$(document).ready(function() {
    $('[data-bs-toggle="popover"]').popover({html:true});
});