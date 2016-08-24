function registerKeyword() {
	var seq = $("#seq").val();
	var keyword = $("#keyword").val();
	var company = $("#company").val();

	$.ajax({
		url: "/register_keyword/insert",
		type: "post",
		dataType : "json",
		data: {seq:seq, keyword:keyword, company:company},
		success: function(data) {
			alert("키워드를 등록하였습니다.");
			$("#keyword").val("");
		},
		error: function(data) {
			alert("키워드 등록에 실패하였습니다.")
		}
	});
}