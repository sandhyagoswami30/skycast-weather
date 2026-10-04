const form = document.querySelector("#weather-form");
if (form) {
  form.addEventListener("submit", () => {
    const button = form.querySelector("button[type='submit']");
    if (button && form.reportValidity()) {
      button.disabled = true;
      button.querySelector("span:nth-child(2)").textContent = "Finding your forecast…";
    }
  });
}

// Present ISO dates in the visitor's local language and format.
document.querySelectorAll(".day-name").forEach((element) => {
  const date = new Date(`${element.textContent.trim()}T12:00:00`);
  if (!Number.isNaN(date.getTime())) {
    element.textContent = new Intl.DateTimeFormat(undefined, { weekday: "short", month: "short", day: "numeric" }).format(date);
  }
});
