// CareerCompass AI — Partial loader
// Injects the shared sidebar into any page with a #sidebar-slot element,
// then highlights the nav link matching the current page's data-page attribute.
// Requires being served over http(s) (fetch of a local file needs a server —
// this is already satisfied by the nginx container in docker-compose).

async function loadSidebar() {
  const slot = document.getElementById("sidebar-slot");
  if (!slot) return;

  try {
    const response = await fetch("/static/partials/sidebar.html");
    if (!response.ok) throw new Error(`Failed to load sidebar: ${response.status}`);
    slot.innerHTML = await response.text();

    const currentPage = document.body.dataset.page;
    const activeLink = slot.querySelector(`[data-page="${currentPage}"]`);
    if (activeLink) activeLink.classList.add("active");
  } catch (err) {
    console.error("CareerCompass: could not load sidebar partial.", err);
  }
}

document.addEventListener("DOMContentLoaded", loadSidebar);
