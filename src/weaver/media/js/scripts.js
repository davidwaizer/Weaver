

$(document).ready(function(){ 
    
    $('ul.navigation li a').mouseover(function(){
        if($(this).parent().attr('class') != 'active')
            $(this).parent().addClass('hover');
    });
    
    $('ul.navigation li a').mouseout(function(){
        if($(this).parent().attr('class') != 'active')
            $(this).parent().removeClass('hover');
    });
    
    $('.servers .server').mouseover(function(){
        $(this).addClass('hover');
    });
    
    $('.servers .server').mouseout(function(){
        $(this).removeClass('hover');
    });
    
    $('.btn').mouseover(function(){
        $(this).addClass('hover');
    });
    
    $('.btn').mouseout(function(){
        $(this).removeClass('hover');
    });
    
});