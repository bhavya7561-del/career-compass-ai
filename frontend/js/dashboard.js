// CareerCompass AI — Dashboard page logic
// Handles: loading + saving the student profile, generating a roadmap,
// and running a skill-gap analysis. All three talk to CCApi.

document.addEventListener("DOMContentLoaded", () => {
  initProfileForm();
  initRoadmap();
  initSkillGap();
});

// ---------------------------------------------------------------------------
// Profile
// ---------------------------------------------------------------------------

function initProfileForm() {
  const form = document.getElementById("profile-form");
  const statusEl = document.getElementById("profile-status");
  const saveBtn = document.getElementById("profile-save-btn");
  if (!form) return;

  // Prefill from the backend if a profile already exists.
  CCApi.getProfile()
    .then((profile) => {
      form.branch.value = profile.branch || "";
      form.semester.value = profile.semester || "";
      form.skills.value = (profile.skills || []).join(", ");
      form.interests.value = (profile.interests || []).join(", ");
      form.goal.value = profile.goal || "";
    })
    .catch((err) => {
      CCUi.showStatus(statusEl, CCUi.friendlyErrorMessage(err), "error");
    });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    CCUi.clearStatus(statusEl);

    const payload = {
      branch: form.branch.value || null,
      semester: form.semester.value || null,
      skills: form.skills.value.trim() || null,
      interests: form.interests.value.trim() || null,
      goal: form.goal.value.trim() || null,
    };

    CCUi.setButtonLoading(saveBtn, true, "Saving...");
    try {
      await CCApi.saveProfile(payload);
      CCUi.showStatus(statusEl, "Profile saved.", "success");
    } catch (err) {
      CCUi.showStatus(statusEl, CCUi.friendlyErrorMessage(err), "error");
    } finally {
      CCUi.setButtonLoading(saveBtn, false);
    }
  });
}

// ---------------------------------------------------------------------------
// Roadmap
// ---------------------------------------------------------------------------

function initRoadmap() {
  const btn = document.getElementById("roadmap-btn");
  const input = document.getElementById("roadmap-domain");
  const statusEl = document.getElementById("roadmap-status");
  const resultsEl = document.getElementById("roadmap-results");
  if (!btn) return;

  btn.addEventListener("click", async () => {
    const domain = input.value.trim();
    CCUi.clearStatus(statusEl);
    resultsEl.innerHTML = "";

    if (!domain) {
      CCUi.showStatus(statusEl, "Enter a target domain first (e.g. AI/ML, VLSI).", "error");
      return;
    }

    CCUi.setButtonLoading(btn, true, "Generating...");
    try {
      const roadmap = await CCApi.getRoadmap(domain);
      renderRoadmap(resultsEl, roadmap);
    } catch (err) {
      CCUi.showStatus(statusEl, CCUi.friendlyErrorMessage(err), "error");
    } finally {
      CCUi.setButtonLoading(btn, false);
    }
  });
}

function renderRoadmap(container, roadmap) {
  if (!roadmap.stages || roadmap.stages.length === 0) {
    container.innerHTML = `<p class="empty-state">No roadmap stages returned.</p>`;
    return;
  }

  container.innerHTML = roadmap.stages
    .map(
      (stage, i) => `
      <div class="roadmap-stage">
        <h4>${i + 1}. ${CCUi.escapeHtml(stage.title)} <span class="stage-duration">${CCUi.escapeHtml(stage.duration)}</span></h4>
        <p class="stage-label">Topics</p>
        <div class="tag-list">
          ${stage.topics.map((t) => `<span class="badge badge-success">${CCUi.escapeHtml(t)}</span>`).join("")}
        </div>
        <p class="stage-label">Resources</p>
        <ul class="stage-resources">
          ${stage.resources.map((r) => `<li>${CCUi.escapeHtml(r)}</li>`).join("")}
        </ul>
      </div>`
    )
    .join("");
}

// ---------------------------------------------------------------------------
// Skill Gap
// ---------------------------------------------------------------------------

function initSkillGap() {
  const btn = document.getElementById("skill-gap-btn");
  const input = document.getElementById("target-role");
  const statusEl = document.getElementById("skill-gap-status");
  const resultsEl = document.getElementById("skill-gap-results");
  if (!btn) return;

  btn.addEventListener("click", async () => {
    const targetRole = input.value.trim();
    CCUi.clearStatus(statusEl);
    resultsEl.innerHTML = "";

    if (!targetRole) {
      CCUi.showStatus(statusEl, "Enter a target role first (e.g. Data Scientist).", "error");
      return;
    }

    CCUi.setButtonLoading(btn, true, "Analyzing...");
    try {
      const result = await CCApi.getSkillGap(targetRole);
      renderSkillGap(resultsEl, result);
    } catch (err) {
      CCUi.showStatus(statusEl, CCUi.friendlyErrorMessage(err), "error");
    } finally {
      CCUi.setButtonLoading(btn, false);
    }
  });
}

function renderSkillGap(container, result) {
  container.innerHTML = `
    <p class="stage-label">Skills you already have</p>
    <div class="tag-list">
      ${
        result.known_skills.length
          ? result.known_skills.map((s) => `<span class="badge badge-success">${CCUi.escapeHtml(s)}</span>`).join("")
          : `<span class="empty-state">None identified yet.</span>`
      }
    </div>
    <p class="stage-label">Missing skills</p>
    <div class="tag-list">
      ${
        result.missing_skills.length
          ? result.missing_skills.map((s) => `<span class="badge badge-warning">${CCUi.escapeHtml(s)}</span>`).join("")
          : `<span class="empty-state">No gaps identified.</span>`
      }
    </div>
    <p class="stage-label">Recommended resources</p>
    <ul class="stage-resources">
      ${result.recommended_resources.map((r) => `<li>${CCUi.escapeHtml(r)}</li>`).join("")}
    </ul>
  `;
}
