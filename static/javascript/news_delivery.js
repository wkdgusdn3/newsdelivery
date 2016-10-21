// menuBar active 관리
$(document).ready( function () {
    var selected = document.location.pathname;
    
    switch(selected) {
        case "/main" :
        $("li[name='menuBar'][value='0']").addClass('active');
        break;
        case "/delivered_news" :
        $("li[name='menuBar'][value='1']").addClass('active');
        break;
        case "/register_keyword" :
        $("li[name='menuBar'][value='2']").addClass('active');
        break;
        case "/manage_keyword" :
        $("li[name='menuBar'][value='3']").addClass('active');
        break;
        case "/manage_info" :
        $("li[name='menuBar'][value='4']").addClass('active');
        break;
    }
});

function logOut() {
    $.ajax({
        url: "/logout",
        type: "post",
        success: function(data) {
            location.href='/';
        }
    });
}