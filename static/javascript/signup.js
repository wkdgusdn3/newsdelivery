// 회원가입시 비밀번호 체크
$(document).ready( function () {
    $("#password_confirm").change(function() {   //  email validation
    	var password = $("#password").val();

    	if(password != $(this).val()){
    		$("#password_valid_check").html("<font color ='red'>비밀번호를 다시 확인해 주세요.</font>");
    	}else{
    		$("#password_valid_check").html("");
    	}
    }); 
});

function signUp() {
	var email = $("#email").val();
	var password = $("#password").val();
	var password_confirm = $("#password_confirm").val();
	var birth = $("#birth").val();
	var sex = $("#sex").val();

	if(!emailCheck(email)) {
		alert("메일 형식에 맞지 않습니다.\n다시 입력해주세요.")
		return null;
	}

	if(password != password_confirm) { // 비밀번호 check
		alert("비밀번호가 다릅니다.");
		return null;
	}

	$.ajax({
		url: "/signup/signup",
		type: "post",
		dataType : "json",
		data: {email:email, password:SHA256(password), birth:birth, sex:sex},
		success: function(data) {
			var json = JSON.parse(JSON.stringify(data));
			if(json.status == "success") {
				alert("회원가입이 완료되었습니다.");
				location.href='/';	
			} else {
				alert("회원가입에 실패하였습니다.");	
			}
		},
		error: function(data) {
			alert("회원가입에 실패하였습니다.");
		}
	});
}

function emailCheck(email) {
	
	re=/^[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*@[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*.[a-zA-Z]{2,3}$/i;

	if(re.test(email)) {
		return true;
	}

	return false;
}