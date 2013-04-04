	# add tooltips
	$('.kl-tooltip').tooltip()

	# choose notebooks
	cbChoose = ->
		$.get(
			'/api/setting/notebook_list',
			{},
			(->

			),
			'json'
		)

	# tab menu
	$('#menu a').click (e) ->
		e.preventDefault()
		$(this).tab 'show'

	# bio check
	$('#f-acct-bio').change ->
		if $('#f-acct-bio').val().length > 500
			$('#f-acct-bio-limit').addClass 'red'
			$('#f-acct-bio-limit').removeClass 'gray'
			$('#f-acct-btn').addClass 'disabled'
		else
			$('#f-acct-bio-limit').addClass 'gray'
			$('#f-acct-bio-limit').removeClass 'red'
			$('#f-acct-btn').removeClass 'disabled'

	# account info update submit
	$('#form-account').submit ->
		if $('#f-acct-bio').val().length > 500
			$('#f-acct-msg').html 'Length of bio exceeds the max limit.'
			return false

		return true
