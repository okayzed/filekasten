
module.exports = {
  refresh: function() {
    this.rpc.refresh().done(function(res, err) {
      console.log("REFRESHED BREADCRUMBS");
    });

  }
}
