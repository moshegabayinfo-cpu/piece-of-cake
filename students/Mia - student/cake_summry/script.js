const cakes = [
    { name: "עוגת שוקולד", price: 140 },
    { name: "עוגת גבינה", price: 160 },
    { name: "עוגת לימון", price: 100 }
];

const budget = document.getElementById("budget");
const message = document.getElementById("error");
const button = document.getElementById("budget-button");
const cakeRows = document.getElementById("cake-rows");

function renderCakes(list) {
    cakeRows.innerHTML = "";

    for (const cake of list) {
        const row = document.createElement("tr");
        const nameCell = document.createElement("td");
        const priceCell = document.createElement("td");

        nameCell.textContent = cake.name;
        priceCell.textContent = cake.price;

        row.append(nameCell, priceCell);
        cakeRows.append(row);
    }
}

function getAffordableCakes() {
    const trimmedValue = budget.value.trim();
    const rawBudget = Number(trimmedValue);

    if (trimmedValue === "" || !Number.isFinite(rawBudget) || rawBudget < 0) {
    message.textContent = "התקציב אינו תקין, אנא הזינו מספר חיובי או 0";
    return;
}
let affordable = [];

    for (let i = 0; i < cakes.length; i++) {
        if (rawBudget >= cakes[i]["price"]) {
            affordable.push(cakes[i]);
        }
    }
    renderCakes(affordable);
    
       if (affordable.length === 0) {
        message.textContent = "אין עוגות בסכום הזה, נסו סכום אחר :)";
    } else {
        message.textContent = "מספר העוגות שנמצאו הוא " + affordable.length;
    }
}
renderCakes(cakes);
button.addEventListener("click", getAffordableCakes);
