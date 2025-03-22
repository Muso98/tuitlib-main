/**
 * Copyright since 2007 PrestaShop SA and Contributors
 * PrestaShop is an International Registered Trademark & Property of PrestaShop SA
 *
 * NOTICE OF LICENSE
 *
 * This source file is subject to the Academic Free License 3.0 (AFL-3.0)
 * that is bundled with this package in the file LICENSE.md.
 * It is also available through the world-wide-web at this URL:
 * https://opensource.org/licenses/AFL-3.0
 * If you did not receive a copy of the license and are unable to
 * obtain it through the world-wide-web, please send an email
 * to license@prestashop.com so we can send you a copy immediately.
 *
 * DISCLAIMER
 *
 * Do not edit or add to this file if you wish to upgrade PrestaShop to newer
 * versions in the future. If you wish to customize PrestaShop for your
 * needs please refer to https://devdocs.prestashop.com/ for more information.
 *
 * @author    PrestaShop SA and Contributors <contact@prestashop.com>
 * @copyright Since 2007 PrestaShop SA and Contributors
 * @license   https://opensource.org/licenses/AFL-3.0 Academic Free License 3.0 (AFL-3.0)
 */

$(function(){
	if(!!('ontouchstart' in window)){		
		$('html').bind('touchstart', function(){
			showDialog();
			$("html").unbind("touchstart");
		});
	} else{
		$("html").bind("mouseleave", function () { 
			showDialog();
			$("html").unbind("mouseleave");
		});
	}
});

function createCookie(cookiename, cookievalue, exdays) {
	const d = new Date();
	d.setTime(d.getTime() + (exdays*60*60*1000));
	let expires = "expires="+ d.toUTCString();
	document.cookie = cookiename + "=" + cookievalue + ";" + expires + ";path=/";
}

function getCookie(cookiename) {
	let name = cookiename + "=";
	let decodedCookie = decodeURIComponent(document.cookie);
	let ca = decodedCookie.split(';');
	for(let i = 0; i <ca.length; i++) {
	  let c = ca[i];
	  while (c.charAt(0) == ' ') {
		c = c.substring(1);
	  }
	  if (c.indexOf(name) == 0) {
		return c.substring(name.length, c.length);
	  }
	}
	return "";
}

function showDialog()
{  
	if (!getCookie("cookieCouponPopup")) {	
		var data={'task':'showPopup'};
		$.ajax({
			type: "POST",
			cache: false,
			url: cz_coupon_url + '/front-end-ajax.php',
			dataType : "json",
			data: data,
			complete: function(){},
			success: function (response) {
				//console.log(response);
			}
		});   
		setTimeout(function(){
			$("#overlay").show();
			$(".newsletter-main").show();
		}, 500);
	}
}

function closeDialog(cookies_time)
{  
	var data={'task':'cancelRegisNewslette1', 'cookies_time':cookies_time};       
	if ($('#notshow').is(':checked')){
		data.notshow = '1';
		createCookie('cookieCouponPopup','closed',cookies_time);
    }else{
        data.notshow = '0';
    }

	$.ajax({
		type: "POST",
		cache: false,
		url: cz_coupon_url + '/front-end-ajax.php',
		dataType : "json",
		data: data,
		complete: function(){},
		success: function (response) {
			//console.log(response);
		}
	});  

	setTimeout(function(){
		$("#overlay").hide();
		$(".newsletter-main").hide();
	}, 500);
}
function check_email(email){
	emailRegExp = /^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.([a-z]){2,4})$/;	
	if(emailRegExp.test(email)){
		return true;
	}else{
		return false;
	}
}
function regisNewsletter(){
    var data={'task':'regisNewsletter', 'action':0};
    var email = $("#newsletter_input_email").val();
    if(check_email(email) == true){
        data.email = email;
        $("#regisNewsletterMessage").html("");
    }else{
        $("#regisNewsletterMessage").html('<p class="alert alert-danger">'+enterEmail+'</p>');
        return false;
    }
    
    if ($('#notshow').is(':checked')){
		data.notshow = '1';
		createCookie('cookieCouponPopup','closed',cookies_time);
    }else{
        data.notshow = '0';
    }
    $.ajax({
		type: "POST",
		cache: false,
		url: cz_coupon_url + '/front-end-ajax.php',
		dataType : "json",
		data: data,
        complete: function(){},
		success: function (response)
		{

			if(response.indexOf("@")>0)
			{
				var new_response = response.substring(response.indexOf("@")+1, response.length);
				$("#regisNewsletterMessage").html('<p class="alert alert-success">'+new_response+'</p>');
			}
			else {
				$("#regisNewsletterMessage").html('<p class="alert alert-warning">'+response+'</p>');
			}
			$("#coupon-text-before").hide();
			$("#coupon-text-after").show();
			
		},
		 error: function(XMLHttpRequest, textStatus, errorThrown) { 
            alert("Status: " + textStatus); 
            alert("Error: " + errorThrown);
        }  
	});
}