async function fetchProfessionals() {
    try {
        const response = await fetch('http://localhost:5000/professionals');
        const professionals = await response.json();

        const subscribedList = document.getElementById('subscribed-list');
        const unsubscribedList = document.getElementById('unsubscribed-list');
        const events = [];

        professionals.forEach(pro => {
            const li = document.createElement('li');
            li.classList.add('professional');
            li.innerHTML = `
            <strong>${pro.name}</strong><br>
            Type: ${pro.page_type}<br>
            Adresse: ${pro.address}<br>
            Email: <a href="mailto:${pro.email}">${pro.email}</a><br>
            Téléphone: ${pro.phone}<br>
            Liens: ${pro.urls.map(url => `<a href="https://${url}" target="_blank">${url}</a>`).join(', ')}
          `;

            if (pro.subscribed) {
                subscribedList.appendChild(li);
            } else {
                unsubscribedList.appendChild(li);
            }

            if (Array.isArray(pro.events)) {
                pro.events.forEach(event => {
                    events.push({
                        title: event.name,
                        start: new Date(event.date),
                        url: event.link,
                    });
                });
            }
        });

        renderCalendar(events);

    } catch (error) {
        console.error('Erreur lors de la récupération des professionnels:', error);
    }
}

function renderCalendar(events) {
    const calendarEl = document.getElementById('calendar');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'fr',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek'
        },
        events: events,
        eventClick: function (info) {
            info.jsEvent.preventDefault();
            if (info.event.url) {
                window.open(info.event.url, '_blank');
            }
        }
    });
    calendar.render();
}

fetchProfessionals();