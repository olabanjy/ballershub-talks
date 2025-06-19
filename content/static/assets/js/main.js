/*-------------------

Template Name: <
Author:  Pixydrops
Author URI: https://themeforest.net/user/pixydrops/portfolio
Developer: Pixydrops
Version: 1.0.0
Description: 

--------------------
CSS TABLE OF CONTENTS
--------------------

01.<-- preloader
02.<-- header
03.<-- swiper slider
04.<-- Custom text Animation
05.<-- Custom Audio Player
06.<-- Tilt Js
07.<-- magnificPopup
08.<-- Odometer
09.<-- Booststrap Customization
10.<-- nice select
11.<-- wow animation
11.<-- Aos animation
12.<-- ustom Search 


<<- The code is arranged in a very simple way, it is coded in this way to use anywhere.-->>

-------------------*/

(function ($) {
	"use strict";

	$(document).ready(function () {
		//--- Custom Header Start ---//

		$(".navbar-toggle-btn").on("click", function () {
			$(".navbar-toggle-item").slideToggle(300);
			$("body").toggleClass("overflow-hidden");
			$(this).toggleClass("open");
		});
		$(".menu-item button").on("click", function () {
			$(this).siblings("ul").slideToggle(300);
		});

		var fixed_top = $(".header-section");
		if ($(window).scrollTop() > 50) {
			fixed_top.addClass("animated fadeInDown header-fixed");
		} else {
			fixed_top.removeClass("animated fadeInDown header-fixed");
		}
		//--== Sticky Header ==--//

		//--== Window On Scroll ==--//
		$(window).on("scroll", function () {
			if ($(window).scrollTop() > 50) {
				fixed_top.addClass("animated fadeInDown header-fixed");
			} else {
				fixed_top.removeClass("animated fadeInDown header-fixed");
			}
		});
		//--- Custom Header End ---//

		//--- Custom Sidebar ---//
		$(".remove-click").on("click", function (e) {
			$(".subside-barmenu").toggleClass("active");
		});
		//--- Custom Sidebar Start ---//

		//--- Search Popup Start ---//
		const $searchWrap = $(".search-wrap");
		const $navSearch = $(".nav-search");
		const $searchClose = $("#search-close");

		$(".search-trigger").on("click", function (e) {
			e.preventDefault();
			$searchWrap.animate({ opacity: "toggle" }, 500);
			$navSearch.add($searchClose).addClass("open");
		});

		$(".search-close").on("click", function (e) {
			e.preventDefault();
			$searchWrap.animate({ opacity: "toggle" }, 500);
			$navSearch.add($searchClose).removeClass("open");
		});

		function closeSearch() {
			$searchWrap.fadeOut(200);
			$navSearch.add($searchClose).removeClass("open");
		}

		$(document.body).on("click", function (e) {
			closeSearch();
		});

		$(".search-trigger, .main-search-input").on("click", function (e) {
			e.stopPropagation();
		});
		//--- Search Popup Start ---//

		//--- Custom Tilt Js Start ---//
		const tilt = document.querySelectorAll(".tilt");
		VanillaTilt.init(tilt, {
			reverse: true,
			max: 15,
			speed: 400,
			scale: 1.01,
			glare: true,
			reset: true,
			perspective: 800,
			transition: true,
			"max-glare": 0.45,
			"glare-prerender": false,
			gyroscope: true,
			gyroscopeMinAngleX: -45,
			gyroscopeMaxAngleX: 45,
			gyroscopeMinAngleY: -45,
			gyroscopeMaxAngleY: 45,
		});
		//--- Custom Tilt Js End ---//

		//--- Custom Line Animation ---//
		for (let i = 0; i < 3; i++) {
			const clone = $("<span></span>").clone();
			clone.appendTo(".line-shape.first");
		}
		//--- Custom Line Animation ---//

		//--- Scroll Top Start ---//
		let calcScrollValue = () => {
			let scrollProgress = document.getElementById("progress");
			let progressValue = document.getElementById("valu");
			let pos = document.documentElement.scrollTop;
			let calcHeight =
				document.documentElement.scrollHeight -
				document.documentElement.clientHeight;
			let scrollValue = Math.round((pos * 250) / calcHeight);

			if (pos > 250) {
				scrollProgress.style.display = "grid";
			} else {
				scrollProgress.style.display = "none";
			}
			scrollProgress.addEventListener("click", () => {
				document.documentElement.scrollTop = 0;
			});
		};
		window.onscroll = calcScrollValue;
		window.onload = calcScrollValue;
		//--- Scroll Top End ---//

		//---  Counter Start ---//
		$(".count").counterUp({
			delay: 15,
			time: 4000,
		});
		//--- Counter  End ---//

		//--- Swiper Sponsor SLide Start ---//

		//--- Swiper Team SLide End ---//
		const sponsorWrapper = new Swiper(".sponsor-wrapper", {
			spaceBetween: 30,
			speed: 1500,
			loop: true,
			autoplay: {
				delay: 1500,
				disableOnInteraction: false,
			},
			navigation: {
				nextEl: ".cmn-prev",
				prevEl: ".cmn-next",
			},

			breakpoints: {
				1199: {
					slidesPerView: 5,
				},
				991: {
					slidesPerView: 5,
					spaceBetween: 14,
				},
				767: {
					slidesPerView: 4,
					spaceBetween: 14,
				},
				575: {
					slidesPerView: 3,
					spaceBetween: 10,
				},
				480: {
					slidesPerView: 2,
					spaceBetween: 10,
				},
				0: {
					slidesPerView: 2,
					spaceBetween: 10,
				},
			},
		});
		//--- Swiper Sponsor SLide End ---//

		//--- Swiper Episode SLide End ---//
		const latestEpisodewrap = new Swiper(".latest-episodewrap", {
			spaceBetween: 30,
			speed: 1500,
			loop: true,
			navigation: {
				nextEl: ".cust-test-next",
				prevEl: ".cust-test-prev",
			},

			breakpoints: {
				1199: {
					slidesPerView: 3,
					spaceBetween: 30,
				},
				991: {
					slidesPerView: 3,
					spaceBetween: 14,
				},
				767: {
					slidesPerView: 2,
					spaceBetween: 14,
				},
				575: {
					slidesPerView: 2,
					spaceBetween: 10,
				},
				480: {
					slidesPerView: 2,
					spaceBetween: 10,
				},
				0: {
					slidesPerView: 1,
					spaceBetween: 10,
				},
			},
		});
		//--- Swiper Episode SLide End ---//

		//--- Swiper Episode SLide End ---//
		const latestEpisodewrap02 = new Swiper(".latest-episodewrap02", {
			spaceBetween: 30,
			speed: 1500,
			loop: true,
			navigation: {
				nextEl: ".cust-test-next",
				prevEl: ".cust-test-prev",
			},

			breakpoints: {
				1199: {
					slidesPerView: 4,
				},
				991: {
					slidesPerView: 4,
					spaceBetween: 14,
				},
				767: {
					slidesPerView: 3,
					spaceBetween: 14,
				},
				575: {
					slidesPerView: 2,
					spaceBetween: 10,
				},
				480: {
					slidesPerView: 2,
					spaceBetween: 10,
				},
				0: {
					slidesPerView: 1,
					spaceBetween: 10,
				},
			},
		});
		//--- Swiper Episode SLide End ---//

		//--- Swiper Feature SLide End ---//
		const featureWrap = new Swiper(".feature-wrap", {
			spaceBetween: 30,
			speed: 1500,
			loop: true,
			pagination: {
				el: ".cmn-pagination",
				clickable: true,
			},

			breakpoints: {
				1199: {
					slidesPerView: 3,
				},
				991: {
					slidesPerView: 3,
					spaceBetween: 14,
				},
				767: {
					slidesPerView: 2,
					spaceBetween: 14,
				},
				575: {
					slidesPerView: 2,
					spaceBetween: 10,
				},
				480: {
					slidesPerView: 1,
					spaceBetween: 10,
				},
				0: {
					slidesPerView: 1,
					spaceBetween: 10,
				},
			},
		});
		//--- Swiper Feature SLide End ---//

		//--- Swiper Tesimonials SLide Start ---//
		const swiper = new Swiper(".small-sliderthumb-wrap", {
			loop: true,
			spaceBetween: 10,
			slidesPerView: 3,
			freeMode: true,
			centeredSlides: true,
			watchSlidesProgress: true,
		});
		const swiper2 = new Swiper(".middle-sliderthumb-wrap", {
			loop: true,
			spaceBetween: 10,
			navigation: {
				nextEl: ".cust-test-next",
				prevEl: ".cust-test-prev",
			},
			thumbs: {
				swiper: swiper,
			},
		});
		//--- Swiper Tesimonials SLide End ---//

		//--- Aos Animation --- //
		$(".title").attr({
			"data-aos": "zoom-in",
			"data-aos-duration": "2000",
		});

		AOS.init({
			once: true,
		});
		//--- Aos Animation --- //

		//--- magnific Popup --- //
		$(".img-popup").magnificPopup({
			type: "image",
			gallery: {
				enabled: true,
			},
		});

		$(".video-popup").magnificPopup({
			type: "iframe",
			callbacks: {},
		});
		//--- magnific Popup --- //

		//--- Nice Select --- //
		$("select").niceSelect();
		//--- Nice Select --- //

		//--- Custom Accordion Tabs --- //
		$(".accordion-single .header-area").on("click", function () {
			if ($(this).closest(".accordion-single").hasClass("active")) {
				$(this).closest(".accordion-single").removeClass("active");
				$(this).next(".content-area").slideUp();
			} else {
				$(".accordion-single").removeClass("active");
				$(this).closest(".accordion-single").addClass("active");
				$(".content-area").not($(this).next(".content-area")).slideUp();
				$(this).next(".content-area").slideToggle();
			}
		});
		//--- Custom Accordion Tabs --- //

		// Custom Tabs
		$(".tablinks .nav-links").each(function () {
			var targetTab = $(this).closest(".singletab");
			targetTab.find(".tablinks .nav-links").each(function () {
				var navBtn = targetTab.find(".tablinks .nav-links");
				navBtn.click(function () {
					navBtn.removeClass("active");
					$(this).addClass("active");
					var indexNum = $(this).closest("li").index();
					var tabcontent = targetTab.find(".tabcontents .tabitem");
					$(tabcontent).removeClass("active");
					$(tabcontent).eq(indexNum).addClass("active");
				});
			});
		});
	}); // End Document Ready Function
})(jQuery);
