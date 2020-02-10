let quiz_home_container = new Vue({
    delimiters: ['[[', ']]'],
    el: '#quiz_home_container',
    data: {
        my_quizzes: null,
    },
    created: function () {
        console.log("Hey, I'm gonna call the functions on startup.");
        this.update_my_quizzes(false);
    },
    methods: {
        update_my_quizzes: function (showMore) {
            let self = this;
            $.ajax({
                url: "/api_in/get_my_quizzes",
                success: function (result, status, xhr) {
                    console.log("Hey! Found some quizzes!");
                    result = JSON.parse(result);
                    self.my_quizzes = result;
                },
                error: function(xhr, status, error){
                    console.log("Opppppsssss! Error!");
                    console.log(error);
                }
            });
        },
        getDate: function(dateTime) {
            let sample = '2020-02-08 22:49:38.380821+00:00';
            return dateTime.slice(0, 10);
        },
        getDuration: function (attempt) {
            let startTime = attempt.startTime.slice(11, 18);
            let endTime = attempt.endTime.slice(11, 18);
            return `${startTime} - ${endTime} (${(attempt.elapsedTime/60.0).toFixed(2)} / ${attempt.max_duration} min)`;
        },
    }
});