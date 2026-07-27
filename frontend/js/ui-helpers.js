// CareerCompass AI — Shared UI helpers
// Small DOM utilities reused across dashboard.js, chat.js, resume.js, history.js.

const CCUi = (() => {
  function setButtonLoading(button, isLoading, loadingText = "Please wait...") {
    if (isLoading) {
      button.dataset.originalText = button.textContent;
      button.textContent = loadingText;
      button.disabled = true;
    } else {
      button.textContent = button.dataset.originalText || button.textContent;
      button.disabled = false;
    }
  }

  function showStatus(container, message, type = "error") {
    // type: "error" | "success"
    container.textContent = message;
    container.className = `status-message status-${type}`;
    container.hidden = false;
  }

  function clearStatus(container) {
    container.textContent = "";
    container.hidden = true;
  }

  // Escape user/AI text before inserting via innerHTML, to avoid HTML injection
  // and to avoid a raw XSS surface from AI-generated content.
  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text ?? "";
    return div.innerHTML;
  }

  function formatDate(isoString) {
    try {
      return new Date(isoString).toLocaleString(undefined, {
        dateStyle: "medium",
        timeStyle: "short",
      });
    } catch {
      return isoString;
    }
  }

  // Friendly wrapper for handling CCApi.ApiError consistently.
  function friendlyErrorMessage(err) {
    if (err instanceof CCApi.ApiError) {
      if (err.status === 0) return err.message;
      if (err.status === 503) return "The AI service isn't configured yet (missing OpenAI API key on the server).";
      return err.message;
    }
    return "Something unexpected went wrong. Please try again.";
  }

  return { setButtonLoading, showStatus, clearStatus, escapeHtml, formatDate, friendlyErrorMessage };
})();
