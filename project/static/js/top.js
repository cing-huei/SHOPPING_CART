
window.onscroll = function() {
    var top1 = document.getElementById("top-1");
    var logo = document.getElementById("logo");
    var btn1 = document.getElementById("btn-1");
    var scrollPosition = window.pageYOffset || document.documentElement.scrollTop;

    if (scrollPosition > 0) {
        top1.style.top = scrollPosition + "px";
        logo.style.display = "none";
        btn1.style.top = scrollPosition + "px";
    } else {
        top1.style.top = "";
        logo.style.display = "block";
        btn1.style.top = "";
    }
};