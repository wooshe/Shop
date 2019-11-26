$(document).ready(function () {

    var name = '/media/default/photo_product.jpg';
    var index = 0;
    var image_address, list, loop, last_index;
    var scroll_position = 0;
    var temp = 0;
    var status = 'on';


    $('.thumbs_style img').first().css('opacity', '1');
    $('#image').html(" <img class='gallery_img_style' src='" + name + "' > ");

    loop = setInterval(slider, 3000);

    function slider() {
        last_index = $('.thumbs_style').last().index();

        if (index == last_index) {
            index = $('.thumbs_style').first().index();

        } else {
            index = index + 1;

        }

        image_address = $('.thumbs_style').eq(index).find('img').attr('src');
        list = image_address
        name = list;

        $('#image img').fadeOut(300, function () {
            $('#image').html(" <img class='gallery_img_style' src='" + name + "' > ");
            $('#image img').fadeOut(0);
            $('#image img').fadeIn(300);

        });

        $('#large_img').fadeOut(300, function () {

            $(this).attr('src', name);
            $(this).fadeIn(300);

        });

        $('.thumbs_style img').css('opacity', '0.4');
        $('.thumbs_style').eq(index).find('img').css('opacity', '1');

        if (index >= 4) {

            scroll_position = $('#thumbs').scrollLeft() + 115;

            $('#thumbs').animate({

                scrollLeft: scroll_position

            }, 500);

        }

        if (temp == 1) {

            $('#thumbs').animate({

                scrollLeft: 0

            }, 500);

            temp = 0;
        }

        if (index == last_index) {

            temp = 1;
        }

    }

    $('.thumbs_style img').click(function () {

        clearInterval(loop);

        index = $(this).parent().index();

        $('.thumbs_style img').css('opacity', '0.4');
        $(this).css('opacity', '1');

        image_address = $(this).attr('src');
        list = image_address
        name = list;

        $('#image img').fadeOut(300, function () {
            $('#image').html(" <img class='gallery_img_style' src='" + name + "' > ");
            $('#image img').fadeOut(0);
            $('#image img').fadeIn(300);

        });

        if (status == 'on') {
            loop = setInterval(slider, 3000);
        }

    });

    name = $('.gallery_img_style').attr('src');



    $('#enlarge').hide();

    $('#expand').click(function () {

        $('#enlarge').fadeIn(250);

    });

    $('#enlarge').css({

        'background': 'rgb(0,0,0)',
        'width': '100%',
        'height': '100%',
        'position': 'fixed',
        'top': '0',
        'left': '0'
    });

    $('#enlarge div').css({

        'width': '1000px',
        'height': '700px',
        'margin': '0px auto',
        'margin-top': '35px',
        'position': 'relative'

    });

    $('#large_img').css({

        'width': '1000px',
        'height': '700px'
    });

    $('#large_close').css({

        'width': '13px',
        'position': 'absolute',
        'top': '8px',
        'right': '8px'

    });

    $('#large_left').css({

        'width': '23px',
        'position': 'absolute',
        'top': '314px',
        'left': '10px'

    });

    $('#large_right').css({

        'width': '23px',
        'position': 'absolute',
        'top': '314px',
        'right': '10px'

    });

    $('#large_pause,#large_play').css({

        'width': '12px',
        'position': 'absolute',
        'top': '318px',
        'right': '40px'
    });

    $('#large_play').css({

        'display': 'none'
    });

    $('#large_close').click(function () {

        $('#enlarge').fadeOut(250, function () {

            $(this).hide();

        });
    });

    $('#pause,#large_pause').click(function () {

        status = 'off';
        $('#pause,#large_pause').fadeOut();
        $('#play,#large_play').fadeIn();
        clearInterval(loop);
    });

    $('#play,#large_play').click(function () {

        status = 'on';
        $('#play,#large_play').fadeOut();
        $('#pause,#large_pause').fadeIn();
        loop = setInterval(slider, 3000);
    });

    $(document).on('click', '#righty', function (e) {
        clearInterval(loop);

        last_index = $('.thumbs_style').last().index();

        if (index == last_index) {
            index = $('.thumbs_style').first().index();

        } else {
            index = index + 1;

        }

        image_address = $('.thumbs_style').eq(index).find('img').attr('src');
        list = image_address
        name = list;

        $('#image img').fadeOut(250, function () {
            $('#image').html(" <img class='gallery_img_style' src='" + name + "' > ");
            $('#image img').fadeOut(0);
            $('#image img').fadeIn(250);

        });

        $('#large_img').fadeOut(250, function () {

            $(this).attr('src', name);
            $(this).fadeIn(250);

        });

        $('.thumbs_style img').css('opacity', '0.4');
        $('.thumbs_style').eq(index).find('img').css('opacity', '1');

        if (status == 'on') {
            loop = setInterval(slider, 3000);
        }
    });

    $(document).on('click', '#lefty', function (e) {
        clearInterval(loop);

        if (index == $('.thumbs_style').first().index()) {
            index = $('.thumbs_style').last().index();

        } else {
            index = index - 1;

        }

        image_address = $('.thumbs_style').eq(index).find('img').attr('src');
        list = image_address
        name = list;

        $('#image img').fadeOut(300, function () {
            $('#image').html(" <img class='gallery_img_style' src='" + name + "' > ");
            $('#image img').fadeOut(0);
            $('#image img').fadeIn(300);

        });

        $('#large_img').fadeOut(250, function () {

            $(this).attr('src', name);
            $(this).fadeIn(250);

        });

        $('.thumbs_style img').css('opacity', '0.4');
        $('.thumbs_style').eq(index).find('img').css('opacity', '1');

        if (status == 'on') {
            loop = setInterval(slider, 3000);
        }
    });

});