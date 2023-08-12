let isLoading = false;
let nextPage = 2; // Start from the second page, since the first is already loaded

$(window).scroll(function () {
  if (
    $(window).scrollTop() + $(window).height() >= $(document).height() - 100 &&
    !isLoading
  ) {
    isLoading = true; // Ensure we don't trigger multiple requests at once

    // Fetch the next page of results
    $.get(`?page=${nextPage}`, function (data) {
      const newResults = $(data).find(".searched-results-container").children();
      if (newResults.length > 0) {
        $(".searched-results-container").append(newResults);
        nextPage++; // Update the next page number
      }
      isLoading = false;
    });
  }
});
