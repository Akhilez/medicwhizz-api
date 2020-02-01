var section1 = new Vue({
    delimiters: ['[[', ']]'],
    el: '#section1',
    data: {
        message: 'Hello Vue!',
        counter: {'days': 0, 'hours': 0, 'minutes': 0, 'seconds': 0},
        countDownDate: new Date("May 1, 2020 00:00:00").getTime()
    },
    created: function () {
        this.update_counter();
    },
    methods: {
        update_counter: function () {
            var self = this;
            setInterval(function () {

                // Get today's date and time
                var now = new Date().getTime();

                // Find the distance between now and the count down date
                var distance = self.countDownDate - now;

                // Time calculations for days, hours, minutes and seconds
                self.$data.counter.days = Math.floor(distance / (1000 * 60 * 60 * 24));
                self.counter.hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                self.counter.minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                self.counter.seconds = Math.floor((distance % (1000 * 60)) / 1000);

            }, 1000);
        }
    }
});