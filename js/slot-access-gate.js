(function () {
  'use strict';

  function getApiOrigin() {
    var meta = document.querySelector('meta[name="bonzi-api-origin"]');
    var raw = meta && meta.content ? meta.content.trim().replace(/\/+$/, '') : '';
    return raw || 'https://bonzi-v5.onrender.com';
  }

  function escapeHtml(value) {
    return String(value || '').replace(/[&<>"']/g, function (ch) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[ch];
    });
  }

  function showLocked(reason) {
    document.body.classList.remove('access-checking');
    document.body.classList.add('access-locked');
    var panel = document.getElementById('slot-access-panel');
    if (panel) return;
    panel = document.createElement('section');
    panel.id = 'slot-access-panel';
    panel.setAttribute('role', 'status');
    panel.innerHTML = '' +
      '<div class="slot-access-card">' +
      '<div class="slot-access-label">Access</div>' +
      '<h1>Passage locked</h1>' +
      '<p>Play the slotgame first. A valid claim unlocks this page on this browser.</p>' +
      '<a class="slot-access-action" href="/?slot=open">Open the slotgame</a>' +
      (reason ? '<p class="slot-access-reason">' + escapeHtml(reason) + '</p>' : '') +
      '</div>';
    var nav = document.getElementById('mobile-menu-container') || document.body.firstChild;
    if (nav && nav.parentNode) {
      nav.parentNode.insertBefore(panel, nav.nextSibling);
    } else {
      document.body.insertBefore(panel, document.body.firstChild);
    }
  }

  function grantAccess() {
    document.body.classList.remove('access-checking', 'access-locked');
    document.body.classList.add('access-granted');
    var panel = document.getElementById('slot-access-panel');
    if (panel) panel.remove();
  }

  function verify() {
    fetch(getApiOrigin() + '/api/slotgame/verify_access', {
      method: 'GET',
      credentials: 'include',
      headers: { 'Accept': 'application/json' }
    }).then(function (response) {
      return response.json().catch(function () { return {}; });
    }).then(function (payload) {
      if (payload && payload.valid) {
        grantAccess();
      } else {
        showLocked(payload && payload.reason ? String(payload.reason) : 'not_unlocked');
      }
    }).catch(function () {
      showLocked('check_failed');
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', verify);
  } else {
    verify();
  }
})();
