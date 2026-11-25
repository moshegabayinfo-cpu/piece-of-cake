
const cakes = [
    { name: "Chocolate Cake", price: 10 },
    { name: "Vanilla Cake", price: 12 },
    { name: "Strawberry Cake", price: 15 }
];
 
function filterCakes(){
    const budgetInput = document.getElementById("budget");
    const budget = parseFloat(budgetInput.value);
    const errorMessage = document.getElementById("error_message");

    if (isNaN(budget) || budget < 0) {
        errorMessage.textContent = "Please enter a valid budget.";
        return;
    }
    
    errorMessage.textContent = "";
    const filteredCakes = [];

    for (const cake of cakes) {
        if (cake.price <= budget) {
            filteredCakes.push(cake);
        }
    }
    if (filteredCakes.length === 0) {
        errorMessage.textContent = "No cakes available within your budget.";
    }else {
        const table = document.querySelector('#cakeTable');
        table.innerHTML = '<tr><td>' 
        + filteredCakes.map(cake => `${cake.name}: $${cake.price.toFixed(2)}`).join('</td></tr><tr><td>') + '</td></tr>'
    }
}