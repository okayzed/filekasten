var NEW_PAGE;
var FILE_FINDER = false;

var $ = require("jquery");

module.exports = {
  initialize: function(ctx) {
    FILE_FINDER = ctx.file_finder;
    console.log("FILE FINDER IS", FILE_FINDER);

    if (this.$el.find(".newjrnl").length > 0 || this.$el.find(".newfile").length > 0) {
      return;
    }


    var fileForm = $("<form method='POST' action='/new/' class='newpage row' > <input type='hidden' name='name' class='name' /> </form>");
    var jrnlForm = $("<form method='POST' action='/journal/new/' class='newpage row' > <input type='hidden' name='name' class='name' /> </form>");
    var newFile = $("<a href='#' class='mll newfile' >Add Page</a>");
    var newJrnl = $("<a href='#' class='mll newjrnl' >Add New Journal Entry </a>");


    newFile.on("click", function() {
        fileForm.find("input.name").val(NEW_PAGE);
        fileForm.submit();
    });

    newJrnl.on("click", function() {
      jrnlForm.find("input.name").val(NEW_PAGE);
      jrnlForm.submit();
    });

    newFile.hide();
    $(".quicklinks").append(newFile);
    $(".quicklinks").append(fileForm);

    $(".quicklinks").append(newJrnl);
    $(".quicklinks").append(jrnlForm);

    this.$el.on("change paste keyup blur focus", ".filefind", function(el) {


      newJrnl = $(".newjrnl");
      newFile = $(".newfile");

      var val = $(this).val();
      var lval = val.toLowerCase();

      if (val) {
        $(".pagelisting").show().removeClass("hidden");
        $(".content").hide();
        $(".preview .content").show();
      } else if (!FILE_FINDER) {
        $(".content").show();
      }

      $(".namespace").hide();
      var show_all = val == "";
      $(".namespace li, li.result").each(function() {
        var text = $(this).text().toLowerCase();

        if (show_all || text.indexOf(lval) != -1 || !lval) {
          $(this).show();
          $(this).closest(".namespace").show();
        } else {
          $(this).hide();
        }
      });

      $(".namespace").each(function() {
        var ns = $(this);
        var text = ns.find("h2").text().toLowerCase();
        if (show_all || text.indexOf(lval) != -1 || !lval) {
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
        newFile.text('');
        newJrnl.text('Add New Journal Entry');
        newJrnl.show();
      }

      if (val[0] == '.' || val[0] == '@' || val[0] == ':') {
        newJrnl.show();
        newJrnl.text('Add journal entry to ' + val);
        newFile.hide();
      } else if (val) {
        newJrnl.hide();
      }

    });

  }
};

