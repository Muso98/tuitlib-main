/**
 * 2010-2019 Codezeel
 *
 * NOTICE OF LICENSE
 *
 * Tm feature for prestashop 1.7: compare, wishlist at product list 
 *
 * DISCLAIMER
 *
 *  @Module Name: CZ Feature
 *  @author    codezeel <support@codezeel.com>
 *  @copyright 2010-2019 codezeel
 *  @license   http://www.codezeel.com - prestashop template provider
 */
$(document).ready(function(){
	createStWishlistModalPopup();
	StWishlistButtonAction();
	prestashop.on('updateProductList', function() {
		StWishlistButtonAction();
	});
	prestashop.on('clickQuickView', function() {		
		check_active_wishlist = setInterval(function(){
			if($('.quickview.modal').length)
			{			
				$('.quickview.modal').on('shown.bs.modal', function (e) {
					StWishlistButtonAction();
				})
				clearInterval(check_active_wishlist);
			}
			
		}, 300);
		
	});
	
	// $('.quickview.modal').on('shown.bs.modal', function (e) {
			// console.log('aaa');
	// })
	activeEventModalWishlist();
	StListWishlistAction();
	$('.st-save-wishlist-bt').click(function(){
		if (!$(this).hasClass('active'))
		{
			$(this).addClass('active');
			$('.new-wishlist .has-danger .form-control-feedback').html('');
			$('.new-wishlist .has-success .form-control-feedback').html('');
			var name_wishlist = $.trim($('#wishlist_name').val());
			if (!name_wishlist)
			{
				$('#wishlist_name').parent().addClass('has-error');
				$(this).removeClass('active');
			}
			else
			{
				var object_e = $(this);
				$('#wishlist_name').parent().removeClass('has-error');
				$('.st-save-wishlist-bt-text').hide();
				$('.st-save-wishlist-loading').css({'display':'block'});
				$.ajax({
					type: 'POST',
					headers: {"cache-control": "no-cache"},
					url: wishlist_url,
					async: true,
					cache: false,
					data: {
						"ajax": 1,
						"action": "add-wishlist",
						"name_wishlist": name_wishlist,					
					},
					success: function (result)
					{
						var object_result = $.parseJSON(result);
						if (object_result.errors.length)
						{
							// console.log(object_result.errors);
							$('.new-wishlist .has-success .form-control-feedback').html('');
							$('.new-wishlist .has-danger .form-control-feedback').html(object_result.errors).fadeIn();
						}
						else
						{
							$('.new-wishlist .has-danger .form-control-feedback').html('');
							$('.new-wishlist .has-success .form-control-feedback').html(object_result.result.message).fadeIn();
							setTimeout(function() {
								$('.new-wishlist .has-success .form-control-feedback').fadeOut();
							}, 3000);
							$('#wishlist_name').val('');
							
							$('.list-wishlist table tbody').append(object_result.result.wishlist);
							$('html, body').animate({
								scrollTop: $('.list-wishlist table tr.new').offset().top
							}, 500, function (){
								$('.list-wishlist table tr.new').removeClass('new');
							});
							StListWishlistAction();
							//DONGND:: reload list product if a wishlist current view
							$('.list-wishlist tr.show .view-wishlist-product').trigger('click');
						}
						$('.st-save-wishlist-bt-text').show();
						$('.st-save-wishlist-loading').hide();
						object_e.removeClass('active');
					},
					error: function (XMLHttpRequest, textStatus, errorThrown) {
						alert("TECHNICAL ERROR: \n\nDetails:\nError thrown: " + XMLHttpRequest + "\n" + 'Text status: ' + textStatus);
					}
				});
				
			}
		}
		return false;
	})
});

function createStWishlistModalPopup()
{
	var leoWishlistModalPopup = '';
	leoWishlistModalPopup += '<div class="modal st-modal st-modal-wishlist fade" tabindex="-1" role="dialog" aria-hidden="true">';
		leoWishlistModalPopup += '<div class="modal-dialog" role="document">';
			leoWishlistModalPopup += '<div class="modal-content">';
				leoWishlistModalPopup += '<div class="modal-header">';
					leoWishlistModalPopup += '<button type="button" class="close" data-dismiss="modal" aria-label="Close">';
						leoWishlistModalPopup += '<span aria-hidden="true">&times;</span>';
					leoWishlistModalPopup += '</button>';
					leoWishlistModalPopup += '<h5 class="modal-title text-xs-center">';
					leoWishlistModalPopup += '</h5>';
				leoWishlistModalPopup += '</div>';
				leoWishlistModalPopup += '<div class="modal-footer">';			
					leoWishlistModalPopup += '<button type="button" class="btn btn-secondary" data-dismiss="modal">'+wishlist_cancel_txt+'</button>';
					leoWishlistModalPopup += '<button type="button" class="st-modal-wishlist-bt btn btn-primary">';						
						leoWishlistModalPopup += '<span class="st-modal-wishlist-loading cssload-speeding-wheel"></span>';
						leoWishlistModalPopup += '<span class="st-modal-wishlist-bt-text">';
							leoWishlistModalPopup += wishlist_ok_txt;
						leoWishlistModalPopup += '</span>';
					leoWishlistModalPopup += '</button>';				
				leoWishlistModalPopup += '</div>';
			leoWishlistModalPopup += '</div>';
		leoWishlistModalPopup += '</div>';
	leoWishlistModalPopup += '</div>';
	$('body').append(leoWishlistModalPopup);
}

function StWishlistButtonAction()
{
	if (!$('.st-wishlist-button').hasClass('show-list'))
	{
		$('.st-wishlist-button').click(function(){
			if (!$('.st-wishlist-button.active').length)
			{			
				var id_product = $(this).data('id-product');
				var id_wishlist = $(this).data('id-wishlist');
				var id_product_attribute = $(this).data('id-product-attribute');
				var content_wishlist_mess_remove = wishlist_remove+'. <a href="'+wishlist_url+'" target="_blank"><strong>'+wishlist_viewwishlist+'.</strong></a>';
				var content_wishlist_mess_add = wishlist_add+'. <a href="'+wishlist_url+'" target="_blank"><strong>'+wishlist_viewwishlist+'.</strong></a>';			
				
				$(this).addClass('active');
				
				if (!isLogged)
				{
					$('.st-modal-wishlist .modal-title').html(wishlist_loggin_required);
					$('.st-modal-wishlist').modal('show');
					return false;
				}
				
				var object_e = $(this);
				object_e.find('.st-wishlist-bt-loading').css({'display':'block'});
				//object_e.find('.st-wishlist-bt-content').hide();
				if ($(this).hasClass('added') || $(this).hasClass('delete'))
				{
					//DONGND:: remove product form wishlist				
					$.ajax({
						type: 'POST',
						headers: {"cache-control": "no-cache"},
						url: wishlist_url,
						async: true,
						cache: false,
						data: {
							"ajax": 1,
							"action": "remove",
							"id_product": id_product,
							"id_wishlist": id_wishlist,
							"id_product_attribute": id_product_attribute,
							"quantity": 1,
						},
						success: function (result)
						{
							var object_result = $.parseJSON(result);
							if (object_result.errors.length)
							{
								$('.st-modal-wishlist .modal-title').html(object_result.errors);
								$('.st-modal-wishlist').modal('show');
							}
							else
							{
								//Sttheme add: update number product on icon wishlist after remove from wishlist								
								if ($('.ap-btn-wishlist .ap-total-wishlist').length)
								{								
									var old_num_wishlist = parseInt($('.ap-btn-wishlist .ap-total-wishlist').data('wishlist-total'));
									var new_num_wishlist = old_num_wishlist-1;
									$('.ap-btn-wishlist .ap-total-wishlist').data('wishlist-total',new_num_wishlist);
									$('.ap-btn-wishlist .ap-total-wishlist').text(new_num_wishlist);
								}
								
								// compared_products.splice($.inArray(parseInt(id_product), compared_products), 1);
								if (object_e.hasClass('delete'))
								{
									//DONGND:: remove from page wishlist
									$('td.product-'+id_product).fadeOut(function(){
										$(this).remove();
									});
								}
								else
								{
									//DONGND:: remove from page product list
									$('.st-modal-wishlist .modal-title').html(content_wishlist_mess_remove);
									$('.st-modal-wishlist').modal('show');
									$('.st-wishlist-button[data-id-product='+id_product+']').removeClass('added');
									$('.st-wishlist-button[data-id-product='+id_product+']').attr('title',buttonwishlist_title_add);
									object_e.find('.st-wishlist-bt-loading').hide();
									//object_e.find('.st-wishlist-bt-content').show();
								}
							}
						},
						error: function (XMLHttpRequest, textStatus, errorThrown) {
							alert("TECHNICAL ERROR: \n\nDetails:\nError thrown: " + XMLHttpRequest + "\n" + 'Text status: ' + textStatus);
						}
					});
				}
				else
				{

					//DONGND:: add product to list product wishlist
					$.ajax({
						type: 'POST',
						headers: {"cache-control": "no-cache"},
						url: wishlist_url,
						async: true,
						cache: false,
						data: {
							"ajax": 1,
							"action": "add",
							"id_product": id_product,
							"id_wishlist": id_wishlist,
							"id_product_attribute": id_product_attribute,
							"quantity": 1,
						},
						success: function (result)
						{
							 //console.log(result);
							var object_result = $.parseJSON(result);
							if (object_result.errors.length)
							{
								$('.st-modal-wishlist .modal-title').html(object_result.errors);
								$('.st-modal-wishlist').modal('show');
							}
							else
							{
								$('.st-modal-wishlist .modal-title').html(content_wishlist_mess_add);
								$('.st-modal-wishlist').modal('show');
								//Sttheme add: update number product on icon wishlist after add from wishlist								
								if ($('.ap-btn-wishlist .ap-total-wishlist').length)
								{								
									var old_num_wishlist = parseInt($('.ap-btn-wishlist .ap-total-wishlist').data('wishlist-total'));
									var new_num_wishlist = old_num_wishlist+1;
									$('.ap-btn-wishlist .ap-total-wishlist').data('wishlist-total',new_num_wishlist);
									$('.ap-btn-wishlist .ap-total-wishlist').text(new_num_wishlist);
								}
								
								// console.log(object_result.result.id_wishlist);
								//DONGND:: update id wishlist if the first add of user
								if (id_wishlist == '')
								{
									$('.st-wishlist-button').data('id-wishlist', object_result.result.id_wishlist);
									// wishlist_products[object_result.result.id_wishlist].push(id_product);
								}
								// else
								// {
									// wishlist_products[id_wishlist].push(id_product);
								// }
								
								$('.st-wishlist-button[data-id-product='+id_product+']').addClass('added');
								$('.st-wishlist-button[data-id-product='+id_product+']').attr('title',buttonwishlist_title_remove);
								object_e.find('.st-wishlist-bt-loading').hide();
								//object_e.find('.st-wishlist-bt-content').show();
							}
																		
						},
						error: function (XMLHttpRequest, textStatus, errorThrown) {
							alert("TECHNICAL ERROR: \n\nDetails:\nError thrown: " + XMLHttpRequest + "\n" + 'Text status: ' + textStatus);
						}
					});										
				}
			}
			return false;
		})
	}
	else
	{
		// $('.st-wishlist-button').each(function(){
			
			// $(this).click(function(e){
				
				// e.preventDefault();
			// });
			// var htmlContent =  $(this).next().html();
			// $(this).popover({
				// placement : 'bottom', //placement of the popover. also can use top, bottom, left or right
				// title : '', //this is the top title bar of the popover. add some basic css
				// html: true, //needed to show html of course
				// content : htmlContent,  //this is the content of the html box. add the image here or anything you want really.
				// template: '<div class="popover popover-list-wishlist" role="tooltip"><div class="popover-arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>'
			// });
			
		// });
		
		// $('.popover').popover('hide');
		
		// $('.st-wishlist-button').click(function(){
			// if ($(this).hasClass('active'))
			// {
				// $(this).next().fadeOut();
				// $(this).removeClass('active');
			// }
			// else
			// {
				// $('.st-wishlist-button.active').next().fadeOut();
				// $('.st-wishlist-button.active').removeClass('active');
				// $(this).addClass('active');
				// $(this).next().fadeIn();
			// }
			
			// return false;
		// });
		
		// $('.popover').on('show.bs.popover' , function () {
			//DONGND:: add/remove wishlist with list wishlist
			$('.wishlist-item').click(function(){
				if (!$('.wishlist-item.active-add').length)
				{			
					var id_product = $(this).data('id-product');
					var id_wishlist = $(this).data('id-wishlist');
					var id_product_attribute = $(this).data('id-product-attribute');
					var content_wishlist_mess_remove = wishlist_remove+'. <a href="'+wishlist_url+'" target="_blank"><strong>'+wishlist_viewwishlist+'.</strong></a>';
					var content_wishlist_mess_add = wishlist_add+'. <a href="'+wishlist_url+'" target="_blank"><strong>'+wishlist_viewwishlist+'.</strong></a>';			
					
					$(this).addClass('active-add');
					
					if (!isLogged)
					{
						$('.st-modal-wishlist .modal-title').html(wishlist_loggin_required);
						$('.st-modal-wishlist').modal('show');
						return false;
					}
					
					var object_e = $(this);
					var parents_e = object_e.parents('.st-wishlist-button-dropdown');
					parents_e.find('.st-wishlist-button').addClass('active');
					parents_e.find('.st-wishlist-bt-loading').css({'display':'block'});
					//parents_e.find('.st-wishlist-bt-content').hide();
					if ($(this).hasClass('added') || $(this).hasClass('delete'))
					{
						//DONGND:: remove product form wishlist				
						$.ajax({
							type: 'POST',
							headers: {"cache-control": "no-cache"},
							url: wishlist_url,
							async: true,
							cache: false,
							data: {
								"ajax": 1,
								"action": "remove",
								"id_product": id_product,
								"id_wishlist": id_wishlist,
								"id_product_attribute": id_product_attribute,
								"quantity": 1,
							},
							success: function (result)
							{
								var object_result = $.parseJSON(result);
								if (object_result.errors.length)
								{
									$('.st-modal-wishlist .modal-title').html(object_result.errors);
									$('.st-modal-wishlist').modal('show');
								}
								else
								{
									//Sttheme add: update number product on icon wishlist after remove from wishlist								
									if ($('.ap-btn-wishlist .ap-total-wishlist').length)
									{								
										var old_num_wishlist = parseInt($('.ap-btn-wishlist .ap-total-wishlist').data('wishlist-total'));
										var new_num_wishlist = old_num_wishlist-1;
										$('.ap-btn-wishlist .ap-total-wishlist').data('wishlist-total',new_num_wishlist);
										$('.ap-btn-wishlist .ap-total-wishlist').text(new_num_wishlist);
									}
									
									// compared_products.splice($.inArray(parseInt(id_product), compared_products), 1);
									if (object_e.hasClass('delete'))
									{
										//DONGND:: remove from page wishlist
										$('td.product-'+id_product).fadeOut(function(){
											$(this).remove();
										});
									}
									else
									{
										//DONGND:: remove from page product list
										$('.st-modal-wishlist .modal-title').html(content_wishlist_mess_remove);
										$('.st-modal-wishlist').modal('show');
										
										$('.wishlist-item[data-id-wishlist='+id_wishlist+'][data-id-product='+id_product+']').removeClass('added');
										$('.wishlist-item[data-id-wishlist='+id_wishlist+'][data-id-product='+id_product+']').attr('title',buttonwishlist_title_add);
										if (!$('.wishlist-item[data-id-product='+id_product+']').hasClass('added'))
										{
											$('.st-wishlist-button[data-id-product='+id_product+']').removeClass('added');
										}
										
										parents_e.find('.st-wishlist-bt-loading').hide();
										//parents_e.find('.st-wishlist-bt-content').show();
										parents_e.find('.st-wishlist-button').removeClass('active');
									}
								}
							},
							error: function (XMLHttpRequest, textStatus, errorThrown) {
								alert("TECHNICAL ERROR: \n\nDetails:\nError thrown: " + XMLHttpRequest + "\n" + 'Text status: ' + textStatus);
							}
						});
					}
					else
					{

						//DONGND:: add product to list product wishlist
						$.ajax({
							type: 'POST',
							headers: {"cache-control": "no-cache"},
							url: wishlist_url,
							async: true,
							cache: false,
							data: {
								"ajax": 1,
								"action": "add",
								"id_product": id_product,
								"id_wishlist": id_wishlist,
								"id_product_attribute": id_product_attribute,
								"quantity": 1,
							},
							success: function (result)
							{
								// console.log(result);
								var object_result = $.parseJSON(result);
								if (object_result.errors.length)
								{
									$('.st-modal-wishlist .modal-title').html(object_result.errors);
									$('.st-modal-wishlist').modal('show');
								}
								else
								{
									$('.st-modal-wishlist .modal-title').html(content_wishlist_mess_add);
									$('.st-modal-wishlist').modal('show');
									//Sttheme add: update number product on icon wishlist after add from wishlist								
									if ($('.ap-btn-wishlist .ap-total-wishlist').length)
									{								
										var old_num_wishlist = parseInt($('.ap-btn-wishlist .ap-total-wishlist').data('wishlist-total'));
										var new_num_wishlist = old_num_wishlist+1;
										$('.ap-btn-wishlist .ap-total-wishlist').data('wishlist-total',new_num_wishlist);
										$('.ap-btn-wishlist .ap-total-wishlist').text(new_num_wishlist);
									}
									
									// console.log(object_result.result.id_wishlist);
						
									$('.wishlist-item[data-id-wishlist='+id_wishlist+'][data-id-product='+id_product+']').addClass('added');
									$('.wishlist-item[data-id-wishlist='+id_wishlist+'][data-id-product='+id_product+']').attr('title',buttonwishlist_title_remove);
									if (!$('.st-wishlist-button[data-id-product='+id_product+']').hasClass('added'))
									{
										$('.st-wishlist-button[data-id-product='+id_product+']').addClass('added');
									}
									
									parents_e.find('.st-wishlist-bt-loading').hide();
									//parents_e.find('.st-wishlist-bt-content').show();
									parents_e.find('.st-wishlist-button').removeClass('active');
								}
																			
							},
							error: function (XMLHttpRequest, textStatus, errorThrown) {
								alert("TECHNICAL ERROR: \n\nDetails:\nError thrown: " + XMLHttpRequest + "\n" + 'Text status: ' + textStatus);
							}
						});										
					}
				}
				return false;
			});
		// });
		
	}
	
}

function StListWishlistAction()
{
	//DONGND:: click delete wishlist
	$('.delete-wishlist').click(function(){
		if (!$(this).hasClass('active'))
		{
			$(this).addClass('active');
			$(this).parents('tr').addClass('active');
			if ($('.list-wishlist tr.active .default-wishlist').is(":checked"))
			{
				$('.st-modal-wishlist .modal-title').html(wishlist_del_default_txt);
				$('.st-modal-wishlist').removeClass('enable-action').modal('show');
			}
			else
			{
				$('.st-modal-wishlist .modal-title').html(wishlist_confirm_del_txt);
				$('.st-modal-wishlist').addClass('enable-action').modal('show');
			}
		}
		
		return false;
	});
	
	//DONGND:: confirm delete wishlist
	$('.st-modal-wishlist-bt').click(function(){
		if (!$(this).hasClass('active'))
		{
			// console.log('test');
			$(this).addClass('active');
			var object_e = $(this);
			var id_wishlist = $('.delete-wishlist.active').data('id-wishlist');
			$('.st-modal-wishlist-bt-text').hide();
			$('.st-modal-wishlist-loading').css({'display':'block'});
			
			$.ajax({
				type: 'POST',
				headers: {"cache-control": "no-cache"},
				url: wishlist_url,
				async: true,
				cache: false,
				data: {
					"ajax": 1,
					"action": "delete-wishlist",
					"id_wishlist": id_wishlist,					
				},
				success: function (result)
				{
					var object_result = $.parseJSON(result);
					if (object_result.errors.length)
					{
						
						$('.st-modal-wishlist .modal-title').html(object_result.errors);
						$('.st-modal-wishlist').removeClass('enable-action').modal('show');
					}
					else
					{				
						var object_delete = $('.list-wishlist tr.active');
						$('.st-modal-wishlist').modal('hide');
						object_delete.fadeOut(function(){
							if ($(this).hasClass('show'))
							{
								$('.st-wishlist-product').fadeOut().html('');
							}
							else
							{
								//DONGND:: reload list product if a wishlist current view
								$('.list-wishlist tr.show .view-wishlist-product').trigger('click');
							}
							$(this).remove();
						})
						
					}
					$('.st-modal-wishlist-loading').hide();
					$('.st-modal-wishlist-bt-text').show();
					object_e.removeClass('active');
								
				},
				error: function (XMLHttpRequest, textStatus, errorThrown) {
					alert("TECHNICAL ERROR: \n\nDetails:\nError thrown: " + XMLHttpRequest + "\n" + 'Text status: ' + textStatus);
				}
			});
		}
	})
	
	//DONGND:: change default wishlist
	$('.default-wishlist').click(function(){
		if ($(this).is(":checked"))
		{
			// console.log('test');
			if (!$('.default-wishlist.active').length)
			{
				$(this).addClass('active');
				var object_e = $(this);
				var id_wishlist = $('.default-wishlist.active').data('id-wishlist');
				$.ajax({
					type: 'POST',
					headers: {"cache-control": "no-cache"},
					url: wishlist_url,
					async: true,
					cache: false,
					data: {
						"ajax": 1,
						"action": "default-wishlist",
						"id_wishlist": id_wishlist,					
					},
					success: function (result)
					{
						var object_result = $.parseJSON(result);
						if (object_result.errors.length)
						{
							
							$('.st-modal-wishlist .modal-title').html(object_result.errors);
							$('.st-modal-wishlist').removeClass('enable-action').modal('show');
						}
						else
						{				
							$('.default-wishlist:checked').removeAttr('checked');
							object_e.prop('checked', true);
						}
						
						object_e.removeClass('active');
									
					},
					error: function (XMLHttpRequest, textStatus, errorThrown) {
						alert("TECHNICAL ERROR: \n\nDetails:\nError thrown: " + XMLHttpRequest + "\n" + 'Text status: ' + textStatus);
					}
				});
			}
		}
		// else
		// {
			// console.log('test1');
			
		// }
		return false;
	})
	
	//DONGND:: show list product of wishlist
	$('.view-wishlist-product').click(function(){
		if (!$('.view-wishlist-product.active').length)
		{
			$(this).addClass('active');
			$(this).next('.st-view-wishlist-product-loading').show();
			$('.list-wishlist tr.show').removeClass('show');
			$(this).parents('tr').addClass('show');
			var object_e = $(this);
			var id_wishlist = $(this).data('id-wishlist');
			// $('.send-wishlist').fadeOut();
			// $('.st-wishlist-product').fadeOut(function(){
				//$('.st-wishlist-product').html('');			
				$.ajax({
					type: 'POST',
					headers: {"cache-control": "no-cache"},
					url: wishlist_url,
					async: true,
					cache: false,
					data: {
						"ajax": 1,
						"action": "show-wishlist-product",
						"id_wishlist": id_wishlist,					
					},
					success: function (result)
					{
						var object_result = $.parseJSON(result);
						if (object_result.errors.length)
						{
							
							$('.st-modal-wishlist .modal-title').html(object_result.errors);
							$('.st-modal-wishlist').removeClass('enable-action').modal('show');
						}
						else
						{				
							$('.st-wishlist-product').hide();
							$('.st-wishlist-product').html(object_result.result.html).fadeIn();
							if (object_result.result.show_send_wishlist)
							{
								$('.send-wishlist').fadeIn();
								// StWishlistButtonAction();						
								if (!$('.leo-modal-send-wishlist').length)
								{
									createStSendWishlistModalPopup();					
									StListWishlistProductModalAction();
								}
								else
								{
									$('.leo-modal-reset-send-wishlist-bt').trigger('click');
								}
								StListWishlistProductAction();
								
							}
							else
							{
								$('.send-wishlist').hide();
							}
							refeshWishlist(id_wishlist);
							
						}
						
						object_e.removeClass('active');
						object_e.next('.st-view-wishlist-product-loading').hide();
									
					},
					error: function (XMLHttpRequest, textStatus, errorThrown) {
						alert("TECHNICAL ERROR: \n\nDetails:\nError thrown: " + XMLHttpRequest + "\n" + 'Text status: ' + textStatus);
					}
				});
			// })
		}
		return false;
	})
}
function StListWishlistProductModalAction()
{
	//DONGND:: send wishlist
	$('.st-send-wishlist-button').click(function(){
		var name_wishlist = $('.list-wishlist tr.show .view-wishlist-product').data('name-wishlist');
		$('.leo-modal-send-wishlist .modal-title').html(wishlist_send_wishlist_txt+' "'+name_wishlist+'"');
		$('.leo-modal-send-wishlist').modal('show');
		
		return false;
	})
	
	$('.leo-modal-send-wishlist').submit(function(){
		// if ($(this).find('.form-group.leo-has-error').length)
		if ($('.leo-fake-send-wishlist-button').hasClass('validate-ok'))
		{
			return false;
		}
	});
	
	//DONGND:: submit send wishlist
	$('.leo-modal-send-wishlist-bt').click(function(){
		if (!$(this).hasClass('active'))
		{
			var check_submit_wishlist = true;
			var list_email = [];
			$(this).addClass('active');
			var object_e = $(this);
			$('.leo-modal-reset-send-wishlist-bt').fadeOut();
			
			$('.wishlist_email').each(function(key, val){
				if ($(this).val() !== '' && !$(this).parents('.form-group').hasClass('has-success') && !$(this).parents('.form-group').hasClass('has-warning'))
				{
					if (!validateEmail($(this).val()))
					{
						$(this).parents('.form-group').addClass('leo-has-error');
						check_submit_wishlist = false;
					}
					else
					{
						$(this).parents('.form-group').removeClass('leo-has-error');
						list_email.push(key);
					}
				}
				
			})
			// console.log(check_submit_wishlist);
			if (check_submit_wishlist)
			{
				// if (list_email.length == 0)
				// console.log(list_email.length);
				// console.log(list_email);
				if (list_email.length == 0)
				{
					$('.wishlist_email').each(function(key, val){
						if ($(this).val() == '')
						{
							$(this).parents('.form-group').addClass('leo-has-error');
							$(this).attr("required", "");
							return false;
						}
					})
					object_e.removeClass('active');
					$('.leo-modal-reset-send-wishlist-bt').fadeIn();
				}
				else
				{
					$('.leo-fake-send-wishlist-button').addClass('validate-ok');
					var id_wishlist = $('.list-wishlist tr.show .view-wishlist-product').data('id-wishlist');
					// console.log(list_email);
				
					$('.leo-modal-send-wishlist-bt-text').hide();
					$('.leo-modal-send-wishlist-loading').css({'display':'block'});
					
					$.each(list_email,function(key, val){
						var index_wishlist_email = val + 1;
						var email = $('#wishlist_email_'+index_wishlist_email).val();
						var object_parent_e = $('#wishlist_email_'+index_wishlist_email).parents('.form-group');
						object_parent_e.find('.wishlist_email_status_loading').show();
						
						$.ajax({
							type: 'POST',
							headers: {"cache-control": "no-cache"},
							url: wishlist_url,
							async: true,
							cache: false,
							data: {
								"ajax": 1,
								"action": "send-wishlist",
								"id_wishlist": id_wishlist,
								"email": email
							},
							success: function (result)
							{
								object_parent_e.find('.wishlist_email_status_loading').hide();
								var object_result = $.parseJSON(result);
								if (object_result.errors.length)
								{
									object_parent_e.addClass('has-warning').find('.send_wishlist_error').fadeIn();
								}
								else
								{				
									object_parent_e.addClass('has-success').find('.send_wishlist_success').fadeIn();
								}
																								
							},
							error: function (XMLHttpRequest, textStatus, errorThrown) {
								alert("TECHNICAL ERROR: \n\nDetails:\nError thrown: " + XMLHttpRequest + "\n" + 'Text status: ' + textStatus);
							}
						});
						
					});
					$(document).ajaxStop(function() {
						// console.log('test');
						$('.leo-modal-send-wishlist-loading').hide();
						$('.leo-modal-send-wishlist-bt-text').show();
						$('.leo-fake-send-wishlist-button').removeClass('validate-ok');
						object_e.removeClass('active');
						$('.leo-modal-reset-send-wishlist-bt').fadeIn();
					});				
					
				}
				if ($('.form-send-wishlist .form-group.leo-has-error').length)
				{
					$('.leo-fake-send-wishlist-button').trigger('click');
				}
			}
			else
			{
				object_e.removeClass('active');
				$('.leo-modal-reset-send-wishlist-bt').fadeIn();
					$('.leo-fake-send-wishlist-button').trigger('click');
			}
			
		}
	})
	
	//DONGND:: reset from send wishlist
	$('.leo-modal-reset-send-wishlist-bt').click(function(){
		$('.wishlist_email').val('').removeAttr('required');
		$('.send_wishlist_form_content .form-group').removeClass('leo-has-error has-success has-warning');
		$('.wishlist_email_status_loading').fadeOut();
		$('.send_wishlist_msg').fadeOut();
	})
}

function StListWishlistProductAction()
{
	//DONGND:: delete product of wishlist
	$('.st-wishlist-button-delete').click(function(){
		if (!$(this).hasClass('active'))
		{
			$(this).addClass('active');
			var object_e = $(this);
			var object_parent_e = object_e.parents('.st-wishlist-product');
			var id_wishlist_product = $(this).data('id-wishlist-product');
			var id_wishlist = $(this).data('id-wishlist');
			$.ajax({
				type: 'POST',
				headers: {"cache-control": "no-cache"},
				url: wishlist_url,
				async: true,
				cache: false,
				data: {
					"ajax": 1,
					"action": "delete-wishlist-product",
					"id_wishlist": id_wishlist,	
					"id_wishlist_product": id_wishlist_product,				
				},
				success: function (result)
				{
					var object_result = $.parseJSON(result);
					if (object_result.errors.length)
					{
						
						$('.st-modal-wishlist .modal-title').html(object_result.errors);
						$('.st-modal-wishlist').removeClass('enable-action').modal('show');
					}
					else
					{				
						object_e.parents('.st-wishlistproduct-item').fadeOut(function(){
							$(this).remove();
							// console.log(object_parent_e);
							// console.log(object_parent_e.find('.st-wishlistproduct-item'));
							// console.log(object_parent_e.find('.st-wishlistproduct-item').length);
							if (!object_parent_e.find('.st-wishlistproduct-item').length)
							{							
								$('.send-wishlist').hide();
								$('.list-wishlist tr.show .view-wishlist-product').trigger('click');
							}
						})
						refeshWishlist(id_wishlist);
					}
					
					object_e.removeClass('active');
					
				},
				error: function (XMLHttpRequest, textStatus, errorThrown) {
					alert("TECHNICAL ERROR: \n\nDetails:\nError thrown: " + XMLHttpRequest + "\n" + 'Text status: ' + textStatus);
				}
			});
		}
		return false;
	})
	
	//DONGND::
	$('.st-wishlist-product-save-button').click(function(){
		if (!$(this).hasClass('active'))
		{
			$(this).addClass('active');
			var object_e = $(this);
			var id_wishlist_product = $(this).data('id-wishlist-product');
			var id_wishlist = $(this).data('id-wishlist');
			// $('.st-wishlistproduct-item-'+id_wishlist_product).addClass('update');
			var quantity = $('.wishlist-product-quantity-'+id_wishlist_product).val();		
			var priority = $('.wishlist-product-priority-'+id_wishlist_product).val();		
			
			if(Math.floor(quantity) == quantity && $.isNumeric(quantity) && quantity > 0)
			{
				$('.wishlist-product-quantity-'+id_wishlist_product).parents('.form-group').removeClass('has-error');
				$.ajax({
					type: 'POST',
					headers: {"cache-control": "no-cache"},
					url: wishlist_url,
					async: true,
					cache: false,
					data: {
						"ajax": 1,
						"action": "update-wishlist-product",
						"id_wishlist": id_wishlist,	
						"id_wishlist_product": id_wishlist_product,
						"quantity": quantity,	
						"priority": priority,		
					},
					success: function (result)
					{
						var object_result = $.parseJSON(result);
						if (object_result.errors.length)
						{
							
							$('.st-modal-wishlist .modal-title').html(object_result.errors);
							$('.st-modal-wishlist').removeClass('enable-action').modal('show');
						}
						else
						{
							$('.st-wishlistproduct-item-'+id_wishlist_product).hide();
							$('.st-wishlistproduct-item-'+id_wishlist_product).fadeIn();
							refeshWishlist(id_wishlist);
						}
						
						object_e.removeClass('active');
						
					},
					error: function (XMLHttpRequest, textStatus, errorThrown) {
						alert("TECHNICAL ERROR: \n\nDetails:\nError thrown: " + XMLHttpRequest + "\n" + 'Text status: ' + textStatus);
					}
				});
			}
			else
			{
				$('.wishlist-product-quantity-'+id_wishlist_product).parents('.form-group').addClass('has-error');			
				$('.st-modal-wishlist .modal-title').html(wishlist_quantity_required);
				$('.st-modal-wishlist').removeClass('enable-action').modal('show');
				object_e.removeClass('active');
			}
		}
		return false;
	})
	
	$('.move-wishlist-item').click(function(){
		if (!$(this).hasClass('active'))
		{
			$(this).addClass('active');
			var object_e = $(this);
			var object_parent_e = object_e.parents('.st-wishlist-product');
			var id_wishlist_product = $(this).data('id-wishlist-product');
			var id_product = $(this).data('id-product');
			var id_product_attribute = $(this).data('id-product-attribute');
			var id_old_wishlist = $('.list-wishlist tr.show .view-wishlist-product').data('id-wishlist');
			var id_new_wishlist = $(this).data('id-wishlist');
			var priority = $('.wishlist-product-priority-'+id_wishlist_product).val();
			var quantity = $('.wishlist-product-quantity-'+id_wishlist_product).val();
			$.ajax({
				type: 'POST',
				headers: {"cache-control": "no-cache"},
				url: wishlist_url,
				async: true,
				cache: false,
				data: {
					"ajax": 1,
					"action": "move-wishlist-product",
					"id_new_wishlist": id_new_wishlist,	
					"id_wishlist_product": id_wishlist_product,
					"id_old_wishlist": id_old_wishlist,	
					"id_product" : id_product,
					"id_product_attribute": id_product_attribute,
					"quantity": quantity,
					"priority": priority,
				},
				success: function (result)
				{
					var object_result = $.parseJSON(result);
					if (object_result.errors.length)
					{
						
						$('.st-modal-wishlist .modal-title').html(object_result.errors);
						$('.st-modal-wishlist').removeClass('enable-action').modal('show');
					}
					else
					{
						object_e.parents('.st-wishlistproduct-item').fadeOut(function(){
							$(this).remove();
							if (!object_parent_e.find('.st-wishlistproduct-item').length)
							{							
								$('.send-wishlist').hide();
								$('.list-wishlist tr.show .view-wishlist-product').trigger('click');
							}
						});
						refeshWishlist(id_new_wishlist);
						refeshWishlist(id_old_wishlist);
					}
					
					object_e.removeClass('active');
					
				},
				error: function (XMLHttpRequest, textStatus, errorThrown) {
					alert("TECHNICAL ERROR: \n\nDetails:\nError thrown: " + XMLHttpRequest + "\n" + 'Text status: ' + textStatus);
				}
			});		
		}
		return false;
	})
}

function activeEventModalWishlist()
{
	$('.st-modal-wishlist').on('hide.bs.modal', function (e) {
		// console.log($('.leo-modal-review-bt').length);
		if ($('.st-wishlist-button.active').length)
		{
			// console.log('aaa');
			$('.st-wishlist-button.active').removeClass('active');
		}
		
		if ($('.wishlist-item.active-add').length)
		{
			// console.log('aaa');
			$('.wishlist-item.active-add').removeClass('active-add');
		}
		// $('.leo-list-wishlist').fadeOut();
		$('.default-wishlist.active').removeClass('active');
		$('.delete-wishlist.active').removeClass('active');
		
		$('.list-wishlist tr.active').removeClass('active');
		
		// $('.st-modal-wishlist').removeClass('enable-action');
	})
	
	$('.st-modal-wishlist').on('hidden.bs.modal', function (e) {
		$('body').css('padding-right', '');
	})
	$('.st-modal-wishlist').on('show.bs.modal', function (e) {
		if ($('.quickview.modal').length)
		{			
			$('.quickview.modal').modal('hide');		
		}
		
	});
}

function createStSendWishlistModalPopup()
{
	var leoSendWishlistModalPopup = '';
	leoSendWishlistModalPopup += '<div class="modal leo-modal leo-modal-send-wishlist fade" tabindex="-1" role="dialog" aria-hidden="true">';
		leoSendWishlistModalPopup += '<div class="modal-dialog" role="document">';
			leoSendWishlistModalPopup += '<div class="modal-content">';
				leoSendWishlistModalPopup += '<div class="modal-header">';
					leoSendWishlistModalPopup += '<button type="button" class="close" data-dismiss="modal" aria-label="Close">';
						leoSendWishlistModalPopup += '<span aria-hidden="true">&times;</span>';
					leoSendWishlistModalPopup += '</button>';
					leoSendWishlistModalPopup += '<h5 class="modal-title text-xs-center">';
					leoSendWishlistModalPopup += '</h5>';
				leoSendWishlistModalPopup += '</div>';
				leoSendWishlistModalPopup += '<div class="modal-body">';
					leoSendWishlistModalPopup += '<div class="send_wishlist_form_content">';
						leoSendWishlistModalPopup += '<form class="form-send-wishlist" action="#" method="post">'
							for (var $i=1; $i<= 10; $i++)
							{								
								leoSendWishlistModalPopup += '<div class="form-group row">';
								  leoSendWishlistModalPopup += '<label class="col-form-label col-sm-2 text-sm-left" for="wishlist_email_'+$i+'">'+wishlist_email_txt+' '+$i+'</label>';
									leoSendWishlistModalPopup += '<div class="wishlist_email_status col-sm-1">';
										leoSendWishlistModalPopup += '<div class="wishlist_email_status_loading cssload-speeding-wheel">';
										leoSendWishlistModalPopup += '</div>';
										leoSendWishlistModalPopup += '<i class="send_wishlist_msg send_wishlist_success material-icons">&#xE876;</i>';
										leoSendWishlistModalPopup += '<i class="send_wishlist_msg send_wishlist_error material-icons">&#xE033;</i>';									
									leoSendWishlistModalPopup += '</div>';
									leoSendWishlistModalPopup += '<div class="col-sm-9">';		
								  leoSendWishlistModalPopup += '<input class="form-control wishlist_email" id="wishlist_email_'+$i+'" name="wishlist_email_'+$i+'" type="email">';
									leoSendWishlistModalPopup += '</div>';
								leoSendWishlistModalPopup += '</div>';
							}
							leoSendWishlistModalPopup += '<button class="btn btn-primary form-control-submit leo-fake-send-wishlist-button pull-xs-right" type="submit"></button>';					  				
						leoSendWishlistModalPopup += '</form>';
					leoSendWishlistModalPopup += '</div>';
				leoSendWishlistModalPopup += '</div>';
				leoSendWishlistModalPopup += '<div class="modal-footer">';	
					leoSendWishlistModalPopup += '<button type="button" class="btn btn-primary leo-modal-reset-send-wishlist-bt">'+wishlist_reset_txt+'</button>';	
					leoSendWishlistModalPopup += '<button type="button" class="btn btn-secondary" data-dismiss="modal">'+wishlist_cancel_txt+'</button>';
					leoSendWishlistModalPopup += '<button type="button" class="leo-modal-send-wishlist-bt btn btn-primary">';						
						leoSendWishlistModalPopup += '<span class="leo-modal-send-wishlist-loading cssload-speeding-wheel"></span>';
						leoSendWishlistModalPopup += '<span class="leo-modal-send-wishlist-bt-text">';
							leoSendWishlistModalPopup += wishlist_send_txt;
						leoSendWishlistModalPopup += '</span>';
					leoSendWishlistModalPopup += '</button>';				
				leoSendWishlistModalPopup += '</div>';
			leoSendWishlistModalPopup += '</div>';
		leoSendWishlistModalPopup += '</div>';
	leoSendWishlistModalPopup += '</div>';
	$('body').append(leoSendWishlistModalPopup);
}

function validateEmail(email) {
  // var regex = /^([\w-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([\w-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$/;
  // return regex.test(email);
	var reg = /^[a-z\p{L}0-9!#$%&'*+\/=?^`{}|~_-]+[.a-z\p{L}0-9!#$%&'*+\/=?^`{}|~_-]*@[a-z\p{L}0-9]+[._a-z\p{L}0-9-]*\.[a-z\p{L}0-9]+$/i;
	return reg.test(email);
}

//DONGND:: update quantity of wishlist
function refeshWishlist(id_wishlist)
{
	$('.st-view-wishlist-product-loading-'+id_wishlist).show();
	$.ajax({
		type: 'POST',
		headers: {"cache-control": "no-cache"},
		url: wishlist_url,
		async: true,
		cache: false,
		data: {
			"ajax": 1,
			"action": "get-wishlist-info",
			"id_wishlist": id_wishlist,					
		},
		success: function (result)
		{
			var object_result = $.parseJSON(result);
			if (object_result.errors.length)
			{
				
				$('.st-modal-wishlist .modal-title').html(object_result.errors);
				$('.st-modal-wishlist').removeClass('enable-action').modal('show');
			}
			else
			{				
				$('.wishlist-numberproduct-'+id_wishlist).html(object_result.result.number_product);
			}
			$('.st-view-wishlist-product-loading-'+id_wishlist).hide();
		},
		error: function (XMLHttpRequest, textStatus, errorThrown) {
			alert("TECHNICAL ERROR: \n\nDetails:\nError thrown: " + XMLHttpRequest + "\n" + 'Text status: ' + textStatus);
		}
	});
}
