// 키워드 삭제
$(document).ready( function () {
    $("#deleteKeyword").click( function() {

        var seq = $("#seq").val();

        if (confirm("정말 삭제하시겠습니까?") == true) {    //확인

            var keywordArray = new Array();
            var companyArray = new Array();

            $("input:checkbox:checked").each(function (index) { // 선택된 키워드 저장
                keywordArray.push($(this).val());
                companyArray.push($(this)[0].getAttribute('company'));
            });

            $.ajax({
                url: "/manage_keyword/delete",
                type: "post",
                dataType : "json",
                data: {seq:seq, keyword:keywordArray, company:companyArray},
                success: function(data) {
                    location.href="/manage_keyword";
                },
                error: function(data) {
                    alert("키워드 삭제에 실패하였습니다.");
                }
            });
        } else {   //취소
            return;
        }
    });
});