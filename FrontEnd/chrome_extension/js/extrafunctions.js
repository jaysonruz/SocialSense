$(document).ready(function(){
 
    $(".btn1").click(function(){
      $(".fix-error-box").slideDown();
        $( ".red" ).css('background', 'white');
    });
      $(".btn2").click(function(){
      $(".fix-error-box").slideUp();
          $( ".red" ).css('background', '#FFD9D9');
          $( ".right-icon" ).css('display', 'block');
    });
  });

  function copyToClipboard(element) {
    var $temp = $("<input>");
    $("body").append($temp);
    $temp.val($(element).text()).select();
    document.execCommand("copy");
    $temp.remove();
  }