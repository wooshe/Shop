(function ($) {


    $(document).ready(function () {

        setTimeout(function () {

            if ($('#id_with_size').prop('checked') == true) {
                $('#size-group .dynamic-size:not(.has_original)').remove();
                $("#size-group select :contains('Без')").attr('style', 'display: none !important');
                $('#id_size-TOTAL_FORMS').attr('value', $('#size-group .has_original').length);

            } else {
                $('#size-group .add-row').attr('style', 'display: none !important');
                $("#id_size-0-size :not(:contains('Без'))").attr('style', 'display: none !important');
                $("#id_size-0-size ").val('Без размера');
                $('#size-group .dynamic-size:not(#size-0)').remove();
                $('#id_size-TOTAL_FORMS').attr('value', 1);
            }
        }, 2000);


        $(document).on('click', '#id_with_size', function (e) {

            if ($('#id_with_size').prop('checked') == true) {
                $('#size-group .add-row').attr('style', 'display: table-row !important');
                $("#id_size-0-size :contains('Без')").attr('style', 'display: none !important');
                $("#size-group select :contains('Без')").attr('style', 'display: none !important');
                $("#id_size-0-size :not(:contains('Без'))").attr('style', 'display: block !important');
                $("#id_size-0-size ").val('L');
                $('#id_size-TOTAL_FORMS').attr('value', 1);

            } else {
                $('#size-group .add-row').attr('style', 'display: none !important');
                $("#id_size-0-size :not(:contains('Без'))").attr('style', 'display: none !important');
                $("#id_size-0-size :contains('Без')").attr('style', 'display: block !important');
                $("#id_size-0-size ").val('Без размера');
                $('#size-group .dynamic-size:not(#size-0)').remove();
                $('#id_size-TOTAL_FORMS').attr('value', 1);
            }
        });

    });


})(django.jQuery);