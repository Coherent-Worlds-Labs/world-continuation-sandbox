async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json();
}

function renderList(id, items, mapper) {
  const node = document.getElementById(id);
  node.innerHTML = "";
  for (const item of items) {
    const li = document.createElement("li");
    li.textContent = mapper(item);
    node.appendChild(li);
  }
}

async function loadOverview() {
  const payload = await fetchJson("/api/overview");
  document.getElementById("overview").textContent = JSON.stringify(payload.metrics, null, 2);
  renderList("branches", payload.branches, (b) => `${b.branch_id} | head=${b.head_state_id} | debt=${b.semantic_debt_est}`);
}

async function loadStates() {
  const branch = document.getElementById("branchFilter").value.trim();
  const url = branch ? `/api/states?branch_id=${encodeURIComponent(branch)}` : "/api/states";
  const states = await fetchJson(url);
  renderList("states", states, (s) => `${s.state_id} | branch=${s.branch_id} | h=${s.height}`);
}

async function loadChallenge() {
  const id = document.getElementById("challengeId").value.trim();
  const payload = await fetchJson(`/api/challenges/${encodeURIComponent(id)}`);
  document.getElementById("challenge").textContent = JSON.stringify(payload, null, 2);
}

async function loadCandidate() {
  const id = document.getElementById("candidateId").value.trim();
  const payload = await fetchJson(`/api/candidates/${encodeURIComponent(id)}`);
  document.getElementById("candidate").textContent = JSON.stringify(payload, null, 2);
}

async function runSearch() {
  const tag = document.getElementById("searchTag").value.trim();
  const rows = await fetchJson(`/api/search?tag=${encodeURIComponent(tag)}`);
  renderList("searchResults", rows, (r) => `${r.state_id} | ${r.meta_m.threads?.[0] ?? ""}`);
}

async function loadStory() {
  const branch = document.getElementById("storyBranch").value.trim() || "branch-main";
  const summary = await fetchJson(`/api/story/summary?branch_id=${encodeURIComponent(branch)}`);
  const events = await fetchJson(`/api/story?branch_id=${encodeURIComponent(branch)}&limit=200`);
  const facts = await fetchJson(`/api/facts/active?branch_id=${encodeURIComponent(branch)}&limit=200`);

  document.getElementById("storySummary").textContent = JSON.stringify(summary, null, 2);
  renderList(
    "storyTimeline",
    events,
    (e) => `h${e.height} | ${e.title} | ${e.scene} | deferred: ${e.deferred_tension}`
  );
  renderList(
    "activeFacts",
    facts,
    (f) => `h${f.introduced_height} | ${f.fact_id} | ${f.anchor_type} | ${f.subject} ${f.predicate} ${f.object} | refs: ${(f.references || []).join(", ")}`
  );
}

document.getElementById("loadStates").addEventListener("click", () => loadStates().catch(console.error));
document.getElementById("loadChallenge").addEventListener("click", () => loadChallenge().catch(console.error));
document.getElementById("loadCandidate").addEventListener("click", () => loadCandidate().catch(console.error));
document.getElementById("runSearch").addEventListener("click", () => runSearch().catch(console.error));
document.getElementById("loadStory").addEventListener("click", () => loadStory().catch(console.error));

loadOverview().catch(console.error);
loadStates().catch(console.error);
loadStory().catch(console.error);
