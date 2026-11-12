
document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("cakeSearch");
    const cakeCards = document.querySelectorAll(".card[data-cake-name]");
    const noResults = document.getElementById("noResults");

    searchInput.addEventListener("input", function () {
        const searchValue = searchInput.value.trim().toLowerCase();

        let foundCakes = 0;

        cakeCards.forEach(function (card) {
            const cakeName = card.dataset.cakeName.toLowerCase();

            if (cakeName.includes(searchValue)) {
                card.style.display = "";
                foundCakes++;
            } else {
                card.style.display = "none";
            }
        });

        if (foundCakes === 0) {
            noResults.style.display = "block";
        } else {
            noResults.style.display = "none";
        }
    });
});
