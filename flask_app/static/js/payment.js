var plan_cost_id = document.getElementById('price')
var plan_cost = Number(plan_cost_id.innerText);
var plan_cost_BRL = plan_cost.toLocaleString('pt-br',{style: 'currency', currency: 'BRL'});
plan_cost_id.innerHTML = plan_cost_BRL+ '<span> / mês</span>'

// Get Stripe publishable key
document.querySelector("#btn-plano").addEventListener("click", event => {
    fetch('/config')
    .then((result) => { return result.json(); })
    .then((data) => {
        // Initialize Stripe.js
        const stripe = Stripe(data.publicKey);
        // Call your backend to create the Checkout Session
        fetch('/create-checkout-session?price_id='+data.stripe_id+'&prod_id='+data.prod_id, {
          method: 'POST',
        })
        .then(function(response) {
          return response.json();
        })
        .then(function(session) {
          //console.log(session.sessionId)
          return stripe.redirectToCheckout({ sessionId: session.sessionId });
        })
        .then(function(result) {
          // If `redirectToCheckout` fails due to a browser or network
          // error, you should display the localized error message to your
          // customer using `error.message`.
          if (result.error) {
            alert(result.error.message);
          }
      });
  });
});

 /* 
for (var j=0; j < Object.keys(prods_info).length; j++){
  var plan_cost_id = document.getElementById('price-'+j)
  var plan_cost = Number(plan_cost_id.innerText);
  var plan_cost_BRL = plan_cost.toLocaleString('pt-br',{style: 'currency', currency: 'BRL'});
  plan_cost_id.innerHTML = plan_cost_BRL+ '<span> / mês</span>'
}

// Get Stripe publishable key
fetch("/config")
.then((result) => { return result.json(); })
.then((data) => {
  // Initialize Stripe.js
  const stripe = Stripe(data.publicKey);
  for (var i=0; i < Object.keys(prods_info).length; i++){
    document.querySelector("#btn-plano-"+i).addEventListener("click", event => {
    var btn_number = parseInt($(event.target).attr('id').replace('btn-plano-', ''));
    console.log(btn_number)
    // Get Checkout Session ID
    console.log(`/create-checkout-session?price_id=${prods_info[btn_number]['stripe_id']}&prod_id=${prods_info[btn_number]['prod_id']}`)
    fetch(`/create-checkout-session?price_id=${prods_info[btn_number]['stripe_id']}&prod_id=${prods_info[btn_number]['prod_id']}`)
    .then((result) => { return result.json(); })
    .then((data) => {
      console.log(data);
      // Redirect to Stripe Checkout
      return stripe.redirectToCheckout({sessionId: data.sessionId})
    })
    .then((res) => {
      console.log(res);
    });
  });
  }
});
*/

