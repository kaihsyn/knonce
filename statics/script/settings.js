// Generated by CoffeeScript 1.5.0
(function() {
  var KL;

  KL = typeof exports !== "undefined" && exports !== null ? exports : this;

  KL.get_notebook_list = function() {
    $('#nb-select-name').fadeOut('fast');
    $('#nb-select-spin').fadeIn();
    $('#nb-select>select').html('');
    $('#nb [name="choose_notebook"]').val('true');
    return $.get('/settings/notebook_list').done(function(data) {
      var nb, _i, _len, _ref;
      _ref = data.notebooks;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        nb = _ref[_i];
        $('#nb-select>select').append("<option value=\"" + nb.guid + "\">" + nb.name + "</option>");
      }
      return $('#nb-select>select').fadeIn();
    }).fail(function(data) {
      $('#nb-select-name').fadeIn();
      return $('#nb-select-msg').html('- Failed to load notebooks list.').fadeIn().delay(5000).fadeOut();
    }).always(function(data) {
      return $('#nb-select-spin').fadeOut();
    });
  };

  $('#menu a').click(function(e) {
    e.preventDefault();
    return $(this).tab('show');
  });

  $('.kl-tooltip').tooltip();

  $('#nb-select>.help-inline.only').on('click', 'a', function() {
    get_notebook_list();
    return false;
  });

  $('#nb').submit(function() {
    if ($('#nb [name="choose_notebook"]').val() === 'true') {
      $('#nb [name="notebook_name"]').val($("#nb-select>select>[value=\"" + ($('#nb-select>select').val()) + "\"]").html());
      $('#nb [name="notebook_guid"]').val($('#nb-select>select').val());
    }
    $('#nb-spin').fadeIn('fast');
    $('#nb-msg').fadeOut().html('');
    $.ajax({
      type: "PUT",
      url: "/settings/notebook",
      data: $(this).serialize()
    }).done(function() {
      return $('#nb-msg').html('Settings Saved!').fadeIn().delay(5000).fadeOut();
    }).fail(function() {
      return $('#nb-msg').html('Failed to save.').fadeIn();
    }).always(function() {
      return $('#nb-spin').fadeOut('fast');
    });
    return false;
  });

  $('#f-acct-bio').change(function() {
    if ($('#f-acct-bio').val().length > 500) {
      $('#f-acct-bio-limit').addClass('red');
      $('#f-acct-bio-limit').removeClass('gray');
      return $('#f-acct-btn').addClass('disabled');
    } else {
      $('#f-acct-bio-limit').addClass('gray');
      $('#f-acct-bio-limit').removeClass('red');
      return $('#f-acct-btn').removeClass('disabled');
    }
  });

  $('#form-account').submit(function() {
    if ($('#f-acct-bio').val().length > 500) {
      $('#f-acct-msg').html('Length of bio exceeds the max limit.').fadeIn().delay(3000).fadeOut();
      return false;
    }
    $('#f-acct-spin').show();
    $('#f-acct-msg').fadeOut().html('');
    $.ajax({
      type: "PUT",
      url: "/settings/account",
      data: $(this).serialize()
    }).done(function() {
      return $('#f-acct-msg').html('Settings Saved!').fadeIn().delay(5000).fadeOut();
    }).fail(function() {
      return $('#f-acct-msg').html('Failed to save.').fadeIn();
    }).always(function() {
      return $('#f-acct-spin').hide();
    });
    return false;
  });

}).call(this);
