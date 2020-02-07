let quiz_home_container = new Vue({
    delimiters: ['[[', ']]'],
    el: '#quiz_home_container',
    data: {
        my_quizzes: [],
    },
    created: function () {
        console.log("Hey, I'm gonna call the functions on startup.");
        this.update_my_quizzes(false);
    },
    methods: {
        update_my_quizzes: function (showMore) {
            $.ajax({
                url: "/api_in/get_my_quizzes",
                success: function (result, status, xhr) {
                    console.log("Hey! Found some quizzes!");
                },
                error: function(xhr, status, error){
                    console.log("Opppppsssss! Error!");
                    console.log(error);
                }
            });
        }
    }
});