// Simple animation helpers and confetti emitter (lightweight)
(function(window){
  function easeOutQuad(t){return t*(2-t)}
  function confetti(ctx, x, y, count=20){
    const pieces=[];
    for(let i=0;i<count;i++){pieces.push({x,y,vx:(Math.random()-0.5)*6,vy:(Math.random()-4)*6,life:60,color:'hsl('+ (Math.random()*60+10) +',80%,60%)'});
    }
    let frame=0;
    function draw(){
      for(const p of pieces){
        p.x += p.vx; p.y += p.vy; p.vy += 0.3; p.life--; ctx.fillStyle = p.color; ctx.fillRect(p.x,p.y,4,6);
      }
      frame++;
      return pieces.some(p=>p.life>0);
    }
    return {draw};
  }
  window.NanaAnimations = { easeOutQuad, confetti };
})(this);
