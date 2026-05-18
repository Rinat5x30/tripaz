/* ─── TripAZ Chat – AJAX Polling ─────────────────────────────────────────── */

let lastMessageId = 0;
let pollInterval = null;
const POLL_MS = 3000;

function initChat(partnerId) {
  const messagesContainer = document.getElementById('chat-messages');
  const form = document.getElementById('chat-form');
  const input = document.getElementById('chat-input');

  if (!messagesContainer || !form) return;

  // Track last message for polling
  const lastMsg = messagesContainer.querySelector('.message-wrap:last-child');
  if (lastMsg) lastMessageId = parseInt(lastMsg.dataset.msgId || '0');

  // Scroll to bottom
  scrollToBottom();

  // Send message
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const content = input.value.trim();
    if (!content) return;

    input.value = '';
    input.style.height = 'auto';

    try {
      const res = await fetch(`/chat/${partnerId}/send/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCsrf(),
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `content=${encodeURIComponent(content)}`,
      });
      const data = await res.json();
      if (data.id) {
        appendMessage({ ...data, is_own: true });
        lastMessageId = data.id;
        scrollToBottom();
      }
    } catch (err) {
      console.error('Send failed', err);
    }
  });

  // Auto-resize textarea
  input.addEventListener('input', () => {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 120) + 'px';
  });

  // Enter to send (Shift+Enter for newline)
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      form.dispatchEvent(new Event('submit'));
    }
  });

  // Start polling
  pollInterval = setInterval(() => pollMessages(partnerId), POLL_MS);
}

async function pollMessages(partnerId) {
  try {
    const res = await fetch(`/chat/${partnerId}/poll/?since=${lastMessageId}`);
    const data = await res.json();

    if (data.messages?.length > 0) {
      data.messages.forEach(msg => {
        appendMessage(msg);
        lastMessageId = Math.max(lastMessageId, msg.id);
      });
      scrollToBottom();
    }
  } catch (err) {
    // Silently ignore poll errors
  }
}

function appendMessage({ id, content, created_at, is_own, sender_id }) {
  const container = document.getElementById('chat-messages');
  if (!container) return;

  const wrap = document.createElement('div');
  wrap.className = `message-wrap ${is_own ? 'own' : ''}`;
  wrap.dataset.msgId = id;

  wrap.innerHTML = `
    <div class="msg-avatar">
      ${is_own ? '👤' : '🧑'}
    </div>
    <div>
      <div class="message ${is_own ? 'own' : 'received'}">${escapeHtml(content)}</div>
      <div class="message-time">${created_at}</div>
    </div>
  `;
  container.appendChild(wrap);
}

function scrollToBottom() {
  const c = document.getElementById('chat-messages');
  if (c) c.scrollTop = c.scrollHeight;
}

function escapeHtml(str) {
  const d = document.createElement('div');
  d.appendChild(document.createTextNode(str));
  return d.innerHTML;
}

function getCsrf() {
  return document.cookie.split('; ')
    .find(c => c.startsWith('csrftoken='))
    ?.split('=')[1] || '';
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  if (pollInterval) clearInterval(pollInterval);
});
