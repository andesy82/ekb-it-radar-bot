const eventsData = [
    {
        id: 1,
        title: "ENIGMA HACK 2026",
        date: "5–6 декабря 2026",
        location: "Хлебозавод №6, Екатеринбург",
        tags: ["Hackathon", "Python", "Web", "C#"]
    },
    {
        id: 2,
        title: "Ural Python & Backend Meetup",
        date: "14 декабря 2026",
        location: "Ельцин Центр, Екатеринбург",
        tags: ["Python", "Web"]
    },
    {
        id: 3,
        title: "ИРИТ-РТФ Winter Code Cup",
        date: "20 декабря 2026",
        location: "УрФУ, Мира 32",
        tags: ["Hackathon", "C#", "Python"]
    },
    {
        id: 4,
        title: "Frontend & UI/UX Intensive EKB",
        date: "18 января 2027",
        location: "Точка кипения, Екатеринбург",
        tags: ["Web"]
    }
];

let subscribedIds = JSON.parse(localStorage.getItem("ekb_radar_subs") || "[]");
let currentTag = "ALL";

const grid = document.getElementById("eventsGrid");
const filterButtons = document.querySelectorAll(".filter-btn");

function renderEvents() {
    const filtered = currentTag === "ALL" 
        ? eventsData 
        : eventsData.filter(ev => ev.tags.includes(currentTag));

    grid.innerHTML = filtered.map(ev => {
        const isSub = subscribedIds.includes(ev.id);
        const tagsHtml = ev.tags.map(t => `<span class="tag">#${t}</span>`).join("");
        return `
            <div class="event-card">
                <div>
                    <div class="event-date">📅 ${ev.date}</div>
                    <div class="event-title">${ev.title}</div>
                    <div class="event-loc">📍 ${ev.location}</div>
                    <div class="tags">${tagsHtml}</div>
                </div>
                <button class="btn ${isSub ? 'subscribed' : ''}" onclick="toggleSub(${ev.id})">
                    ${isSub ? '✓ Напоминание в ТГ включено' : '🔔 Напомнить в Telegram'}
                </button>
            </div>
        `;
    }).join("");
}

function toggleSub(id) {
    if (subscribedIds.includes(id)) {
        subscribedIds = subscribedIds.filter(item => item !== id);
    } else {
        subscribedIds.push(id);
    }
    localStorage.setItem("ekb_radar_subs", JSON.stringify(subscribedIds));
    renderEvents();
}

filterButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        filterButtons.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        currentTag = btn.dataset.tag;
        renderEvents();
    });
});

renderEvents();
