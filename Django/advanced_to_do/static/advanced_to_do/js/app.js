// FUNCTIONALITY FOR MY LIST:
$("#completed").click(function() {
    var current_display = $(".completedList").css("display");
    if (current_display == "none") {
        $(".completedList").css("display", "block");
    }
    else {
        $(".completedList").css("display", "none");
    }
})

$("#not_completed").click(function() {
    var current_display = $(".progressList").css("display");
    if (current_display == "none") {
        $(".progressList").css("display", "block");
    }
    else {
        $(".progressList").css("display", "none");
    }
})