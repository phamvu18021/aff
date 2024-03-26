new DataTable('#datatable');
$(document).ready(function () {
    $("#btn_port_link").on('click', function () {
        let link = $("#port_link").val()
        let link_tracker_id = $("#link_tracker_id").val()
        let formData = {
            'link': link,
            'link_tracker_id': link_tracker_id
        };

        $.ajax({
            type: "POST",
            url: "/my/post_link",
            data: formData,
            dataType: "json",
            encode: true,
        }).done(function (data) {
            if (data.status == 200) {
                $("#port_link").val('')
                showSuccessToast({message: data.msg})
            }
            if (data.status == 400) {
                $("#port_link").val('')
                showErrorToast({message: data.msg})
            }

        });
    })
});

