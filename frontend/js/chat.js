// CareerCompass AI — Chat page logic

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("chat-send-btn");
  const messagesEl = document.getElementById("chat-messages");
  const statusEl = document.getElementById("chat-status");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const question = input.value.trim();
    if (!question) return;

    CCUi.clearStatus(statusEl);
    appendMessage(messagesEl, "user", question);
    input.value = "";
    scrollToBottom(messagesEl);

    const typingEl = appendTypingIndicator(messagesEl);
    CCUi.setButtonLoading(sendBtn, true, "Sending...");

    try {
      const result = await CCApi.sendCareerQuestion(question);
      typingEl.remove();
      appendMessage(messagesEl, "ai", result.answer);
    } catch (err) {
      typingEl.remove();
      CCUi.showStatus(statusEl, CCUi.friendlyErrorMessage(err), "error");
    } finally {
      CCUi.setButtonLoading(sendBtn, false);
      scrollToBottom(messagesEl);
    }
  });
});

function appendMessage(container, role, text) {
  const div = document.createElement("div");
  div.className = `msg msg-${role}`;
  // Escaped, then newlines converted to <br> — never raw-inject model output.
  div.innerHTML = CCUi.escapeHtml(text).replace(/\n/g, "<br>");
  container.appendChild(div);
  return div;
}

function appendTypingIndicator(container) {
  const div = document.createElement("div");
  div.className = "msg msg-ai";
  div.innerHTML = `<span class="spinner" style="border-color: rgba(21,26,51,0.2); border-top-color: var(--color-primary);"></span> Thinking...`;
  container.appendChild(div);
  return div;
}

function scrollToBottom(container) {
  container.scrollTop = container.scrollHeight;
}
