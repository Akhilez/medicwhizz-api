let questionEditorSection = new Vue({
    delimiters: ['[[', ']]'],
    el: '#questionEditorSection',
    data: {
        counter: {'days': 0, 'hours': 0, 'minutes': 0, 'seconds': 0},
        choices: [],
    },
    created: function () {
        this.populate_choices();
    },
    methods: {
        add_choice: function () {
            let self = this;
            let choices_table = $("#choices_table");
        },
        populate_choices: function () {
            $('#choices_table tr').each(function () {
                console.log($(this));
                $(this).find('td').each(function () {
                    //do your stuff, you can use $(this) to get current cell
                })
            })

        }
    }
});