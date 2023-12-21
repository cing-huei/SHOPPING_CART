function doublecheck_login() {
    if (confirm("請先登入會員")) {
        window.location.href = '/login/';
    } 
}