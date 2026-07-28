// CareerCompass AI — API client
// Every network call to the FastAPI backend goes through here. Pages never
// call fetch() directly — this keeps the base URL, error handling, and
// response parsing in one place.

const CCApi = (() => {
  // Backend runs on port 8000 regardless of what port/host serves the frontend
  // (localhost in dev via docker-compose, an EC2 public IP/domain in production).
  const API_BASE = window.location.origin;

  class ApiError extends Error {
    constructor(message, status) {
      super(message);
      this.name = "ApiError";
      this.status = status;
    }
  }

  async function request(path, options = {}) {
    let response;
    try {
      response = await fetch(`${API_BASE}${path}`, {
        headers: { "Content-Type": "application/json" },
        ...options,
      });
    } catch (networkErr) {
      // fetch() itself throws on network failure (backend down, CORS, DNS, etc.)
      throw new ApiError(
        "Can't reach the CareerCompass backend. Make sure the API server is running.",
        0
      );
    }

    let data = null;
    try {
      data = await response.json();
    } catch {
      // No JSON body (e.g. plain 500) — fall through with data = null
    }

    if (!response.ok) {
      const detail = (data && data.detail) || `Request failed (${response.status})`;
      throw new ApiError(detail, response.status);
    }

    return data;
  }

  return {
    ApiError,
    getProfile: () => request("/profile"),
    saveProfile: (profile) =>
      request("/profile", { method: "POST", body: JSON.stringify(profile) }),
    sendCareerQuestion: (question) =>
      request("/career-guidance", { method: "POST", body: JSON.stringify({ question }) }),
    getHistory: () => request("/history"),
    getRoadmap: (domain) =>
      request("/roadmap", { method: "POST", body: JSON.stringify({ domain }) }),
    reviewResume: (resume_text) =>
      request("/resume-review", { method: "POST", body: JSON.stringify({ resume_text }) }),
    getSkillGap: (target_role) =>
      request("/skill-gap", { method: "POST", body: JSON.stringify({ target_role }) }),
  };
})();
