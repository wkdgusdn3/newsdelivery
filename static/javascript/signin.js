function signIn() {
	var email = $("#email").val();
	var password = $("#password").val();

	$.ajax({
		url: "/signin/signin",
		type: "post",
		dataType : "json",
		data: {email:email, password:SHA256(password)},
		success: function(data) {
			var json = JSON.parse(JSON.stringify(data));
			if(json.status == "success") {
					location.href="/";
			} else {
				alert("로그인에 실패하였습니다.");
			}
		},
		error: function(data) {
			alert("로그인에 실패하였습니다.");
		}
	});
}