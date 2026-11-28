
const cakes = [
    { name: "עוגת שוקולד", price: 140 },
    { name: "עוגת גבינה", price: 160 },
    { name: "עוגת לימון", price: 100 }
];

function filterCakes() {
    const budgetInput = document.getElementById("budget");
    const budget = parseFloat(budgetInput.value);
    const errorMessage = document.getElementById("error_message");
    const tableBody = document.querySelector("#cakeTable tbody");

    if (isNaN(budget) || budget < 0) {
        errorMessage.textContent = "נא להזין תקציב תקין.";
        return;
    }

    errorMessage.textContent = "";

    const filteredCakes = [];

    for (const cake of cakes) {
        if (cake.price <= budget) {
            filteredCakes.push(cake);
        }
    }

    tableBody.innerHTML = "";

    if (filteredCakes.length === 0) {
        errorMessage.textContent = "אין עוגות במסגרת התקציב שלך.";
    } else {
        tableBody.innerHTML = filteredCakes.map(cake => `
            <tr>
                <td>${cake.name}</td>
                <td>${cake.price} ₪</td>
            </tr>
        `).join("");
    }
}
