module.exports = {
  initialize: function(context) {
    console.log("LOADED WIKI PAGE", context);

    if (window.performance && performance.timing) {
      var time = performance.timing.loadEventEnd - performance.timing.connectStart;
      this.$el.find(".perftime").text("Full page Load " + time/1000.0 + "s");
      console.log("TIMING IS", time);
    }


  }

}
