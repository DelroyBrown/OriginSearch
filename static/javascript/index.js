// Self-invoking function
(function() {
    //http://drbl.in/ohHx
    
    var transitionEnd = 'transitionend webkitTransitionEnd oTransitionEnd MSTransitionEnd';
  
    var elements = document.querySelectorAll("#pie, #line");
  
    document.querySelector(".icon").addEventListener('click', function() {
      for (var i = 0; i < elements.length; i++) {
        (function(element) {
          if (!element.className) {
            element.className = "toggled";
            setTimeout(function() {
              element.className = "toggle-end";
              setTimeout(function() {
                element.className = "";
              }, 1000);
            }, 1700);
          }
        })(elements[i]);
      }
    });
  
  })();
  