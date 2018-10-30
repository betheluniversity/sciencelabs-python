// File for sciencelabs shared JavaScript

$(document).ready(function(){

   $(".show-tutors").click(function() {
       $(this).next().toggle();
       if($(this).text() !== 'Show')
           $(this).text('Show');
       else
           $(this).text('Hide');
    });

});