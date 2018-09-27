var $ = $require("jquery");

module.exports = {
  initialize: function(ctx) {
    console.log("LOADED PAGEFINDER", this.$el);

    if (!ctx.page_finder) {
      return;
    }

    var contentEl = this.$el.find(".preview");

    var last_location;

    function refresh_crumbs() {
      $P._refs.breadcrumbs.refresh();
    }

    function load_window_content() {
      var href = window.location.hash;
      last_location = href;
      var this_href = href.slice(1);
      if (this_href.indexOf("?") == -1) { this_href += "?"; }
      $.get(this_href + "&popup=1", function(data, res) {
        contentEl.html(data);

        refresh_crumbs();

      });

    }

    $(window).on("hashchange", load_window_content);

    $(document).on("click", ".editlink", function(e) {
      e.preventDefault();
      var a = $(this).closest("a");
      var href = a.attr("href");
      $.get(href, function() {
        window.location.reload();
      });
    });

    $(document).on("click", ".postlink", function(e) {
      e.preventDefault();
      var form = $(this).closest("form");
      var params = form.serialize();
      $.post(form.attr("action"), params, function() {
        refresh_crumbs();
      });
    });

    $(document).on("click", ".wikilink, .crumb a", function(e) {
      var wikilink = $(this).closest("a");
      if (wikilink.parent(".crumb").hasClass("home")) { return; }

      var href = wikilink.attr("href")


      e.preventDefault();
      contentEl.empty();

      window.location.hash = href;
      if (last_location == window.location.hash) {
        load_window_content();
      }
    });

    load_window_content();
  }
};
