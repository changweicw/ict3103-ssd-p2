$(document).ready(function(){
    console.log(checkoutTotal+"hi")
    paypal.Button.render({
        env: 'sandbox', // Or 'sandbox'
        client: {
            sandbox: 'AejadqWiITtTFQdn2pMUuEWdTPc0Gg0T0QjxPSlwjnNi9aPFhWF6EujPH72EmhU4AGWVin-FvqVIwKSR',
            production: ''
        },
        commit: true, // Show a 'Pay Now' button
        payment: function (data, actions) {
            
            return actions.payment.create({
                payment: {
                    transactions: [{
                        amount: {
                            total: checkoutTotal,
                            currency: 'SGD'
                        }
                    }]
                }
            });
        },
        onAuthorize: function (data, actions) {
            // Get the payment details
            return actions.payment.get()
                .then(function (paymentDetails) {
                    // Show a confirmation using the details from paymentDetails
                    // Then listen for a click on your confirm button
                    //document.querySelector('#confirm-button')
                    //.addEventListener('click', function () {
                    // Execute the payment
                    return actions.payment.execute()
                        .then(function () {
                            alert("Thank you for purchasing!");
                            // console.log(paymentDetails.id)
                            window.location.replace("/products/"+paymentDetails.id+"/after_pay")
                        });
                });
            //});
        },
        onCancel: function (data, actions) {
            alert('Payment was cancelled');
        }
    }, '#paypal-button');
})
