
/* Digital KnowOra Ultimate Theme JS */
document.addEventListener('DOMContentLoaded', function() {

  /* Countdown Timer */
  function startTimer() {
    var hrs = 23, min = 59, sec = 59;
    var stored = sessionStorage.getItem('dk_timer');
    if (stored) {
      var p = stored.split(':');
      hrs = parseInt(p[0]); min = parseInt(p[1]); sec = parseInt(p[2]);
    }
    setInterval(function() {
      sec--;
      if (sec < 0) { sec = 59; min--; }
      if (min < 0) { min = 59; hrs--; }
      if (hrs < 0) { hrs = 23; min = 59; sec = 59; }
      var hh = hrs < 10 ? '0'+hrs : hrs;
      var mm = min < 10 ? '0'+min : min;
      var ss = sec < 10 ? '0'+sec : sec;
      var els1 = document.getElementById('t-hrs');
      var els2 = document.getElementById('t-min');
      var els3 = document.getElementById('t-sec');
      if (els1) els1.textContent = hh;
      if (els2) els2.textContent = mm;
      if (els3) els3.textContent = ss;
      var pdT = document.getElementById('pd-timer');
      if (pdT) pdT.textContent = hh + ':' + mm + ':' + ss;
      sessionStorage.setItem('dk_timer', hrs+':'+min+':'+sec);
    }, 1000);
  }
  startTimer();

  /* Social Proof Popup */
  var names = ['Rahul from Delhi','Priya from Mumbai','Amit from Pune','Neha from Bangalore','Vikas from Jaipur','Sneha from Hyderabad','Ravi from Chennai','Pooja from Kolkata'];
  var products = ['Portable Blender','Bookkeeping Tracker','Sunset Lamp','Wireless Earbuds','LED Strip Lights','Real Estate ROI Calculator','Freelance CRM','Smart Watch'];
  var times = ['2 minutes ago','5 minutes ago','Just now','8 minutes ago','12 minutes ago'];
  var spEl = document.getElementById('socialProof');
  if (spEl) {
    function showSP() {
      var n = names[Math.floor(Math.random()*names.length)];
      var p = products[Math.floor(Math.random()*products.length)];
      var t = times[Math.floor(Math.random()*times.length)];
      document.getElementById('spName').textContent = n;
      document.getElementById('spAction').innerHTML = 'just purchased <b>'+p+'</b>';
      document.getElementById('spTime').textContent = t;
      spEl.style.display = 'flex';
      setTimeout(function(){ spEl.style.display = 'none'; }, 4000);
    }
    setTimeout(showSP, 5000);
    setInterval(showSP, 15000);
  }

  /* Scroll Animations */
  var obsOpts = { threshold: 0.1, rootMargin: '0px 0px -40px 0px' };
  var obs = new IntersectionObserver(function(entries) {
    entries.forEach(function(e) {
      if (e.isIntersecting) {
        e.target.style.opacity = '1';
        e.target.style.transform = 'translateY(0)';
      }
    });
  }, obsOpts);
  document.querySelectorAll('.swipe-card, .cat-pill, .tr-item, .rev-card').forEach(function(el) {
    el.style.opacity = '0';
    el.style.transform = 'translateY(25px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    obs.observe(el);
  });
});
