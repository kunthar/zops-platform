// 
//	Scripts for the theme, 
// 	slideshow is used for Home Alt #3 (index3.html)
// 	services is used for Services (services.html)
// 

$(function () {
	slideshow.initialize();

	services.initialize();

	contactForm.initialize();

	animation.initialize();

  dropdownSubmenu.initialize();

  zoomerang.initialize();


	// retina display
	if(window.devicePixelRatio >= 1.2){
	    $("[data-2x]").each(function(){
	        if(this.tagName == "IMG"){
	            $(this).attr("src",$(this).attr("data-2x"));
	        } else {
	            $(this).css({"background-image":"url("+$(this).attr("data-2x")+")"});
	        }
	    });
	}
});

var zoomerang = {
  initialize: function () {
    Zoomerang.config({
      maxHeight: 730,
      maxWidth: 900
    }).listen('[data-trigger="zoomerang"]')
  }
}

var dropdownSubmenu = {
  initialize: function () {
    // prevent dropdown link click to hide dropdown
    $('.navbar-nav .dropdown-item').click(function (e) {
      e.stopPropagation()
    })

    // toggle for dropdown submenus
    $('.dropdown-submenu .dropdown-toggle').click(function (e) {
      e.preventDefault()
      $(this).parent().toggleClass('show')
      $(this).siblings('.dropdown-menu').toggleClass('show')
    })
  }
}

var animation = {
  lastScrollY: 0,
  ticking: false,
  _this: null,
  elements: null,

  initialize: function () {
    _this = this;
    _this.elements = $('[data-animate]');

    window.addEventListener('scroll', _this.onScroll, false);
    _this.update();
  },
  
  onScroll: function () {
    _this.lastScrollY = window.scrollY;
    _this.requestTick();
  },

  requestTick: function () {
    if(!_this.ticking) {
      requestAnimationFrame(_this.update);
      _this.ticking = true;
    }
  },

  update: function () {
    for (var i = _this.elements.length - 1; i >= 0; i--) {
      var $el = $(_this.elements[i])

      if ($el.hasClass($el.data("animate"))) {
        continue;
      }

      if (_this.isInViewport($el)) {
        _this.triggerAnimate($el);
      }
    }

    // allow further rAFs to be called
    _this.ticking = false;
  },

  isInViewport: function ($element) {
    var top_of_element = $element.offset().top;
    var bottom_of_element = $element.offset().top + $element.outerHeight();
    var bottom_of_screen = $(window).scrollTop() + $(window).height();
    var top_of_screen = $(window).scrollTop();

    return ((bottom_of_screen > top_of_element) && (top_of_screen < bottom_of_element));
  },

  triggerAnimate: function ($element) {
    var effect = $element.data("animate");
    var infinite = $element.data("animate-infinite") || null;
    var delay = $element.data("animate-delay") || null;
    var duration = $element.data("animate-duration") || null;
    
    if (infinite !== null) {
      $element.addClass("infinite");
    }

    if (delay !== null) {
      $element.css({
        "-webkit-animation-delay": delay + "s",
        "-moz-animation-delay": delay + "s",
        "animation-delay": delay + "s"
      })
    }

    if (duration !== null) {
      $element.css({
        "-webkit-animation-duration": duration + "s",
        "-moz-animation-duration": duration + "s",
        "animation-duration": duration + "s"
      })
    }

    $element.addClass("animated " + effect)
    .one("webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend", function () {
      $element.addClass("animated-end")
    });
  }
};

window.utils = {
	isFirefox: function () {
		return navigator.userAgent.toLowerCase().indexOf('firefox') > -1;
	}
};

var contactForm = {
	initialize: function () {
		var $contactForm = $("#contact-form");
		if (!$contactForm.length) {
			return;
		}
		
		$contactForm.validate({
			rules: {
				"name": {
					required: true
				},
				"email": {
					required: true,
					email: true
				},
				"message": {
					required: true
				}
			},
			highlight: function (element) {
				$(element).closest('.form-group').removeClass('success').addClass('error')
			},
			success: function (element) {
				element.addClass('valid').closest('.form-group').removeClass('error').addClass('success')
			}
		});
	}
}

var services = {
	screenHover: function () {
		$screens = $(".features-hover-section .images img");
		$features = $(".features-hover-section .features .feature");
		$features.mouseenter(function () {
			if (!$(this).hasClass("active")) {
				$features.removeClass("active");
				$(this).addClass("active");
				var index = $features.index(this);
				$screens.stop().fadeOut();
				$screens.eq(index).fadeIn();
			}			
		});
	},

	initialize: function () {
		this.screenHover();
	}
}

var slideshow = {
	initialize: function () {
		var $slideshow = $(".slideshow"),
			$slides = $slideshow.find(".slide"),
			$btnPrev = $slideshow.find(".btn-nav.prev"),
			$btnNext = $slideshow.find(".btn-nav.next");

		var index = 0;
		var interval = setInterval(function () {
			index++;
			if (index >= $slides.length) {
				index = 0;
			}
			updateSlides(index);
		}, 4500);

		$btnPrev.click(function () {
			clearInterval(interval);
			interval = null;
			index--;
			if (index < 0) {
				index = $slides.length - 1;
			}
			updateSlides(index);
		});

		$btnNext.click(function () {
			clearInterval(interval);
			interval = null;
			index++;
			if (index >= $slides.length) {
				index = 0;
			}
			updateSlides(index);
		});

		$slideshow.hover(function () {
			$btnPrev.addClass("active");
			$btnNext.addClass("active");
		}, function () {
			$btnPrev.removeClass("active");
			$btnNext.removeClass("active");
		});


		function updateSlides(index) {
			$slides.removeClass("active");
			$slides.eq(index).addClass("active");
		}
	}
}