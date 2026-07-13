/* QuestLinq — minimal site JS: mobile nav + client-side date filtering
   for the "tonight" / "this weekend" event views. No dependencies. */
(function () {
  'use strict';

  // Mobile nav toggle
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Date filtering. Pages set <body data-date-filter="tonight|weekend">.
  // Event cards carry data-weekday="mon..sun" (recurring weekly events).
  var filter = document.body.getAttribute('data-date-filter');
  if (!filter) return;

  var DAYS = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
  var today = DAYS[new Date().getDay()];
  var wanted;
  if (filter === 'tonight') {
    wanted = [today];
  } else if (filter === 'weekend') {
    wanted = ['fri', 'sat', 'sun'];
  } else {
    return;
  }

  var cards = document.querySelectorAll('[data-weekday]');
  var shown = 0;
  cards.forEach(function (card) {
    if (wanted.indexOf(card.getAttribute('data-weekday')) === -1) {
      card.style.display = 'none';
    } else {
      shown++;
    }
  });

  var note = document.querySelector('[data-filter-note]');
  if (note) {
    if (filter === 'tonight') {
      var pretty = { sun: 'Sunday', mon: 'Monday', tue: 'Tuesday', wed: 'Wednesday', thu: 'Thursday', fri: 'Friday', sat: 'Saturday' }[today];
      note.textContent = 'Showing events for ' + pretty + ' night.';
    } else {
      note.textContent = 'Showing Friday, Saturday, and Sunday events.';
    }
  }

  if (shown === 0) {
    var grid = document.querySelector('.card-grid');
    if (grid) {
      var empty = document.createElement('p');
      empty.className = 'empty-state';
      empty.innerHTML = 'Nothing listed for ' + (filter === 'tonight' ? 'tonight — yet' : 'this weekend — yet') +
        '. <a href="/events/on/kingston/">Browse the full calendar</a> or check back soon.';
      grid.after(empty);
    }
  }
})();
