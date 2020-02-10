let admin_home_container = new Vue({
    delimiters: ['[[', ']]'],
    el: '#admin_home_container',
    data: {
        dummy: "hi",
    },
    created: function () {
        console.log("hi");
    },
    methods: {
        disablePackagesEditing: function(disabled) {
            $("#packages_editor_table :input").attr("disabled", disabled);
            let disabler = $("#packageEditDisabler");
            let enabler = $("#packageEditEnabler");
            if (disabled){
                enabler.hide();
                disabler.show();
            } else {
                enabler.show();
                disabler.hide();
            }
        },
        deletePackage: function(package_id) {
            console.log("Deleting package" + package_id);
        }
    }
});