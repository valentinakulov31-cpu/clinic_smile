(function () {
    function initServicePageBlockDeleteButtons() {
        var group = document.querySelector("#page_blocks-group");
        if (!group) {
            return;
        }

        var forms = Array.prototype.slice.call(group.querySelectorAll(".inline-related"));
        forms.forEach(function (form) {
            if (form.classList.contains("empty-form")) {
                return;
            }

            var unsavedDeleteLink = form.querySelector("h3 .inline-deletelink");
            if (unsavedDeleteLink && unsavedDeleteLink.dataset.pageBlockDeleteReady !== "1") {
                unsavedDeleteLink.dataset.pageBlockDeleteReady = "1";
                unsavedDeleteLink.classList.add("page-block-delete-button", "page-block-unsaved-delete-button");
                unsavedDeleteLink.textContent = "Удалить блок";
                if (unsavedDeleteLink.parentElement) {
                    unsavedDeleteLink.parentElement.classList.add("page-block-unsaved-delete");
                }
            }

            if (form.dataset.pageBlockDeleteReady === "1") {
                return;
            }

            var deleteContainer = form.querySelector("h3 .delete");
            if (!deleteContainer) {
                return;
            }

            var deleteCheckbox = deleteContainer.querySelector('input[type="checkbox"][name$="-DELETE"]');
            if (!deleteCheckbox) {
                return;
            }

            form.dataset.pageBlockDeleteReady = "1";
            deleteContainer.classList.add("page-block-delete-native");

            var button = document.createElement("button");
            button.type = "button";
            button.className = "page-block-delete-button";
            button.setAttribute("aria-pressed", "false");
            deleteContainer.appendChild(button);

            function syncState() {
                var marked = deleteCheckbox.checked;
                form.classList.toggle("page-block-marked-delete", marked);
                button.classList.toggle("is-undo", marked);
                button.setAttribute("aria-pressed", marked ? "true" : "false");
                button.textContent = marked ? "Не удалять" : "Удалить блок";
            }

            button.addEventListener("click", function () {
                deleteCheckbox.checked = !deleteCheckbox.checked;
                deleteCheckbox.dispatchEvent(new Event("change", { bubbles: true }));
                syncState();
            });
            deleteCheckbox.addEventListener("change", syncState);
            syncState();
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initServicePageBlockDeleteButtons);
    } else {
        initServicePageBlockDeleteButtons();
    }

    document.addEventListener("formset:added", initServicePageBlockDeleteButtons);
})();
