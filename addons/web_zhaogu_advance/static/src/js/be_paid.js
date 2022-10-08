$(document).ready(function() {
    $('#return-shipment').click(function () {
      val = $(this).siblings('#order-id-btn').val()
      $('#order-id').val(val)
      $('#return-shipment-form').css('display','block')
    })
    $('#clear-btn').click(function () {
      $('#return-shipment-form').css('display','none')
    })
})