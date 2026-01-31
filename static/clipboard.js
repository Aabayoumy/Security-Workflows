(function () {
  const template = `
    <button class="book-code-copy" type="button" aria-label="Copy">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-copy"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
    </button>`;

  function addButtons() {
    document.querySelectorAll("pre > code").forEach((code) => {
      const pre = code.parentNode;
      // Hugo wraps code in .highlight div
      const wrapper = pre.closest('.highlight') || pre;
      
      if (wrapper.querySelector(".book-code-copy")) return;

      wrapper.style.position = "relative";
      const btnContainer = document.createElement("div");
      btnContainer.innerHTML = template;
      const copyButton = btnContainer.firstChild;
      wrapper.appendChild(copyButton);
      
      copyButton.addEventListener("click", () => {
        // Remove line numbers if they exist
        let text = code.textContent;
        navigator.clipboard.writeText(text).then(() => {
          copyButton.classList.add("copied");
          setTimeout(() => copyButton.classList.remove("copied"), 2000);
        });
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", addButtons);
  } else {
    addButtons();
  }
})();
