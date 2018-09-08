module.exports = {
  initialize: function() {

  },
  events: {
    "click .adddir" : "add_dir"
  },
  add_dir: function() {
    var dirEl = $("<dir class='cart mtl col-md-3 lfloat mrl pbl' />");
    dirEl.append("<label>Dir</label>");
    dirEl.append("<input autocomplete=off name='dir[]' class='formcontrol' type='text' />");
    dirEl.append("<br />");
    dirEl.append("<label>Namespace</label>");
    dirEl.append("<input autocomplete=off name='namespace[]' class='formcontrol' type='text' />");

    this.$el.find(".dirs").append(dirEl);
  }

}
