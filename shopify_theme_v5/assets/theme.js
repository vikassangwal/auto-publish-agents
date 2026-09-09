
document.addEventListener('DOMContentLoaded', function() {
  /* Countdown Timer */
  var h=23,m=59,s=59;
  var st=sessionStorage.getItem('dk5_t');
  if(st){var p=st.split(':');h=+p[0];m=+p[1];s=+p[2]}
  setInterval(function(){
    s--;if(s<0){s=59;m--}if(m<0){m=59;h--}if(h<0){h=23;m=59;s=59}
    var hh=h<10?'0'+h:h,mm=m<10?'0'+m:m,ss=s<10?'0'+s:s;
    var e1=document.getElementById('fh'),e2=document.getElementById('fm'),e3=document.getElementById('fs');
    if(e1)e1.textContent=hh;if(e2)e2.textContent=mm;if(e3)e3.textContent=ss;
    sessionStorage.setItem('dk5_t',h+':'+m+':'+s);
  },1000);

  /* Social Proof */
  var names=['Rahul from Delhi','Priya from Mumbai','Amit from Pune','Neha from Bangalore','Vikas from Jaipur','Sneha from Hyderabad','Ravi from Chennai','Pooja from Kolkata','Suresh from Lucknow','Anita from Ahmedabad'];
  var prods=['Portable Blender','Bookkeeping Tracker','Sunset Lamp','Wireless Earbuds','LED Strip Lights','ROI Calculator','Smart Watch','Freelance CRM','Phone Stand','Mini Projector'];
  var times=['just now','1 min ago','2 min ago','4 min ago','7 min ago'];
  var sp=document.getElementById('spPopup');
  if(sp){
    function showSP(){
      document.getElementById('spN').textContent=names[Math.floor(Math.random()*names.length)];
      document.getElementById('spP').textContent=prods[Math.floor(Math.random()*prods.length)];
      document.getElementById('spT').textContent=times[Math.floor(Math.random()*times.length)];
      sp.style.display='flex';
      setTimeout(function(){sp.style.display='none'},4500);
    }
    setTimeout(showSP,6000);
    setInterval(showSP,18000);
  }

  /* Scroll Animation */
  var obs=new IntersectionObserver(function(es){
    es.forEach(function(e){if(e.isIntersecting){e.target.style.opacity='1';e.target.style.transform='translateY(0)'}});
  },{threshold:0.08});
  document.querySelectorAll('.deal-card,.pcard,.sc-card,.rv,.offer-card,.ts-item').forEach(function(el){
    el.style.opacity='0';el.style.transform='translateY(20px)';el.style.transition='opacity .5s ease,transform .5s ease';
    obs.observe(el);
  });
});
