

$(document).ready(function(){ 
    
    $('#nav-main ul li a').mouseover(function(){
        if($(this).parent().attr('class') != 'active')
            $(this).parent().addClass('hover');
    });
    
    $('#nav-main ul li a').mouseout(function(){
        if($(this).parent().attr('class') != 'active')
            $(this).parent().removeClass('hover');
    });
    
});