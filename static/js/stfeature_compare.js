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
	createStCompareModalPopup();
	StCompareButtonAction();
	prestashop.on('updateProductList', function() {
		StCompareButtonAction();
	});
	
	prestashop.on('clickQuickView', function() {		
		check_active_compare = setInterval(function(){
			if($('.quickview.modal').length)
			{			
				$('.quickview.modal').on('shown.bs.modal', function (e) {
					StCompareButtonAction();
				})
				clearInterval(check_active_compare);
			}
			
		}, 300);
		
	});	

	activeEventModalCompare();
});


function createStCompareModalPopup()
{
	var leoCompareModalPopup = '';
	leoCompareModalPopup += '<div class="modal st-modal st-modal-compare fade" tabindex="-1" role="dialog" aria-hidden="true">';
		leoCompareModalPopup += '<div class="modal-dialog" role="document">';
			leoCompareModalPopup += '<div class="modal-content">';
				leoCompareModalPopup += '<div class="modal-header">';
					leoCompareModalPopup += '<button type="button" class="close" data-dismiss="modal" aria-label="Close">';
						leoCompareModalPopup += '<span aria-hidden="true">&times;</span>';
					leoCompareModalPopup += '</button>';
					leoCompareModalPopup += '<h5 class="modal-title text-xs-center">';
					leoCompareModalPopup += '</h5>';
				leoCompareModalPopup += '</div>';
			leoCompareModalPopup += '</div>';
		leoCompareModalPopup += '</div>';
	leoCompareModalPopup += '</div>';
	$('body').append(leoCompareModalPopup);
}
function StCompareButtonAction()
{
	$('.st-compare-button').click(function(){
		if (!$('.st-compare-button.active').length)
		{
			var total_product_compare = compared_products.length;
			var id_product = $(this).data('id-product');
			
			var content_product_compare_mess_remove = productcompare_remove+'. <a href="'+productcompare_url+'" target="_blank"><strong>'+productcompare_viewlistcompare+'.</strong></a>';
			var content_product_compare_mess_add = productcompare_add+'. <a href="'+productcompare_url+'" target="_blank"><strong>'+productcompare_viewlistcompare+'.</strong></a>';
			var content_product_compare_mess_max = productcompare_max_item+'. <a href="'+productcompare_url+'" target="_blank"><strong>'+productcompare_viewlistcompare+'.</strong></a>';
			
			$(this).addClass('active');
			$(this).find('.st-compare-bt-loading').css({'display':'block'});
			//$(this).find('.st-compare-bt-content').hide();
			var object_e = $(this);
			if ($(this).hasClass('added') || $(this).hasClass('delete'))
			{
				//DONGND:: remove product form list product compare
				//DONGND:: add product to list product compare
				$.ajax({
					type: 'POST',
					headers: {"cache-control": "no-cache"},
					url: productcompare_url,
					async: true,
					cache: false,
					data: {
						"ajax": 1,
						"action": "remove",
						"id_product": id_product
					},
					success: function (result)
					{
						 console.log(result);
						//Sttheme add: update number product on icon compare
						if ($('.ap-btn-compare .ap-total-compare').length)
						{
							var old_num_compare = parseInt($('.ap-btn-compare .ap-total-compare').data('compare-total'));
							var new_num_compare = old_num_compare-1;
							$('.ap-btn-compare .ap-total-compare').data('compare-total',new_num_compare);
							$('.ap-btn-compare .ap-total-compare').text(new_num_compare);
						}
												
						compared_products.splice($.inArray(parseInt(id_product), compared_products), 1);
						if (object_e.hasClass('delete'))
						{
							//DONGND:: remove from page product compare
							if ($('.leo-productscompare-item').length == 1)
							{								
								window.location.replace(productcompare_url);
							}
							else
							{
								$('td.product-'+id_product).fadeOut(function(){
									$(this).remove();
									
								});
							}
						}
						else
						{
							//DONGND:: remove from page product list
							$('.st-modal-compare .modal-title').html(content_product_compare_mess_remove);
							$('.st-modal-compare').modal('show');
							$('.st-compare-button[data-id-product='+id_product+']').removeClass('added');
							$('.st-compare-button[data-id-product='+id_product+']').attr('title',buttoncompare_title_add);
							object_e.find('.st-compare-bt-loading').hide();
							//object_e.find('.st-compare-bt-content').show();
						}
					},
					error: function (XMLHttpRequest, textStatus, errorThrown) {
						alert("TECHNICAL ERROR: \n\nDetails:\nError thrown: " + XMLHttpRequest + "\n" + 'Text status: ' + textStatus);
					}
				});
			}
			else
			{
				if (total_product_compare < comparator_max_item)
				{
					//DONGND:: add product to list product compare
					$.ajax({
						type: 'POST',
						headers: {"cache-control": "no-cache"},
						url: productcompare_url,
						async: true,
						cache: false,
						data: {
							"ajax": 1,
							"action": "add",
							"id_product": id_product
						},
						success: function (result)
						{
							// console.log(result);
							$('.st-modal-compare .modal-title').html(content_product_compare_mess_add);
							$('.st-modal-compare').modal('show');
							//Sttheme add: update number product on icon compare
							if ($('.ap-btn-compare .ap-total-compare').length)
							{								
								var old_num_compare = parseInt($('.ap-btn-compare .ap-total-compare').data('compare-total'));
								alert(old_num_compare);
								var new_num_compare = old_num_compare+1;
								$('.ap-btn-compare .ap-total-compare').data('compare-total',new_num_compare);
								$('.ap-btn-compare .ap-total-compare').text(new_num_compare);
							}
							
							compared_products.push(id_product);
							$('.st-compare-button[data-id-product='+id_product+']').addClass('added');
							$('.st-compare-button[data-id-product='+id_product+']').attr('title',buttoncompare_title_remove);
							object_e.find('.st-compare-bt-loading').hide();
							//object_e.find('.st-compare-bt-content').show();
										
						},
						error: function (XMLHttpRequest, textStatus, errorThrown) {
							alert("TECHNICAL ERROR: \n\nDetails:\nError thrown: " + XMLHttpRequest + "\n" + 'Text status: ' + textStatus);
						}
					});
					
				}
				else
				{
					//DONGND:: list product compare limited
					$('.st-modal-compare .modal-title').html(content_product_compare_mess_max);
					$('.st-modal-compare').modal('show');
					object_e.find('.st-compare-bt-loading').hide();
					//object_e.find('.st-compare-bt-content').show();
				}
			}
		}
		return false;
	})
}

function activeEventModalCompare()
{
	$('.st-modal-compare').on('hide.bs.modal', function (e) {
		// console.log($('.leo-modal-review-bt').length);
		if ($('.st-compare-button.active').length)
		{
			// console.log('aaa');
			$('.st-compare-button.active').removeClass('active');
		}
	})
	$('.st-modal-compare').on('hidden.bs.modal', function (e) {
		$('body').css('padding-right', '');
	})
	$('.st-modal-compare').on('shown.bs.modal', function (e) {
		if ($('.quickview.modal').length)
		{			
			$('.quickview.modal').modal('hide');		
		}
	});
}
