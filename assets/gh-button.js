(function(){
  function openGame(){
    window.open('./NanaCarRace/game/','_blank','noopener');
  }
  document.addEventListener('DOMContentLoaded',function(){
    var btn=document.getElementById('play-nanacarrace-btn');
    if(btn){btn.addEventListener('click', openGame);}
  });
})();
