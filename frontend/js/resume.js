// CareerCompass AI — Resume review page logic

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("resume-form");
  const textarea = document.getElementById("resume-text");
  const submitBtn = document.getElementById("review-btn");
  const statusEl = document.getElementById("resume-status");
  const resultsEl = document.getElementById("resume-results");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = textarea.value.trim();
    CCUi.clearStatus(statusEl);

    // Mirrors the backend's ResumeReviewRequest(min_length=20) so the user
    // gets instant feedback instead of waiting on a round trip to fail.
    if (text.length < 20) {
      CCUi.showStatus(statusEl, "Paste a bit more of your resume (at least 20 characters).", "error");
      return;
    }

    CCUi.setButtonLoading(submitBtn, true, "Reviewing...");
    resultsEl.innerHTML = "";
    try {
      const result = await CCApi.reviewResume(text);
      renderResults(resultsEl, result);
    } catch (err) {
      CCUi.showStatus(statusEl, CCUi.friendlyErrorMessage(err), "error");
    } finally {
      CCUi.setButtonLoading(submitBtn, false);
    }
  });
});

function renderResults(container, result) {
  container.innerHTML = `
    <p style="font-size: var(--text-sm); margin-bottom: var(--space-4);">${CCUi.escapeHtml(result.summary)}</p>

    <p class="stage-label" style="font-size: var(--text-xs); font-weight: 600; color: var(--color-slate); text-transform: uppercase; letter-spacing: 0.03em; margin-bottom: var(--space-2);">Strengths</p>
    ${result.strengths
      .map((s) => `<span class="badge badge-success" style="margin-bottom: var(--space-2); display: inline-block;">${CCUi.escapeHtml(s)}</span>`)
      .join("<br>")}

    <p class="stage-label" style="font-size: var(--text-xs); font-weight: 600; color: var(--color-slate); text-transform: uppercase; letter-spacing: 0.03em; margin: var(--space-4) 0 var(--space-2);">Improvements</p>
    ${result.improvements
      .map((s) => `<span class="badge badge-warning" style="margin-bottom: var(--space-2); display: inline-block;">${CCUi.escapeHtml(s)}</span>`)
      .join("<br>")}
  `;
}
