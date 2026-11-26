const cakes = [
    { name: "עוגת שוקולד", price: 140 },
    { name: "עוגת גבינה", price: 160 },
    { name: "עוגת לימון", price: 100 }
];

function showCakes(filteredCakes) {
    let cakeList = "";

    for (let cake of filteredCakes) {
        cakeList += `<tr><td>${cake.name}</td><td>${cake.price}</td></tr>`;
    }

    let cakesList = document.getElementById("cakes-list");
    cakesList.innerHTML = cakeList;
}

function cakeBudget() {

    let budget = document.getElementById("budget").value;
    let errorMessage = document.getElementById("error");

    if (budget === "") {
        errorMessage.innerHTML = "נא להזין תקציב";
        return;
    }

    budget = Number(budget);

    if (!Number.isFinite(budget)) {
        errorMessage.innerHTML = "נא להזין מספר תקין";
        return;
    }

    if (budget < 0) {
        errorMessage.innerHTML = "התקציב לא יכול להיות שלילי";
        return;
    }

    let filteredCakes = cakes.filter(cake => cake.price <= budget);

    showCakes(filteredCakes);

    if (filteredCakes.length === 0) {
        errorMessage.innerHTML = "לא נמצאו עוגות בתקציב זה";
    } else {
        errorMessage.innerHTML = "";
        return;
    
    }
}


let budgetButton = document.getElementById("budget-button");
budgetButton.addEventListener("click", cakeBudget);
showCakes(cakes);
