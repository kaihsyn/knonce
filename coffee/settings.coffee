KL = exports ? this

# get notebook list
KL.get_notebook_list = ->
	$('#nb-select-name').fadeOut('fast')
	$('#nb-select-spin').fadeIn()
	$('#nb-select>select').html ''

	$('#nb [name="choose_notebook"]').val 'true'

	$.get('/settings/notebook_list')
		.done((data) ->
			for nb in data.notebooks
				$('#nb-select>select').append "<option value=\"#{nb.guid}\">#{nb.name}</option>"
			$('#nb-select>select').fadeIn()
		)
		.fail((data) ->
			$('#nb-select-name').fadeIn()
			$('#nb-select-msg').html('- Failed to load notebooks list.').fadeIn().delay(5000).fadeOut()
		)
		.always((data) ->
			$('#nb-select-spin').fadeOut()
		)

## TAB

# tab menu
$('#menu a').click (e) ->
	e.preventDefault()
	$(this).tab 'show'

## NOTEBOOK

# add tooltips
$('.kl-tooltip').tooltip()

# show notebook list
$('#nb-select>.help-inline.only').on 'click', 'a', ->
	get_notebook_list()
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
