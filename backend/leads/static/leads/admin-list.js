document.addEventListener("DOMContentLoaded", () => {
  const filters = Array.from(document.querySelectorAll(".lead-filter-panel details"));

  filters.forEach((filter) => {
    filter.removeAttribute("open");
    filter.addEventListener("toggle", () => {
      if (!filter.open) return;
      filters.forEach((otherFilter) => {
        if (otherFilter !== filter) otherFilter.removeAttribute("open");
      });
    });
  });

  document.addEventListener("click", (event) => {
    if (event.target.closest(".lead-filter-panel details")) return;
    filters.forEach((filter) => filter.removeAttribute("open"));
  });
});
