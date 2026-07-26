const regionEl = document.getElementById("region");
const minMagEl = document.getElementById("min_mag");
const windowEl = document.getElementById("window");
const sortEl = document.getElementById("sort");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");

function magClass(mag) {
    if (mag === null || mag === undefined) return "mag-low";
    if (mag < 2.5) return "mag-low";
    if (mag < 4.5) return "mag-mid";
    if (mag < 6.0) return "mag-high";
    return "mag-severe";
}

function timeAgo(isoString) {
    if (!isoString) return "Unknown time";
    const then = new Date(isoString);
    const diffMs = Date.now() - then.getTime();
    const mins = Math.floor(diffMs / 60000);
    if (mins < 60) return `${mins} min ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours} h ago`;
    const days = Math.floor(hours / 24);
    return `${days} d ago`;
}

function renderQuakes(quakes) {
    resultsEl.innerHTML = "";
    if (quakes.length === 0) {
        statusEl.textContent = "No earthquakes matched these filters. Try widening your search.";
        return;
    }
    statusEl.textContent = `${quakes.length} earthquake(s) found.`;
    for (const q of quakes) {
        const li = document.createElement("li");
        li.className = "quake-card";
        const magVal = q.magnitude !== null && q.magnitude !== undefined
            ? q.magnitude.toFixed(1) : "?";
        li.innerHTML = `
            <div class="magnitude ${magClass(q.magnitude)}">${magVal}</div>
            <div class="quake-info">
                <p class="place">${q.place}</p>
                <p class="meta">${timeAgo(q.time)} &middot; depth ${q.depth_km != null ? q.depth_km.toFixed(0) : "?"} km</p>
                <p class="note">${q.note}</p>
                <a href="${q.url}" target="_blank" rel="noopener">View on USGS &rarr;</a>
            </div>
        `;
        resultsEl.appendChild(li);
    }
}

async function loadQuakes() {
    statusEl.textContent = "Loading recent earthquakes...";
    resultsEl.innerHTML = "";
    const params = new URLSearchParams({
        region: regionEl.value,
        min_mag: minMagEl.value,
        window: windowEl.value,
        sort: sortEl.value,
    });
    try {
        const res = await fetch(`/api/quakes?${params}`);
        const data = await res.json();
        if (!res.ok) {
            statusEl.textContent = data.error || "Something went wrong.";
            return;
        }
        renderQuakes(data.quakes);
    } catch (err) {
        statusEl.textContent = "Couldn't reach the server. Check your connection and try again.";
    }
}

[regionEl, minMagEl, windowEl, sortEl].forEach((el) =>
    el.addEventListener("change", loadQuakes)
);

loadQuakes();
