const cakes = [
    { name: "עוגת שוקולד", price: 140 },
    { name: "עוגת גבינה", price: 160 },
    { name: "עוגת לימון", price: 100 }
];
function budget(){
   const budget= document.getElementById("input");
   const error= document.getElementById("error");
   if (budget<0 || isNaN(budget)){
    error.textContent="enter valid budget";
    return;

   }
   const validCakes=[];
    for(const cake of cakes){
        if (budget>=cake.price)
            validCakes.push(cake);  
    }
   if(validCakes.length===0){
     error.textContent="no cakes for ur budget";

   }else {
        const table = document.querySelector('#cakeTable');
        table.innerHTML = '<tr><td>' 
        + filteredCakes.map(cake => `${cake.name}: $${cake.price.toFixed(2)}`).join('</td></tr><tr><td>') + '</td></tr>'
    }

}