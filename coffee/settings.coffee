	# add tooltips
	$('.kl-tooltip').tooltip()

	# notebook list
	$('#nb-select>.help-inline.only').on 'click', 'a', ->
		$('#nb-select-name').hide()
		$('#nb-select-spin').show()
		$('#nb-select>select').html ''

		$.get('/settings/notebook_list')
			.done((data) ->
				for nb in data.notebooks
					$('#nb-select>select').append "<option value=\"#{nb.value}\" data-name=\"#{nb.name}\">#{nb.name}</option>"
				$('#nb-select>select').show()
			)
			.fail((data) ->
				$('#nb-select-name').show()
				$('#nb-select-msg')
					.html('- Failed to load notebooks list.')
					.show()
					.delay(5000)
					.hide()
			)
			.always((data) ->
				$('#nb-select-spin').hide()
			)
		return false

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
