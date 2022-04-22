let collapseButton = document.querySelector(".sidebar-collapse-button");
const sidebar = document.querySelector(".sidebar");
const sidetabs = document.querySelectorAll(".sidetab-content");
const tabtext = document.querySelectorAll(".sidetab-text");

collapseButton.addEventListener("click", () => {
    console.log("collapsing sidebar");
    sidebar.classList.toggle("sidebar-collapsed");
    sidetabs.forEach(tab => tab.classList.toggle("sidetab-content-collapsed"));
    tabtext.forEach(t => t.classList.toggle("sidetab-text-collapsed"));
    collapseButton.classList.toggle("sidebar-collapse-button-collapsed");
});
