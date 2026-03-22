function loadChart(fake,real){

const ctx=document.getElementById("chart");

new Chart(ctx,{
type:'doughnut',

data:{
labels:["Fake","Real"],

datasets:[{
data:[fake,real],
backgroundColor:["#ff4d4d","#4caf50"]
}]
}

});

}