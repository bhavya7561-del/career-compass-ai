// CareerCompass AI — Chat history page logic

document.addEventListener("DOMContentLoaded", async () => {
  const listEl = document.getElementById("history-list");
  const statusEl = document.getElementById("history-status");
  if (!listEl) return;

  listEl.innerHTML = `<p class="empty-state">Loading your conversation history...</p>`;

  try {
    const entries = await CCApi.getHistory();
    renderHistory(listEl, entries);
  } catch (err) {
    listEl.innerHTML = "";
    CCUi.showStatus(statusEl, CCUi.friendlyErrorMessage(err), "error");
  }
});

function renderHistory(container, entries) {
  if (!entries || entries.length === 0) {
    container.innerHTML = `<p class="empty-state">No conversations yet — head to AI Chat to ask your first question.</p>`;
    return;
  }

  container.innerHTML = entries
    .map(
      (entry) => `
      <div class="history-item">
        <div>
          <p class="history-question">${CCUi.escapeHtml(entry.question)}</p>
          <p style="font-size: var(--text-sm); color: var(--color-slate); margin: 0;">${CCUi.escapeHtml(truncate(entry.answer, 160))}</p>
        </div>
        <span class="history-time">${CCUi.escapeHtml(CCUi.formatDate(entry.created_at))}</span>
      </div>`
    )
    .join("");
}

function truncate(text, maxLength) {
  if (!text || text.length <= maxLength) return text;
  return text.slice(0, maxLength).trimEnd() + "...";
}
