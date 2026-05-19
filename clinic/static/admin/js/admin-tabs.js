(function () {
    function initAdminTabs() {
        var form = document.querySelector("#content-main form");
        if (!form) {
            return;
        }

        var panels = Array.prototype.slice.call(form.querySelectorAll("fieldset.admin-tab"));
        if (panels.length < 2) {
            return;
        }

        var nav = document.createElement("div");
        nav.className = "admin-tabs-nav";

        panels.forEach(function (panel, index) {
            panel.classList.add("admin-tab-panel");
            panel.hidden = index !== 0;

            var heading = panel.querySelector("h2");
            var title = heading ? heading.textContent.trim() : "Вкладка " + (index + 1);
            var button = document.createElement("button");
            button.type = "button";
            button.textContent = title;
            button.className = index === 0 ? "active" : "";

            button.addEventListener("click", function () {
                panels.forEach(function (item) {
                    item.hidden = item !== panel;
                });
                Array.prototype.forEach.call(nav.querySelectorAll("button"), function (item) {
                    item.classList.toggle("active", item === button);
                });
            });

            nav.appendChild(button);
        });

        panels[0].parentNode.insertBefore(nav, panels[0]);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initAdminTabs);
    } else {
        initAdminTabs();
    }
})();
