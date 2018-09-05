module.exports = {
  initialize: function(context) {
    console.log("LOADED WIKI PAGE", context);
    this.$el.css("visibility", "inherit");

    var time = performance.timing.loadEventEnd - performance.timing.connectStart;
    this.$el.find(".perftime").text("Full page Load " + time/1000.0 + "s");
    console.log("TIMING IS", time);


  }

}
