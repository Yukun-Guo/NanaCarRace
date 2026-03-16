(function(){
  const canvas=document.getElementById('gameCanvas');
  const ctx=canvas.getContext('2d');
  const scoreEl=document.getElementById('score');
  const W=canvas.width, H=canvas.height;
  let keys={left:false,right:false};
  window.addEventListener('keydown',e=>{if(e.key==='ArrowLeft')keys.left=true; if(e.key==='ArrowRight')keys.right=true; if(e.key===' '){init();}}
  ,false);
  window.addEventListener('keyup',e=>{if(e.key==='ArrowLeft')keys.left=false; if(e.key==='ArrowRight')keys.right=false;},false);

  function rand(min,max){return Math.random()*(max-min)+min}

  let player, obstacles, frame, score, running;
  function init(){
    player={w:40,h:60,x:W/2-20,y:H-100,speed:4};
    obstacles=[];
    frame=0;score=0;running=true;scoreEl.textContent=score;
    requestAnimationFrame(loop);
  }

  function spawn(){
    const laneWidth=W*0.6; const laneX=(W-laneWidth)/2;
    const w=rand(30,80); const x=rand(laneX, laneX+laneWidth-w);
    obstacles.push({x:x,y:-60,w:w,h:20,vy:2+Math.random()*2});
  }

  function update(){
    if(keys.left) player.x -= player.speed;
    if(keys.right) player.x += player.speed;
    // clamp to canvas
    const laneWidth=W*0.6; const laneX=(W-laneWidth)/2;
    if(player.x < laneX) player.x = laneX;
    if(player.x + player.w > laneX+laneWidth) player.x = laneX+laneWidth - player.w;

    // obstacles
    if(frame%60===0) spawn();
    for(let i=obstacles.length-1;i>=0;i--){
      const o=obstacles[i]; o.y += o.vy; if(o.y>H+100) {obstacles.splice(i,1); score+=1; scoreEl.textContent=score}
      // collision AABB
      if(!(player.x+player.w < o.x || player.x > o.x+o.w || player.y+player.h < o.y || player.y > o.y+o.h)){
        running=false;
      }
    }
  }

  function draw(){
    // clear
    ctx.clearRect(0,0,W,H);
    // draw road
    const laneWidth=W*0.6; const laneX=(W-laneWidth)/2;
    ctx.fillStyle='#444'; ctx.fillRect(laneX,0,laneWidth,H);
    // lane lines
    ctx.strokeStyle='#aaa'; ctx.lineWidth=2; ctx.setLineDash([10,10]);
    for(let y=0;y<H;y+=80){ctx.beginPath();ctx.moveTo(W/2,y);ctx.lineTo(W/2,y+40);ctx.stroke();}
    ctx.setLineDash([]);

    // draw player
    ctx.fillStyle='#ff3333'; ctx.fillRect(player.x,player.y,player.w,player.h);
    // obstacles
    ctx.fillStyle='#222'; ctx.strokeStyle='#fff';
    for(const o of obstacles){ctx.fillRect(o.x,o.y,o.w,o.h); ctx.strokeRect(o.x,o.y,o.w,o.h)}

    if(!running){
      ctx.fillStyle='rgba(0,0,0,0.6)'; ctx.fillRect(0,H/2-40,W,80);
      ctx.fillStyle='#fff'; ctx.font='20px sans-serif'; ctx.textAlign='center'; ctx.fillText('Game Over - Press Space to Restart',W/2,H/2+8);
    }
  }

  function loop(){
    frame++; if(running){update(); draw(); requestAnimationFrame(loop);} else {draw();}
  }

  // initialize positions and start
  init();
})();
