paypal.Button.render({
    env: 'sandbox', // Or 'sandbox'
    client: {
        sandbox: 'AejadqWiITtTFQdn2pMUuEWdTPc0Gg0T0QjxPSlwjnNi9aPFhWF6EujPH72EmhU4AGWVin-FvqVIwKSR',
        production: ''
    },
    onError: function(err){
        var x = err.message
        var a = x.substring(x.indexOf('{'),x.length)
        var b = a.substring(0,a.lastIndexOf("}")+1)
        console.log(JSON.parse(b))
    },
    commit: true, // Show a 'Pay Now' button
    payment: function (data, actions) {
        try {
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
        } catch (err) {
            console.log("Payment err: "+err)
        }

    },
    onAuthorize: function (data, actions) {
        // Get the payment details
        try {
            return actions.payment.get()
                .then(function (paymentDetails) {
                    // Show a confirmation using the details from paymentDetails
                    // Then listen for a click on your confirm button
                    //document.querySelector('#confirm-button')
                    //.addEventListener('click', function () {
                    // Execute the payment
                    console.log(paymentDetails)
                    return actions.payment.execute()
                        .then(function () {
                            alert("Thank you for purchasing!");
                            // console.log(paymentDetails.id)
                            window.location.replace("/products/" + paymentDetails.id + "/after_pay")
                        });
                });
            //});
        } catch (err) {
            console.log("on authorize err: "+err)
        }

    },
    onCancel: function (data, actions) {
        alert('Payment was cancelled');
    }
}, '#paypal-button');