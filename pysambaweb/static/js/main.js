$(document).ready(function() {

    if( ($('#language').val()).indexOf("es") !== -1 ){
        $._.setLocale('es');
    }

    jQuery.validator.addMethod(
        "textOnly", 
        function(value, element) { return /^[a-zA-Z0-9_]+$/.test(value); }, 
        $._("Field alphanumeric and symbols _")
        );
    jQuery.validator.addMethod(
        "notEqual",
        function(value, element, params) {
            if ( value == $(params).val() ) { return false; 
            } else{ return true; };
        },
        $._("Your new password has not changed")
        );

    $('#formpasswd').validate({
        rules: {
            nickname: {
                required : true,
                minlength: 2,
                textOnly : true
            },
            oldpasswd: {
                required : true,
                minlength: 10,
                textOnly : true
            },
            newpasswd: {
                required : true,
                minlength: 10,
                textOnly : true,
                notEqual : '#oldpasswd'
            },
            retpasswd: {
                required : true,
                minlength: 10,
                textOnly : true,
                equalTo : '#newpasswd'
            }
        },
        messages: {
            nickname: {
                required: $._("This field is required"),
                minlength: $._("{0} Minimum  characters")
            },
            oldpasswd: {
                required: $._("This field is required"),
                minlength: $._("{0} Minimum  characters")
            },
            newpasswd: {
                required: $._("This field is required"),
                minlength: $._("{0} Minimum  characters")
            },
            retpasswd: {
                required: $._("This field is required"),
                minlength: $._("{0} Minimum  characters"),
                equalTo: $._("Confirm your new password")
            }
        },
        highlight: function(element) {
            $(element).closest('.control-group')
            .removeClass('success').addClass('error');
        },
        success: function(element) {
            $(element)
            .text('OK!').addClass('valid')
            .closest('.control-group').removeClass('error')
            .addClass('success').removeClass('fail');
        }
    });
});

//$('button#listfile.btn.btn-danger').on("click", function() {
//	var filename=$(this).attr("filename");
//	//var count=$(this).attr("data-target");
//	var count=$(this).attr("data-target");
//	$.ajax({
//		url: "/permission",
//		data: {filename:filename},
//		dataType: "json",
//		type: "GET",
//		success: function(result) {
//			var html = '';
//			var r = '';
//			var w = '';
//			var x = '';
//			$.each(result, function(user, permit){
//				if(permit[0] == 1){
//					r = "checked='checked'";
//				} else {
//					r = '';
//				}
//				if(permit[1] == 1){
//					w = "checked='checked'";
//				} else {
//					w = '';
//				}
//				if(permit[2] == 1){
//					x = "checked='checked'";
//				} else {
//					x = '';
//	
//	
//	
//			}
//				html += "<div id='just' filename='"+filename+"' user='"+user+"'>";
//				html += "<button class='btn btn-primary'>"+user+"</button>&nbsp&nbsp;";
//				html += "<label class='checkbox inline'><input type='checkbox' id='r' value='r' "+r+">读权限</label>"
//				html += "<label class='checkbox inline'><input type='checkbox' id='w' value='w' "+w+">写权限</label>"
//				html += "<label class='checkbox inline'><input type='checkbox' id='x' value='x' "+x+">列目录权限</label>"
//					html += "<label class='checkbox inline'><input type='button' id='btn1'  value='提交'></label><br></div>"
//			});
//			$("h6"+count).html(html);
//		},
//		failure: function(result) {
//			alert('fail');
//		},
//		
//		error: function(result) {
//			alert('error');
//		}
//	});
//}
//);

//$('.collapse').on("click","input[type='button']", function(e){
//	//被点击的元素的父父节点(div id = just)
//	focusdiv = $(this).parent().parent();
//
//	var filename = focusdiv.attr('filename');
//	var user  = focusdiv.attr('user');
//	var checked = [];
//	var permission = '';
//	focusdiv.find('input[type=checkbox]:checked').each(function() {
//		checked.push($(this).val());
//	});
//	permission = checked.join('');
//	$.ajax({
//		url: "/changepermission",
//		data: {filename:filename, user:user, permission:permission},
//		dataType: "json",
//		type: "GET",
//		success: function(result) {
//			alert(result);
//			button = focusdiv.parent().parent().prev();
//			button.click();
//			button.click();
//		},
//		failure: function(result) {
//			alert('fail');
//		},
//		
//		error: function(result) {
//			alert('error');
//		}
//	});
//
//});



function listfile(filename, num, groupname) {
	$.ajax({
		url: "/permission",
		data: {filename:filename, groupname: groupname},
		dataType: "json",
		type: "GET",
		success: function(result) {
			var html = '';
			var r = '';
			var w = '';
			var x = '';
			$.each(result, function(user, permit){
				if(permit[0] == 1){
					r = "checked='checked'";
				} else {
					r = '';
				}
				if(permit[1] == 1){
					w = "checked='checked'";
				} else {
					w = '';
				}
			    
                html += "<div id='"+groupname+"' filename='"+filename+"' user='"+user+"'>";
				html += "<label class='label label-primary'><i class='icon-user icon-white'></i>"+user+"</label>&nbsp&nbsp;";
				html += "<label class='checkbox inline'><input type='checkbox' id='r' value='r' "+r+">读权限</label>";
				html += "<label class='checkbox inline'><input type='checkbox' id='w' value='w' "+w+">写权限</label>";
				html += "<label class='checkbox inline'><input type='button' filename ='"+filename+"' user='"+user+"' id='"+groupname+"'  value='提交' onclick=\"changepermission.call(this);\"></label><br></div>";
			});
			$("h6#"+num).html(html);
		},
		failure: function(result) {
			Notify.error('操作失败');
		},
		
		error: function(result) {
			Notify.error('与服务器通讯异常');
		}
	});
}

function changepermission() {
	//被点击的元素的父父节点(div id = just)
	filename = $(this).attr('filename');
	user = $(this).attr('user');
	groupname = $(this).attr('id');
	focusdiv = $(this).parent().parent();
	var checked = [];
	var permission = '';
	focusdiv.find('input[type=checkbox]:checked').each(function() {
		checked.push($(this).val());
	});
	permission = checked.join('');
	$.ajax({
		url: "/changepermission",
		data: {filename:filename, user:user, permission:permission, groupname:groupname},
		dataType: "json",
		type: "GET",
		success: function(result) {
			Notify.success("修改用户"+user+"权限成功");
			console.info(focusdiv.parent().parent());
			listfile(filename, focusdiv.parent().parent().prev().attr('count'), groupname);
		},
		failure: function(result) {
			alert('fail');
		},
		
		error: function(result) {
			alert('error');
		}
	});
}


//list share for index
//$('button#listshare.btn.btn-danger').on("click", function() {
//	var groupname=$(this).attr("groupname");
//	var count=$(this).attr("data-target");
//	$.ajax({
//		url: "/listshareuser",
//		data: {groupname:groupname},
//		dataType: "json",
//		type: "GET",
//		success: function(result) {
//			var html = '';
//			$.each(result, function(key,user){
//				html += "<div id='shareuser' groupname='"+groupname+"' user='"+user+"'>";
//				html += "<a class='btn btn-primary' href='#'><i class='icon-user icon-white'></i>" + user + "</a>";
//				html += "<a class='btn' href='#' onclick=\"deluser('"+user+"','"+groupname+"');\"><i class='icon-trash'></i>删除</a>";
//				html += "</div>"
//			});
//			html += "<a href='#myModal' role='button' data-toggle='modal' class ='btn' href='#' onclick=\"listuser('"+groupname+"');\">添加用户</a>";
//			html += "<div aria-hidden='true' aria-labelledby='myModalLabel' role='dialog' tabindex='-1' class='modal hide fade' id='myModal' style='display:none;' data-keyboard='false'>";
//			html += "<div class='modal-header'>";
//			html += "<button aria-hidden='true' data-dismiss='modal' class='close' type='button'>x</button>";
//			html += "<h3 id='myModalLabel'>添加用户</h3></div>";
//			html += "<div class='modal-body'><h4>test</h4></div";
//			html += "<div calss='modal-footer'><button data-dismiss='modal' class='btn'>关闭</button></div></div>";
//			$("p"+count).html(html);
//			//alert('ok');
//		},
//		failure: function(result) {
//			alert('fail');
//		},
//		
//		error: function(result) {
//			alert('error');
//		}
//	});
//}
//);

function listshareuser(groupname) {
	$.ajax({
		url: "/listshareuser",
		data: {groupname:groupname},
		dataType: "json",
		type: "GET",
		success: function(result) {
			var html = '';
			$.each(result, function(key,user){
				html += "<div id='shareuser' groupname='"+groupname+"' user='"+user+"'>";
				html += "<div class='row-fluid show-grid'><div class='span1'><label class='label label-info' href='#'><i class='icon-user icon-white'></i>" + user + "</label></div>";
				html += "<div class='span2'><label class='label label-important' onclick=\"deluser('"+user+"','"+groupname+"');\"><i class='icon-trash'></i>删除</label></div>";
				html += "</div></div>"
			});

		    html +=  "<input type='input' id='username"+groupname+"'>" 
            html += "<a href='#myModal' role='button' data-toggle='modal' class ='btn' href='#' onclick=\"listuser('"+groupname+"',document.getElementById('username"+groupname+"').value);\">添加用户</a>";
			html += "<div aria-hidden='true' aria-labelledby='myModalLabel' role='dialog' tabindex='-1' class='modal hide fade' id='myModal' style='display:none;' data-keyboard='false'>";
			html += "<div class='modal-header'>";
			html += "<button aria-hidden='true' data-dismiss='modal' class='close' type='button' onclick=\"listshareuser('"+groupname+"')\">x</button>";
			html += "<h3 id='myModalLabel'>添加用户</h3></div>";
			html += "<div class='modal-body'><h4>&nbsp</h4>";
			html += "<div calss='modal-footer'><button data-dismiss='modal' class='btn' onclick=\"listshareuser('"+groupname+"')\">关闭</button></div></div>";
			$("p#"+groupname).html(html);

		},
		failure: function(result) {
			alert('fail');
		},
		
		error: function(result) {
			alert('error');
		}
	});
}

function listuser(groupname, user) {
	$.ajax({
		url: "/listuserinformation",
		data: {user:user},
		dataType: "json",
		type: "GET",
		success: function(result) {
			    var html = "";
            if(result.status == true) { 
                html += "<p>"+result.msg+"</p>";
                html += "<br><label class='btn btn-success' onclick=\"adduser('"+user+"','"+groupname+"');\"><i class='icon icon-user'></i>"+user+"</label>";
        }
            else {
                html += "<div class='alert'><button type='button' class='close' data-dismiss='alert'>&times;</button><strong>Warning!</strong>";
                html += result.msg+"</div>";
                Notify.error(result.msg);
            }
            $("h4").html(html);
		},
		failure: function(result) {
            Notify.error(result.msg);
		},
		
		error: function(result) {
            Notify.error('通讯故障listuser');
		}
	});
}

function adduser(user, groupname) {
	$.ajax({
		url: "/adduser",
		data: {'groupname':groupname,'username':user},
		dataType: "json",
		type: "GET",
		success: function(result) {
            if(result.status == true) {
			    //listuser(groupname);
			    Notify.success(result.msg);
                var html = '';
                html += "我们已经给"+user+"添加了访问权限";
                $("h4").html(html);
            }
            else {
                Notify.error(result.error);
            }
		},
		failure: function(result) {
			Notify.error("赋予用户"+user+"访问权限失败");
		},
		
		error: function(result) {
			Notify.error('与服务器通讯异常');
		}
	});
}

function deluser(user, groupname) {
	$.ajax({
		url: "/removeuserfromgroup",
		data: {groupname:groupname,username:user},
		dataType: "json",
		type: "GET",
		success: function(result) {
			listshareuser(groupname);
			Notify.success("去除用户"+user+"访问权限成功");
		},
		failure: function(result) {
			Notify.error("去除用户"+user+"fail");
		},
		
		error: function(result) {
			Notify.error('与服务器通讯故障');
		}
	});

}



function addfolder(path, groupname, foldername) {
    $.ajax({
		url: "/addfolder",
        timeout: 10000,
		data: {path:path, groupname:groupname, foldername:foldername},
		dataType: "json",
		type: "GET",
		success: function(result) {
        if (result.status == true) {
            Notify.success(result.msg);
            setTimeout('location.reload()', 1000); 

        }
        else {
            Notify.error(result.msg);
            setTimeout('location.reload()', 2000); 
        }
		},
		failure: function(result) {
            Notify.error('操作失败，请联系管理员');
		},
		
		error: function(result) {
            Notify.error('与服务器通讯故障');
		}
	});
}

function addshare(sharename) {
    $.ajax({
		url: "/addshare",
        timeout: 10000,
		data: {sharename:sharename},
		dataType: "json",
		type: "GET",
		success: function(result) {
        if (result.status == true) {
            Notify.success(result.msg);
            setTimeout('location.reload()', 1000); 

        }
        else {
            Notify.error(result.msg);
            setTimeout('location.reload()', 2000); 
        }
		},
		failure: function(result) {
            Notify.error('操作失败，请联系管理员');
		},
		
		error: function(result) {
            Notify.error('与服务器通讯故障');
		}
	});
}

function listgroups(user) {
	$.ajax({
		url: "/listavailgroups",
		data: {user:user},
		dataType: "json",
		type: "GET",
		success: function(result) {
			var html = '';
			$.each(result, function(key, group){
				html += "<label class='label label-info' group='"+group+"' user='"+user+"' onclick=\"addadmin('"+user+"','"+group+"')\"><i class='icon-user icon-white'></i>"+group+"</label>&nbsp";
			});
			$("p#listadmin").html(html);
		},
		failure: function(result) {
            Notify.error('操作失败，请联系管理员');
		},
		
		error: function(result) {
            Notify.error('与服务器通讯故障');
		}
	});
}

function renamefolder(path, filename, newname) {
	$.ajax({
		url: "/renamefolder",
		data: {'path':path, 'filename':filename, 'newname': newname},
		dataType: "json",
		type: "GET",
		success: function(result) {
            if (result.status == true) {
                Notify.success(result.msg);
                setTimeout('location.reload()', 2000); 
            }
            else {
                Notify.error(result.msg);
            }
		},
		failure: function(result) {
            Notify.error('操作失败，请联系管理员');
		},
		
		error: function(result) {
            Notify.error('与服务器通讯故障');
		}
	});


}

function renameshare(sharename, newname) {
    //alert(sharename+newname);
	$.ajax({
		url: "/renameshare",
		data: {'sharename':sharename, 'newname': newname},
		dataType: "json",
		type: "GET",
		success: function(result) {
            if (result.status == true) {
                Notify.success(result.msg);
                setTimeout('location.reload()', 2000); 
            }
            else {
                Notify.error(result.msg);
            }
		},
		failure: function(result) {
            Notify.error('操作失败，请联系管理员');
		},
		
		error: function(result) {
            Notify.error('与服务器通讯故障');
		}
	});
}


//全站顶部通知
Notify = {
	success: function(txt){
		var a = noty({"text": txt, layout:"top", type:"success",timeout:1000});
	},
	error: function(txt){
		var b = noty({"text":txt, layourt:"top", type:"error", timeout:2000});
	}
};
