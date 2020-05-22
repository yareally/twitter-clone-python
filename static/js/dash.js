/*global $*/
$('#post-msg-btn').click(function() {
    "use strict";


    var message = $('#twit-msg').val();
    var userId = $('input#user_id').val();


    var request = $.ajax({
        url: 'http://' + window.location.host + '/add_message',
        type: 'GET',
        data: {user_id: userId, message: message},
        dataType: 'json',
        contentType: "application/json; charset=utf-8"
    });


    request.done(function(msg) {

        var timestamp = msg.post_time;
        var formattedTime = msg.format_time;
        var msgId = msg.msg_id;
        var msgCount = msg.msg_count;

        $('div#msg-area ul li:first').animate({

        }, function() {
            $('#tweet-count').fadeOut(function() {
                $(this).text(msgCount + "\n Twics");
            }).fadeIn();

            $(this).css('padding-top', '0px');
            $(this).parent().parent().prepend($('<ul><li>' +
                '<h4>' +
                '<a href="/dash/user_id/' + userId + '/msg_id/' + msgId + timestamp + '">' +
                formattedTime + '<\/a>' +
                '<\/h4><\/li>' +
                '<li><p>' + message + '<\/p><\/li>' +
                '<li>' +
                '<a href="#"><span class="glyphicon glyphicon-eye-open"> View<\/span><\/a>' +
                '<a href="#"> <span class="glyphicon glyphicon-share-alt"> Reply<\/span><\/a>' +
                '<a href="#"> <span class="glyphicon glyphicon-retweet"> Retwic<\/span><\/a>' +
                '<a href="#"> <span class="glyphicon glyphicon-heart"> Favorite<\/span><\/a>' +
                '<\/li><\/ul>').fadeIn(1000));
        });



        console.log("done");

    });
    request.fail(function() {

        alert('errorrrrrr');
    });
    request.always(function() {

    });
});


