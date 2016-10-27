$(document).ready( function () {
    var date = new Date();

    var year = date.getFullYear();
    var month = date.getMonth() + 1;
    var day = date.getDate();

   $("#year").val(year).attr("selected", "selected");
   $("#month").val(month).attr("selected", "selected");
   $("#day").val(day).attr("selected", "selected");
});

function search() {
    var seq = $("#seq").val();

    var year = $("#year option:selected").text();
    var month = $("#month option:selected").text();
    var day = $("#day option:selected").text();

    $.ajax({
        url: "/delivered_news/search",
        type: "post",
        dataType : "json",
        data: {seq:seq, year:year, month:month, day:day},
        success: function(data) {
            $("#delivered_news_list").empty();

            var innerHTML = "";

            for(var i = 0; i<data.rows.length; i++) {
                var date = new Date(data.rows[i][3]);
                // alert(date);
                // var time = date.getFullYear() + "-" + date.getMonth() + "-" + date.getDate() + " " + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();

                innerHTML += "<tr>";
                innerHTML += "<td>" + data.rows[i][0] + "</td>";
                innerHTML += "<td>" + data.rows[i][1] + "</td>";
                innerHTML += "<td class='text-left'><a href='" + data.rows[i][4] + "' target='_blank'>" + data.rows[i][2] + "</a></td>";
                innerHTML += "<td>" + date + "</td>";
                innerHTML += "</tr>";
            }

            // $("#delivered_news_list").innerHTML = innerHTML;

            document.getElementById("delivered_news_list").innerHTML = innerHTML;
        },
        error: function(data) {
        }
    });

}