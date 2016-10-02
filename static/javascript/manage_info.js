function updateInfo() {
	var seq = $("#seq").val();
	var password = $("#password").val();
	var password_confirm = $("#password_confirm").val();
	var birth = $("#birth").val();
	var sex = $("#sex").val();

	if(password != password_confirm) { // 비밀번호 check
		alert("비밀번호가 다릅니다.");
		return null;
	}

	if(password == "") {	// 비밀번호 입력 o
		$.ajax({
			url: "/manage_info/update",
			type: "post",
			dataType : "json",
			data: {seq:seq, birth:birth, sex:sex},
			success: function(data) {
				var json = JSON.parse(JSON.stringify(data));
				if(json.status == "success") {
					alert("회원정보 변경이 완료되었습니다.");
					location.href='/';	
				} else {
					alert("회원정보 변경에 실패하였습니다.");	
				}
			},
			error: function(data) {
				alert("회원정보 변경에 실패하였습니다.");	
			}
		});
	} else {				// 비밀번호 입력 x
		$.ajax({
			url: "/manage_info/update",
			type: "post",
			dataType : "json",
			data: {seq:seq, password:SHA256(password), birth:birth, sex:sex},
			success: function(data) {
				var json = JSON.parse(JSON.stringify(data));
				if(json.status == "success") {
					alert("회원정보 변경이 완료되었습니다.");
					location.href='/';	
				} else {
					alert("회원정보 변경에 실패하였습니다.");	
				}
			},
			error: function(data) {
				alert("회원정보 변경에 실패하였습니다.");	
			}
		});
	}
}