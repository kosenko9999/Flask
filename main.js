<script type=text/javascript>
			$(function() {
			$.ajax({
			  type: 'GET'
			  url: '/api/books/1'
			  success: function(data){
			     $.each(data, function(i,item){
                   $('#orders').append('<li>my order</li>)
                });
			   }
			   });
			  });
</script>