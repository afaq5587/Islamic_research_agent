// ═══════════════════════════════════════════════════════════
// ISLAMIC GUIDANCE ASSISTANT — Robotic UI Enhancement JS
// ═══════════════════════════════════════════════════════════

(function() {
  'use strict';

  // ── Configuration ──────────────────────────────────────
  const CONFIG = {
    particleCount: 30,
    hexagonCount: 8,
    typingSpeed: 18,         // ms per character for typewriter feel
  };

  // ── Utility: wait for DOM element ─────────────────────
  function waitFor(selector, callback, timeout = 10000) {
    const start = Date.now();
    const interval = setInterval(() => {
      const el = document.querySelector(selector);
      if (el) {
        clearInterval(interval);
        callback(el);
      } else if (Date.now() - start > timeout) {
        clearInterval(interval);
      }
    }, 100);
  }

  // ── 1. PARTICLE FIELD ─────────────────────────────────
  function createParticleField() {
    const canvas = document.createElement('canvas');
    canvas.id = 'islamic-particle-field';
    Object.assign(canvas.style, {
      position: 'fixed',
      top: '0',
      left: '0',
      width: '100vw',
      height: '100vh',
      pointerEvents: 'none',
      zIndex: '0',
      opacity: '0.55',
    });
    document.body.appendChild(canvas);

    const ctx = canvas.getContext('2d');

    function resize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    // Particle definitions (Islamic star vertices)
    const particles = Array.from({ length: CONFIG.particleCount }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      r: Math.random() * 1.5 + 0.5,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      alpha: Math.random() * 0.6 + 0.2,
      color: Math.random() > 0.5
        ? `rgba(201,168,76,`
        : `rgba(0,180,216,`,
    }));

    let animId;
    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw connecting lines between nearby particles
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 160) {
            ctx.beginPath();
            ctx.strokeStyle = `rgba(201,168,76,${0.12 * (1 - dist / 160)})`;
            ctx.lineWidth = 0.5;
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }

      // Draw particles as star-points
      particles.forEach(p => {
        // Update position
        p.x += p.vx;
        p.y += p.vy;

        // Wrap around edges
        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;

        // Pulse alpha
        p.alpha += (Math.random() - 0.5) * 0.02;
        p.alpha = Math.max(0.1, Math.min(0.8, p.alpha));

        // Draw glow dot
        const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r * 4);
        gradient.addColorStop(0, p.color + p.alpha + ')');
        gradient.addColorStop(1, p.color + '0)');

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r * 4, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = p.color + p.alpha + ')';
        ctx.fill();
      });

      animId = requestAnimationFrame(draw);
    }

    draw();
  }

  // ── 2. FLOATING HEXAGONS ─────────────────────────────
  function createFloatingGeometry() {
    const container = document.createElement('div');
    container.id = 'islamic-geometry';
    Object.assign(container.style, {
      position: 'fixed',
      inset: '0',
      pointerEvents: 'none',
      zIndex: '0',
      overflow: 'hidden',
    });
    document.body.appendChild(container);

    const symbols = ['☪', '✦', '◈', '❖', '⬟', '✧', '◆', '★'];

    for (let i = 0; i < CONFIG.hexagonCount; i++) {
      const el = document.createElement('div');
      const size = 20 + Math.random() * 40;
      const symbol = symbols[i % symbols.length];
      const x = Math.random() * 100;
      const y = Math.random() * 100;
      const duration = 15 + Math.random() * 25;
      const delay = Math.random() * -20;
      const isGold = Math.random() > 0.4;

      Object.assign(el.style, {
        position: 'absolute',
        left: x + 'vw',
        top: y + 'vh',
        fontSize: size + 'px',
        color: isGold ? 'rgba(201,168,76,0.05)' : 'rgba(0,180,216,0.04)',
        animation: `floatGeo ${duration}s ${delay}s linear infinite`,
        userSelect: 'none',
        pointerEvents: 'none',
      });
      el.textContent = symbol;
      container.appendChild(el);
    }

    // Inject keyframes
    if (!document.getElementById('islamic-geo-style')) {
      const style = document.createElement('style');
      style.id = 'islamic-geo-style';
      style.textContent = `
        @keyframes floatGeo {
          0%   { transform: translateY(0) rotate(0deg); opacity: 0; }
          10%  { opacity: 1; }
          90%  { opacity: 1; }
          100% { transform: translateY(-100vh) rotate(360deg); opacity: 0; }
        }
      `;
      document.head.appendChild(style);
    }
  }

  // ── 3. CURSOR TRAIL ────────────────────────────────────
  function createCursorTrail() {
    const trail = [];
    const trailLength = 8;

    for (let i = 0; i < trailLength; i++) {
      const dot = document.createElement('div');
      const size = (trailLength - i) * 2;
      Object.assign(dot.style, {
        position: 'fixed',
        width: size + 'px',
        height: size + 'px',
        borderRadius: '50%',
        background: i === 0
          ? 'rgba(201,168,76,0.9)'
          : `rgba(201,168,76,${0.6 - i * 0.07})`,
        pointerEvents: 'none',
        zIndex: '9999',
        transform: 'translate(-50%, -50%)',
        transition: `all ${50 + i * 30}ms ease`,
        mixBlendMode: 'screen',
      });
      document.body.appendChild(dot);
      trail.push({ el: dot, x: 0, y: 0 });
    }

    document.addEventListener('mousemove', (e) => {
      trail[0].x = e.clientX;
      trail[0].y = e.clientY;
    });

    function updateTrail() {
      for (let i = trail.length - 1; i > 0; i--) {
        trail[i].x += (trail[i - 1].x - trail[i].x) * 0.3;
        trail[i].y += (trail[i - 1].y - trail[i].y) * 0.3;
        trail[i].el.style.left = trail[i].x + 'px';
        trail[i].el.style.top = trail[i].y + 'px';
      }
      trail[0].el.style.left = trail[0].x + 'px';
      trail[0].el.style.top = trail[0].y + 'px';
      requestAnimationFrame(updateTrail);
    }
    updateTrail();
  }

  // ── 4. MESSAGE SEND RIPPLE EFFECT ────────────────────
  function addSendRipple() {
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('button[type="submit"], [aria-label*="send" i]');
      if (!btn) return;

      const ripple = document.createElement('span');
      const rect = btn.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height) * 2;

      Object.assign(ripple.style, {
        position: 'fixed',
        left: e.clientX - size / 2 + 'px',
        top: e.clientY - size / 2 + 'px',
        width: size + 'px',
        height: size + 'px',
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(201,168,76,0.5) 0%, transparent 70%)',
        pointerEvents: 'none',
        zIndex: '9998',
        transform: 'scale(0)',
        animation: 'rippleOut 0.7s ease-out forwards',
      });
      document.body.appendChild(ripple);
      setTimeout(() => ripple.remove(), 700);
    });

    if (!document.getElementById('ripple-style')) {
      const s = document.createElement('style');
      s.id = 'ripple-style';
      s.textContent = `
        @keyframes rippleOut {
          to { transform: scale(1); opacity: 0; }
        }
      `;
      document.head.appendChild(s);
    }
  }

  // ── 5. HEADER ENHANCEMENT ─────────────────────────────
  function enhanceHeader() {
    waitFor('header', (header) => {
      // Add Islamic subtitle
      if (!document.getElementById('islamic-subtitle')) {
        const sub = document.createElement('div');
        sub.id = 'islamic-subtitle';
        Object.assign(sub.style, {
          fontSize: '0.65rem',
          letterSpacing: '0.2em',
          color: 'rgba(201,168,76,0.55)',
          fontFamily: "'Orbitron', monospace",
          textAlign: 'center',
          padding: '2px 0',
          textTransform: 'uppercase',
        });
        sub.textContent = '⬡  AI · QURAN RESEARCH · GUIDANCE  ⬡';
        header.appendChild(sub);
      }
    });
  }

  // ── 6. PAGE TITLE ──────────────────────────────────────
  function setPageMeta() {
    document.title = '☪ Islamic Guidance Assistant';

    // Favicon — crescent moon emoji via SVG
    const favicon = document.createElement('link');
    favicon.rel = 'icon';
    favicon.href = `data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>☪</text></svg>`;
    document.head.appendChild(favicon);
  }

  // ── 7. SMOOTH PAGE ENTRANCE ───────────────────────────
  function smoothEntrance() {
    const overlay = document.createElement('div');
    Object.assign(overlay.style, {
      position: 'fixed',
      inset: '0',
      background: '#030509',
      zIndex: '99999',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexDirection: 'column',
      gap: '16px',
      transition: 'opacity 0.8s ease',
    });

    // Loading symbol
    const symbol = document.createElement('div');
    Object.assign(symbol.style, {
      fontSize: '64px',
      animation: 'spinSymbol 2s linear infinite',
      color: '#c9a84c',
    });
    symbol.textContent = '☪';

    const text = document.createElement('div');
    Object.assign(text.style, {
      fontFamily: "'Orbitron', monospace",
      fontSize: '0.75rem',
      letterSpacing: '0.3em',
      color: 'rgba(201,168,76,0.7)',
    });
    text.textContent = 'INITIALIZING...';

    overlay.appendChild(symbol);
    overlay.appendChild(text);
    document.body.appendChild(overlay);

    const spinStyle = document.createElement('style');
    spinStyle.textContent = `
      @keyframes spinSymbol {
        0%   { transform: rotate(0deg) scale(1); }
        50%  { transform: rotate(180deg) scale(1.2); }
        100% { transform: rotate(360deg) scale(1); }
      }
    `;
    document.head.appendChild(spinStyle);

    // Fade out after 1.5s
    setTimeout(() => {
      overlay.style.opacity = '0';
      setTimeout(() => overlay.remove(), 800);
    }, 1500);
  }

  // ── INIT ───────────────────────────────────────────────
  function init() {
    setPageMeta();
    smoothEntrance();
    createParticleField();
    createFloatingGeometry();
    createCursorTrail();
    addSendRipple();
    enhanceHeader();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
