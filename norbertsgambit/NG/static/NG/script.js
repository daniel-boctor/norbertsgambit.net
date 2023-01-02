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

    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl)
    })
});