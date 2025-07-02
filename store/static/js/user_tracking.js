// user_tracking.js
(function () {
  let startTime = Date.now();
  let scrolled = false;
  let clicked = false;

  document.addEventListener("scroll", function () {
    scrolled = true;
  });

  document.addEventListener("click", function () {
    clicked = true;
  });

  window.addEventListener("beforeunload", function () {
    const timeSpent = Math.round((Date.now() - startTime) / 1000);
    navigator.sendBeacon("/track-behavior/", JSON.stringify({
      action: "page_exit",
      path: window.location.pathname,
      time_spent: timeSpent,
      scrolled: scrolled,
      clicked: clicked
    }));
  });
})();
