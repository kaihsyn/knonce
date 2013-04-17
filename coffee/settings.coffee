# get notebook list
get_notebook_list = ->
	$('#nb-select-name').hide()
	$('#nb-select-spin').show()
	$('#nb-select>select').html ''

	$('#nb [name="choose_notebook"]').val 'true'

	$.get('/settings/notebook/list')
		.done((data) ->
			for nb in data.notebooks
				$('#nb-select>select').append "<option value=\"#{nb.guid}\">#{nb.name}</option>"
			$('#nb-select>select').show()
		)
		.fail((data) ->
			$('#nb-select-name').show()
			$('#nb-select-msg').html('- Failed to load notebooks list.').removeClass('hide')
		)
		.always((data) ->
			$('#nb-select-spin').hide()
		)

# refresh notebook name
refreshing = false
refresh_notebook_name = ->
	if refreshing
		return

	refreshing = true
	$('#nb-select-name-refresh>i').addClass('icon-spin')

	$.get('/settings/notebook/name')
		.fail((data) ->
			if data.responseText == 'Evernote Authorization Expired'
				window.location.reload()
			else if data.responseText == 'Notebook Not Found'
				$('#nb-select-msg').html('We beleive the notebook has been deleted in your Evernote account.<br>Please send a notebook reset request to support.').removeClass('hide')
				$('#nb-select-name-refresh>i').hide()
				$('#nb-select-name>span').hide()
			else
				$('#nb-select-name-refresh>i').hide()
				$('#nb-select-msg').html(' - Failed. Please try again later.').removeClass('hide')
		)
		.done((data) ->
			$('#nb-select-name>span').html data.name
			$('#nb-select-name-refresh>i').removeClass('icon-spin')
		)
	refreshing = false

## TAB

# tab menu
$('#menu a').click (e) ->
	e.preventDefault()
	$(this).tab 'show'

## NOTEBOOK

# add tooltips
$('.kl-tooltip').tooltip()

# show notebook list
$('#nb-select-name-list').click ->
	get_notebook_list()
	return false

# refresh notebook name
$('#nb-select-name-refresh').click ->
	refresh_notebook_name()
	return false

# notebook form submit
$('#nb').submit ->
	if $('#nb [name="choose_notebook"]').val() == 'true'
		$('#nb [name="notebook_name"]').val $("#nb-select>select>[value=\"#{$('#nb-select>select').val()}\"]").html()
		$('#nb [name="notebook_guid"]').val $('#nb-select>select').val()

	$('#nb-spin').fadeIn('fast')
	$('#nb-msg').fadeOut().html('')

	$.ajax({
		type: "PUT",
		url: "/settings/notebook",
		data: $(this).serialize()
	})
	.done(->
		$('#nb-msg').html('Settings Saved!').fadeIn().delay(5000).fadeOut()
	)
	.fail(->
		$('#nb-msg').html('Failed to save.').fadeIn()
	)
	.always(->
		$('#nb-spin').fadeOut('fast')
	)

	return false

## ACCOUNT

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
		$('#f-acct-msg').html('Length of bio exceeds the max limit.').fadeIn().delay(3000).fadeOut()
		return false

	$('#f-acct-spin').show()
	$('#f-acct-msg').fadeOut().html('')

	$.ajax({
		type: "PUT",
		url: "/settings/account",
		data: $(this).serialize()
	})
	.done(->
		$('#f-acct-msg').html('Settings Saved!').fadeIn().delay(5000).fadeOut()
	)
	.fail(->
		$('#f-acct-msg').html('Failed to save.').fadeIn()
	)
	.always(->
		$('#f-acct-spin').hide()
	)

	return false
