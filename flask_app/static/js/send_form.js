$('#contact-form').submit(function(event){
    $('#form_sent').hide();
    $('#form_error').hide();
    $('#form_loading').show();

    event.preventDefault()  
    var formData = $('form').serializeArray()

    $.ajax({
        url: '/contact',
        type: 'POST',
        data: JSON.stringify(formData),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        success: function (data) {
            $('#form_loading').hide();
            $('#form_error').hide();
            $('#form_sent').show();
            console.log('Success on contact form submit');
        },
        error: function (event, jqxhr, settings, thrownError) {
            //console.log('event: ' + JSON.stringify(event));
            //console.log('jqxhr: ' + jqxhr);
            //console.log('settings: ' + settings);
            //console.log('thrownError: ' + thrownError);
            console.log('Error on contact form submit');
            $('#form_loading').hide();
            $('#form_error').show();
            $('#form_sent').hide();
        }
    });
});