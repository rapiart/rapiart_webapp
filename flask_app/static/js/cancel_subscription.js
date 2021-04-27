var plan_cost_id = document.getElementById('plan_cost')
var plan_cost = Number(plan_cost_id.innerText);
var plan_cost_BRL = plan_cost.toLocaleString('pt-br',{style: 'currency', currency: 'BRL'});
plan_cost_id.innerText = "Valor do plano: " + plan_cost_BRL