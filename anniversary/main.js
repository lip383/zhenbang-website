// ===== 导航切换 =====
function toggleNav() {
  const links = document.querySelector('.nav-links');
  links.classList.toggle('open');
}

// ===== 倒计时（庆典日期：2026年6月16日，成立20周年纪念日）=====
function updateCountdown() {
  const target = new Date('2026-06-16T10:00:00');
  const now = new Date();
  const diff = target - now;
  if (diff <= 0) {
    document.getElementById('days') && (document.getElementById('days').textContent = '00');
    document.getElementById('hours') && (document.getElementById('hours').textContent = '00');
    document.getElementById('minutes') && (document.getElementById('minutes').textContent = '00');
    document.getElementById('seconds') && (document.getElementById('seconds').textContent = '00');
    return;
  }
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((diff % (1000 * 60)) / 1000);
  const pad = n => n.toString().padStart(2, '0');
  document.getElementById('days') && (document.getElementById('days').textContent = days);
  document.getElementById('hours') && (document.getElementById('hours').textContent = pad(hours));
  document.getElementById('minutes') && (document.getElementById('minutes').textContent = pad(minutes));
  document.getElementById('seconds') && (document.getElementById('seconds').textContent = pad(seconds));
}
if (document.getElementById('days')) {
  updateCountdown();
  setInterval(updateCountdown, 1000);
}

// ===== 数字滚动动画 =====
function animateCounters() {
  document.querySelectorAll('.stat-card').forEach(card => {
    const target = parseInt(card.dataset.target || 0);
    const counter = card.querySelector('.counter');
    if (!counter || !target) return;
    let current = 0;
    const step = Math.ceil(target / 60);
    const timer = setInterval(() => {
      current += step;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      counter.textContent = current.toLocaleString();
    }, 30);
  });
}

// ===== 滚动动画 =====
function setupScrollAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        // 触发统计数字动画
        if (entry.target.closest('.stats-section')) {
          animateCounters();
        }
      }
    });
  }, { threshold: 0.15 });

  document.querySelectorAll('.timeline-item, .stat-card, .activity-card, .history-item').forEach(el => {
    observer.observe(el);
  });
  // 统计区域
  const statsSection = document.querySelector('.stats-section');
  if (statsSection) observer.observe(statsSection);
}

// ===== 粒子效果 =====
function createParticles() {
  const container = document.getElementById('particles');
  if (!container) return;
  const count = 30;
  for (let i = 0; i < count; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    const size = Math.random() * 4 + 2;
    p.style.cssText = `
      width: ${size}px;
      height: ${size}px;
      left: ${Math.random() * 100}%;
      animation-duration: ${Math.random() * 15 + 10}s;
      animation-delay: ${Math.random() * 10}s;
      opacity: ${Math.random() * 0.5 + 0.1};
    `;
    container.appendChild(p);
  }
  // 流星效果
  for (let i = 0; i < 5; i++) {
    const star = document.createElement('div');
    star.style.cssText = `
      position: absolute;
      width: ${Math.random() * 3 + 1}px;
      height: ${Math.random() * 60 + 30}px;
      left: ${Math.random() * 100}%;
      top: ${Math.random() * 60}%;
      background: linear-gradient(180deg, transparent, rgba(200,162,0,0.6));
      border-radius: 50%;
      animation: float ${Math.random() * 8 + 6}s linear ${Math.random() * 5}s infinite;
      pointer-events: none;
    `;
    container.appendChild(star);
  }
}

// ===== 导航栏滚动效果 =====
function setupNavScroll() {
  const nav = document.querySelector('.nav');
  if (!nav) return;
  window.addEventListener('scroll', () => {
    if (window.scrollY > 60) {
      nav.style.background = 'rgba(5,14,26,0.98)';
    } else {
      nav.style.background = 'rgba(5,14,26,0.92)';
    }
  });
}

// ===== 关闭弹窗 =====
function closeModal(id) {
  document.getElementById(id) && document.getElementById(id).classList.remove('show');
}
// 点击遮罩关闭
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('show');
  }
});

// ===== 平滑滚动 =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    target && target.scrollIntoView({ behavior: 'smooth' });
  });
});

// ===== 初始化 =====
document.addEventListener('DOMContentLoaded', () => {
  createParticles();
  setupScrollAnimations();
  setupNavScroll();
  // 触发已在视口内的元素
  setTimeout(() => {
    document.querySelectorAll('.timeline-item, .stat-card, .activity-card, .history-item').forEach(el => {
      const rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight) {
        el.classList.add('visible');
      }
    });
  }, 100);
});
