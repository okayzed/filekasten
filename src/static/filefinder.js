$(function() {
  var newForm = $("<form method='POST' action='/new/' class='newpage' > <input type='hidden' name='name' class='name' /> </form>");
  var newFile = $("<a class='mll' >Create Page</a>");
  newFile.on("click", function() {
      newForm.find("input.name").val(NEW_PAGE);
      newForm.submit();
  });

  newFile.hide();
  $("body").append(newFile);
  $("body").append(newForm);

  $(".filefind").on("change paste keyup blur focus", function() {

    var val = $(this).val();
    if (FILE_FINDER) {
      $(".namespace").hide();
      var show_all = val == "";
      $("li").each(function() {
        var text = $(this).text().toLowerCase();

        if (show_all || text.indexOf(val) != -1) {
          $(this).show();
          $(this).closest(".namespace").show();
        } else {
          $(this).hide();
        }
      });
    }


    NEW_PAGE = val;
    if (val) {
      newFile.show();
      newFile.text("Create page '" + val + "'");
    }

  });
});
