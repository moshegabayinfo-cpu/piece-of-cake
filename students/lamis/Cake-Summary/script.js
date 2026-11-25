
const cakes = [
    { name: "chocolate cake", price: 140 },
    { name: "cheesecake", price: 160 },
    { name: "lemon cake", price: 100 }
];

const Button = document.getElementById("button");
const budgetInput = document.getElementById("budget");
const cakeRows = document.getElementById("cakeRows");
const message = document.getElementById("message");

function affordablecake(cakes, budget) {
    const matches = [];

    for (let i = 0; i < cakes.length; i++) {
        if (cakes[i].price <= budget) {
            matches.push(cakes[i]);
        }
    }

    return matches;
}

Button.addEventListener("click", function() {

    cakeRows.replaceChildren();

    const budget = budgetInput.valueAsNumber;

    if (!Number.isFinite(budget) || budget < 0) {
        message.textContent = "Invalid budget, please enter a valid budget!";
        return;
    }

    const matches = affordablecake(cakes, budget);

    for (const cake of matches) {
        const row = cakeRows.insertRow();
        row.insertCell().textContent = cake.name;
        row.insertCell().textContent = cake.price;
    }

    if (matches.length === 0) {
        message.textContent = "Sorry, budget too low!";
    } else {
        message.textContent = "Here are the cakes you can afford!";
    }

});
