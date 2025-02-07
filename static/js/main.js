document.querySelectorAll('.form-check-label').forEach(function(label) {
    label.addEventListener('click', function() {
        var checkbox = label.previousElementSibling;
        checkbox.checked = !checkbox.checked;
    });
});
