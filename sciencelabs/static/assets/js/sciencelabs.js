// File for sciencelabs shared JavaScript

$(document).ready(function(){

    $('[data-toggle="tooltip"]').tooltip();

   $(".show-tutors").click(function() {
       $(this).next().toggle();
       if($(this).text() !== 'Show')
           $(this).text('Show');
       else
           $(this).text('Hide');
    });

});