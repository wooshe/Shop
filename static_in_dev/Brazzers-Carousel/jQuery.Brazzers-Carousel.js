/*!
 * jQuery Brazzers Carousel v1.0.0 (http://webdesign-master.ru)
 * Copyright 2015 WebDesign Master.
 */
!function (a) {
    a.fn.brazzersCarousel = function () {
        return this.addClass("brazzers-daddy").append("<div class='tmb-wrap'><div class='tmb-wrap-table'>").append("<div class='image-wrap'>").each(function () {
            var i = a(this);
            i.find("img").appendTo(i.find(".image-wrap")).each(function () {
                i.find(".tmb-wrap-table").append("<div>")
            })
        }).find(".tmb-wrap-table div").hover(function () {
            var i = a(this).parent(".tmb-wrap-table").closest(".brazzers-daddy").find("img"),
                d = a(this).parent(".tmb-wrap-table").find("div");
            i.hide().eq(a(this).index()).css("display", "block"), d.removeClass("active"), a(this).addClass("active")
        }).parent().find(":first").addClass("active")
    }
}(jQuery);
