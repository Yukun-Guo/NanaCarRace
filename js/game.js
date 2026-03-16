(function(){
  const canvas=document.getElementById('gameCanvas');
  const ctx=canvas.getContext('2d');
  const scoreEl=document.getElementById('score');
  let keys={left:false,right:false};

  function resizeCanvas(){
    const rect = canvas.getBoundingClientRect();
    if(rect.width===0 || rect.height===0) return;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.max(320, Math.floor(rect.width * dpr));
    canvas.height = Math.max(480, Math.floor(rect.height * dpr));
    canvas.style.width = rect.width + 'px';
    canvas.style.height = rect.height + 'px';
    ctx.setTransform(dpr,0,0,dpr,0,0);
  }

  window.addEventListener('resize', resizeCanvas);
  window.addEventListener('orientationchange', resizeCanvas);

  window.addEventListener('keydown',e=>{
    const code = e.code || e.key;
    if(code==='ArrowLeft'){ keys.left=true; e.preventDefault(); }
    if(code==='ArrowRight'){ keys.right=true; e.preventDefault(); }
    if(code==='Space' || code==='Spacebar' || e.key===' '){ if(!running){ e.preventDefault(); init(); } }
  },false);
  window.addEventListener('keyup',e=>{const code=e.code||e.key; if(code==='ArrowLeft')keys.left=false; if(code==='ArrowRight')keys.right=false;},false);

  function rand(min,max){return Math.random()*(max-min)+min}

  let player, obstacles, lastTime, score, running, lastSpawnTime;

  function getW(){return canvas.width}
  function getH(){return canvas.height}

  function init(){
    resizeCanvas();
    const W=getW(), H=getH();
    player={w:Math.floor(W*0.12),h:Math.floor(H*0.12),x:W/2-Math.floor(W*0.12)/2,y:H-Math.floor(H*0.18),speed:Math.max(3,Math.floor(W*0.008))};
    obstacles=[];
    lastTime = performance.now();
    lastSpawnTime = lastTime;
    score=0;running=true;scoreEl.textContent=score;
    canvas.focus();
    requestAnimationFrame(loop);
  }

  function spawn(){
    const W=getW(), laneWidth=W*0.6; const laneX=(W-laneWidth)/2;
    const w=rand(Math.floor(W*0.08),Math.floor(W*0.22)); const x=rand(laneX+10, laneX+laneWidth-w-10);
    obstacles.push({x:x,y:-60,w:w,h:Math.floor(W*0.04),vy:2+Math.random()*2});
  }

  function update(delta){
    const W=getW(), H=getH();
    if(keys.left) player.x -= player.speed * (delta/16);
    if(keys.right) player.x += player.speed * (delta/16);
    const laneWidth=W*0.6; const laneX=(W-laneWidth)/2;
    if(player.x < laneX) player.x = laneX;
    if(player.x + player.w > laneX+laneWidth) player.x = laneX+laneWidth - player.w;

    const now = performance.now();
    if(now - lastSpawnTime > 900) { spawn(); lastSpawnTime = now; }

    for(let i=obstacles.length-1;i>=0;i--){
      const o=obstacles[i]; o.y += o.vy * (delta/16); if(o.y>H+100) {obstacles.splice(i,1); score+=1; scoreEl.textContent=score}
      if(!(player.x+player.w < o.x || player.x > o.x+o.w || player.y+player.h < o.y || player.y > o.y+o.h)){
        running=false;
      }
    }
  }

  function draw(){
    const W=getW(), H=getH();
    ctx.clearRect(0,0,W,H);
    const laneWidth=W*0.6; const laneX=(W-laneWidth)/2;
    ctx.fillStyle='#444'; ctx.fillRect(laneX,0,laneWidth,H);
    ctx.strokeStyle='#aaa'; ctx.lineWidth=2; ctx.setLineDash([10,10]);
    for(let y=0;y<H;y+=Math.floor(H*0.12)){ctx.beginPath();ctx.moveTo(W/2,y);ctx.lineTo(W/2,y+Math.floor(H*0.06));ctx.stroke();}
    ctx.setLineDash([]);

    ctx.save();
    const tilt = (keys.left ? -0.08 : (keys.right ? 0.08 : 0));
    ctx.translate(player.x+player.w/2, player.y+player.h/2);
    ctx.rotate(tilt);
    ctx.fillStyle='#ff3333'; ctx.fillRect(-player.w/2,-player.h/2,player.w,player.h);
    ctx.restore();

    ctx.fillStyle='#222'; ctx.strokeStyle='#fff';
    for(const o of obstacles){ctx.fillRect(o.x,o.y,o.w,o.h); ctx.strokeRect(o.x,o.y,o.w,o.h)}

    if(!running){
      ctx.fillStyle='rgba(0,0,0,0.6)'; ctx.fillRect(0,H/2-Math.floor(H*0.06),W,Math.floor(H*0.12));
      ctx.fillStyle='#fff'; ctx.font=Math.floor(H*0.04)+'px sans-serif'; ctx.textAlign='center'; ctx.fillText('Game Over - Press Space to Restart',W/2,H/2+Math.floor(H*0.01));
    }
  }

  let lastFrameTime = performance.now();
  function loop(now){
    const delta = now - lastFrameTime; lastFrameTime = now;
    if(running){update(delta); draw(); requestAnimationFrame(loop);} else {draw();}
  }

  // simple touch controls: left/right buttons or pointer zones
  function setupTouchControls(){
    const leftBtn = document.getElementById('touch-left');
    const rightBtn = document.getElementById('touch-right');
    if(leftBtn && rightBtn){
      document.getElementById('touch-controls').style.display='block';
      const startLeft = e=>{ keys.left = true; e.preventDefault(); };
      const endLeft = e=>{ keys.left = false; e.preventDefault(); };
      const startRight = e=>{ keys.right = true; e.preventDefault(); };
      const endRight = e=>{ keys.right = false; e.preventDefault(); };
      leftBtn.addEventListener('touchstart', startLeft); leftBtn.addEventListener('touchend', endLeft);
      rightBtn.addEventListener('touchstart', startRight); rightBtn.addEventListener('touchend', endRight);
      leftBtn.addEventListener('pointerdown', startLeft); leftBtn.addEventListener('pointerup', endLeft);
      rightBtn.addEventListener('pointerdown', startRight); rightBtn.addEventListener('pointerup', endRight);
    } else {
      canvas.addEventListener('pointerdown', function(e){
        const r = canvas.getBoundingClientRect();
        const x = (e.clientX - r.left) * (window.devicePixelRatio || 1);
        if(x < canvas.width/2) keys.left = true; else keys.right = true;
      });
      canvas.addEventListener('pointerup', function(e){ keys.left=false; keys.right=false; });
    }
  }

  document.addEventListener('DOMContentLoaded', function(){
    resizeCanvas(); setupTouchControls(); init();
  });
})();
