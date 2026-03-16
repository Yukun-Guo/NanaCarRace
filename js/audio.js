// Minimal audio manager
const audioCtx = (typeof AudioContext !== 'undefined') ? new AudioContext() : null;
const sounds = {};
export async function loadSound(name, url){
  if(!audioCtx) return;
  const res = await fetch(url); const ab = await res.arrayBuffer(); const buf = await audioCtx.decodeAudioData(ab);
  sounds[name]=buf;
}
export function playSound(name, loop=false, vol=0.7){
  if(!audioCtx || !sounds[name]) return;
  const src = audioCtx.createBufferSource(); src.buffer = sounds[name]; const gain = audioCtx.createGain(); gain.gain.value = vol; src.connect(gain).connect(audioCtx.destination); src.loop = loop; src.start(0); return src;
}
export function resumeAudio(){ if(audioCtx && audioCtx.state==='suspended') audioCtx.resume(); }
