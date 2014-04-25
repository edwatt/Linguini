

function expand_user_content(span_elem){

	var user_id = $(span_elem).attr('user-id-target');
	var user_content_elem = $('#user-content-' + user_id);

	if(user_content_elem.is(":visible"))
	{
		$(span_elem).html('Expand');
	}
	else
	{
		$(span_elem).html('Collapse');
	}

	user_content_elem.slideToggle();
}

function expand_all(){

	$('.user-content').slideDown();
}

function collapse_all(){

	$('.user-content').slideUp();
}