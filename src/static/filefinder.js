var FILE_FINDER = false;
$(function() {
  var newForm = $("<form method='POST' action='/new/' class='newpage row' > <input type='hidden' name='name' class='name' /> </form>");
  var newFile = $("<a href='#' class='mll newfile' >Add Page</a>");
  newFile.on("click", function() {
      newForm.find("input.name").val(NEW_PAGE);
      newForm.submit();
  });

  newFile.hide();
  $("body").append(newFile);
  $("body").append(newForm);

  $(".filefind").on("change paste keyup blur focus", function() {

    var val = $(this).val();
    var lval = val.toLowerCase();

    if (val) {
      $(".pagelisting").show().removeClass("hidden");
      $(".content").hide();
    } else if (!FILE_FINDER) {
      $(".pagelisting").hide();
      $(".content").show();
    }

    $(".namespace").hide();
    var show_all = val == "";
    $("li").each(function() {
      var text = $(this).text().toLowerCase();

      if (show_all || text.indexOf(lval) != -1) {
        $(this).show();
        $(this).closest(".namespace").show();
      } else {
        $(this).hide();
      }
    });

    $(".namespace").each(function() {
      var ns = $(this);
      var text = ns.find("h2").text().toLowerCase();
      if (show_all || text.indexOf(lval) != -1) {
        ns.find("li").show();
        ns.show();
      }
    });


    NEW_PAGE = val;
    if (val) {
      newFile.show();
      var tokens = val.split("/");
      var filename, namespace;
      if (tokens.length == 1) {
        filename = tokens[0];
      } else {
        namespace = tokens.slice(0, tokens.length - 1).join("/");
        filename = tokens[tokens.length-1];

      }

      if (namespace) {
        newFile.text("Add page '" + filename + "' in namespace '" + namespace + "'");
      } else {
        newFile.text("Add page '" + filename + "'");
      }
    } else {
      newFile.text('')
    }

  });
});
