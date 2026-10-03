(() => {
const links=[...document.querySelectorAll('[data-plate]')], dialog=document.querySelector('.plate-viewer');
if(!dialog || typeof dialog.showModal !== 'function') return;
const img=dialog.querySelector('.viewer-image'), label=dialog.querySelector('#plate-label'), prev=dialog.querySelector('.previous'), next=dialog.querySelector('.next');
let current=0;
function show(i){current=i;img.src=links[i].href;img.alt=links[i].querySelector('img').alt;label.textContent=`Plate ${['I','II','III','IV','V','VI'][i]} / VI`;prev.disabled=i===0;next.disabled=i===links.length-1;}
links.forEach((a,i)=>a.addEventListener('click',e=>{if(e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;e.preventDefault();show(i);dialog.showModal();document.body.style.overflow='hidden';}));
prev.addEventListener('click',()=>{if(current>0)show(current-1)});next.addEventListener('click',()=>{if(current<links.length-1)show(current+1)});
dialog.querySelector('.close-viewer').addEventListener('click',()=>dialog.close());
dialog.addEventListener('close',()=>{document.body.style.overflow='';links[current].focus()});
dialog.addEventListener('keydown',e=>{if(e.key==='ArrowRight'&&current<links.length-1){e.preventDefault();show(current+1)}if(e.key==='ArrowLeft'&&current>0){e.preventDefault();show(current-1)}});
})();