$(document).ready(function(){
    console.log('Script Loaded OK!');

    $('.imgitem').click(async function(){
        const item = $(this).text()
        console.log(item)

        $('#in_img').attr('src', '/static/' + item)

        const response = await $.ajax('/predict', {
            data: JSON.stringify(item),
            method: 'post',
            contentType: 'application/json'       
        })

        console.log(response)
        
        $('#out_img').attr('src', '/static/prediction.png')
        
    })
})



