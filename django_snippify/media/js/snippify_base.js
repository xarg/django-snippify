$(document).ready(function(){
	/**
	 * Search box
	*/
	searchDefault = $("#big-search-input").val();
	if (searchDefault == '') { $("#big-search-input").addClass('default'); }
	$("#big-search-input").focus(function(event){
		if ($(this).val() == searchDefault)  {
			$(this).removeClass('default');
		}
	});

	$("#big-search-input").blur(function(event){
		if ($(this).val() == '') {
			$(this).addClass('default');
		}
	});

	$("#flash_message").delay(5000).slideUp("fast");
	$("#flash_message").click(function(event){
		$('#flash_message').slideUp("fast");
	});

	$("#show-restkey").click(function(event){
		$("#show-restkey").slideUp("fast",function() {
			$("#the-restkey").slideDown("fast");
		});
	});

	/**
	 * Snippets tweeks
	*/
	$('body').resize(function(){
		$('.source').width($('.snippet-code').width()-40);
	})

	$('.source').width($('.snippet-code').width()-40);

	externalLinks();
});

/*
function qsearch() {
	searchDefault = $("#big-search-input").val();
	$("#big-search-input").focus();
	$(this).removeClass('default');
}
*/

/**
 * Replaces rel="external" with target="_blank"
*/
function externalLinks() {
    if (!document.getElementsByTagName) return;
    var anchors = document.getElementsByTagName("a");
    for (var i=0; i<anchors.length; i++) {
        var anchor = anchors[i];
        if (anchor.getAttribute("rel") == "external") {
            anchor.target = "_blank";
            anchor.style.display = "inline";
        }
        else {
            anchor.style.display = "";
        }
    }
}
