const API_URL = "https://ev-recommender.onrender.com";
const form = document.querySelector("#preferenceForm");
const results = document.querySelector("#results");
const template = document.querySelector("#resultTemplate");
const budget = document.querySelector("#budget");
const range = document.querySelector("#range");
const budgetValue = document.querySelector("#budgetValue");
const rangeValue = document.querySelector("#rangeValue");
const installButton = document.querySelector("#installButton");
const newsList = document.querySelector("#newsList");
const newsTemplate = document.querySelector("#newsTemplate");
const refreshNews = document.querySelector("#refreshNews");

let deferredInstallPrompt;

const updateRangeLabels = () => {
  budgetValue.value = `${Number(budget.value).toLocaleString("en-IN")} L`;
  rangeValue.value = `${Number(range.value).toLocaleString("en-IN")} km`;
};

const setNotice = (message) => {
  results.innerHTML = `<p class="notice">${message}</p>`;
};

const setNewsNotice = (message) => {
  newsList.innerHTML = "";
  const notice = document.createElement("p");
  notice.className = "notice";
  notice.textContent = message;
  newsList.appendChild(notice);
};

const getPayload = () => {
  const data = new FormData(form);
  return {
    budget_lakh: Number(data.get("budget_lakh")),
    minimum_range_km: Number(data.get("minimum_range_km")),
    daily_travel_km: Number(data.get("daily_travel_km")),
    city: data.get("city"),
    state: data.get("state"),
    use_case: data.get("use_case"),
    preferred_body_type: data.get("preferred_body_type"),
    family_size: Number(data.get("family_size")),
    home_charging_available: data.get("home_charging_available") === "on",
    fast_charging_needed: data.get("fast_charging_needed") === "on",
    brand_preference: data.get("brand_preference"),
    priority: data.get("priority"),
  };
};

const renderRecommendations = (recommendations) => {
  results.innerHTML = "";

  if (!recommendations.length) {
    setNotice("No cars matched this search. Try relaxing budget, range, or family size.");
    return;
  }

  recommendations.forEach((rec) => {
    const card = template.content.cloneNode(true);
    card.querySelector(".rank").textContent = `Recommendation #${rec.rank}`;
    card.querySelector("h2").textContent = `${rec.car_name} · ${rec.brand}`;
    card.querySelector(".match").textContent = `${rec.match_percentage}%`;
    card.querySelector(".price").textContent = `Price: Rs ${rec.price_lakh} L`;
    card.querySelector(".car-range").textContent = `Range: ${rec.claimed_range_km} km`;
    card.querySelector(".battery").textContent = `Battery: ${rec.battery_capacity_kwh} kWh`;
    card.querySelector(".reason").textContent = rec.reason;
    card.querySelector(".drawbacks").textContent = rec.drawbacks;
    results.appendChild(card);
  });
};

const formatArticleDate = (value) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
};

const renderNews = (articles) => {
  newsList.innerHTML = "";

  if (!articles.length) {
    setNewsNotice("No EV news is available right now.");
    return;
  }

  articles.forEach((article) => {
    const card = newsTemplate.content.cloneNode(true);
    const link = card.querySelector("a");
    const meta = [article.source, formatArticleDate(article.published_at)].filter(Boolean).join(" · ");

    link.href = article.url;
    card.querySelector("h3").textContent = article.title;
    card.querySelector(".news-meta").textContent = meta;
    newsList.appendChild(card);
  });
};

const loadNews = async () => {
  refreshNews.disabled = true;
  setNewsNotice("Loading EV news...");

  try {
    const response = await fetch(`${API_URL}/news`);
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const data = await response.json();
    renderNews(data.articles || []);
  } catch (error) {
    setNewsNotice(`Could not load EV news. ${error.message}`);
  } finally {
    refreshNews.disabled = false;
  }
};

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const submitButton = form.querySelector(".primary-button");
  submitButton.disabled = true;
  setNotice("Finding the best EVs for you...");

  try {
    const response = await fetch(`${API_URL}/recommend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(getPayload()),
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const data = await response.json();
    renderRecommendations(data.recommendations || []);
  } catch (error) {
    setNotice(`Could not reach the recommendation API. ${error.message}`);
  } finally {
    submitButton.disabled = false;
  }
});

[budget, range].forEach((input) => input.addEventListener("input", updateRangeLabels));
updateRangeLabels();

window.addEventListener("beforeinstallprompt", (event) => {
  event.preventDefault();
  deferredInstallPrompt = event;
  installButton.hidden = false;
});

installButton.addEventListener("click", async () => {
  if (!deferredInstallPrompt) return;
  deferredInstallPrompt.prompt();
  await deferredInstallPrompt.userChoice;
  deferredInstallPrompt = null;
  installButton.hidden = true;
});

refreshNews.addEventListener("click", loadNews);
loadNews();

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/service-worker.js");
  });
}
