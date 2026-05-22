// My Deliveries page logic: status transitions + POD capture
(function(){
  const updateUrl = window.RIDER_UPDATE_URL || document.querySelector('.container[data-update-url]')?.dataset.updateUrl || '/rider/delivery/update';

  function toast(msg, type='info'){
    const div = document.createElement('div');
    div.className = `alert alert-${type} position-fixed top-0 end-0 m-3`; div.style.zIndex=1060;
    div.innerHTML = `<i class="fas ${type==='success'?'fa-check-circle':type==='danger'?'fa-exclamation-circle':'fa-info-circle'} me-2"></i>${msg}`;
    document.body.appendChild(div); setTimeout(()=>div.remove(), 3500);
  }

  async function postForm(formData){
    const res = await fetch(updateUrl, { method:'POST', body: formData });
    if(!res.ok){ throw new Error((await res.json()).message || 'Request failed'); }
    return res.json();
  }

  function setRowStatus(deliveryId, status){
    const row = document.getElementById(`delivery-row-${deliveryId}`); if(!row) return;
    row.dataset.status = status;
    const badge = row.querySelector('.delivery-status');
    const map = {delivered:['success','Delivered'], on_the_way:['warning','On The Way'], picked_up:['warning','Picked Up'], assigned:['secondary','Assigned'], failed:['danger','Failed']};
    const [cls,label] = map[status] || ['secondary', status];
    badge.className = `badge delivery-status bg-${cls}`; badge.textContent = label;
    if(['delivered','failed'].includes(status)){
      const btns = row.querySelectorAll('button'); btns.forEach(b=>b.disabled=true);
    }
  }

  // Quick status buttons
  function bindActionButtons(){
    document.querySelectorAll('.btn-pickup').forEach(btn=>{
      btn.addEventListener('click', async ()=>{
        const id = btn.dataset.deliveryId; const fd = new FormData();
        fd.append('delivery_id', id); fd.append('status','picked_up');
        try{ await postForm(fd); setRowStatus(id,'picked_up'); toast('Marked as picked up','success'); }
        catch(e){ toast(e.message||'Failed', 'danger'); }
      });
    });
    document.querySelectorAll('.btn-ontheway').forEach(btn=>{
      btn.addEventListener('click', async ()=>{
        const id = btn.dataset.deliveryId; const fd = new FormData();
        fd.append('delivery_id', id); fd.append('status','on_the_way');
        try{ await postForm(fd); setRowStatus(id,'on_the_way'); toast('Marked on the way','success'); }
        catch(e){ toast(e.message||'Failed', 'danger'); }
      });
    });
    document.querySelectorAll('.btn-failed').forEach(btn=>{
      btn.addEventListener('click', async ()=>{
        const id = btn.dataset.deliveryId; const reason = prompt('Reason for failure?'); if(reason===null) return;
        const fd = new FormData(); fd.append('delivery_id', id); fd.append('status','failed'); fd.append('failure_reason', reason||'');
        try{ await postForm(fd); setRowStatus(id,'failed'); toast('Delivery marked failed','success'); }
        catch(e){ toast(e.message||'Failed', 'danger'); }
      });
    });
    document.querySelectorAll('.btn-complete').forEach(btn=>{
      btn.addEventListener('click', ()=> openPodModal(btn.dataset.deliveryId, btn.dataset.orderId));
    });
  }

  // POD modal, signature, photo, map, GPS
  let podModal, map, marker, drawing=false, lastPt=null;
  const podEl = document.getElementById('podModal');
  const podForm = document.getElementById('podForm');
  const podPhotoInput = document.getElementById('podPhotoInput');
  const podPhotoPreview = document.getElementById('podPhotoPreview');
  const podSigCanvas = document.getElementById('podSignature');
  const podSigFile = document.getElementById('podSignatureFile');
  const clearBtn = document.getElementById('clearSignature');
  const saveBtn = document.getElementById('saveSignature');
  const submitBtn = document.getElementById('submitPodBtn');

  function resizeCanvas(){
    if(!podSigCanvas) return;
    const rect = podSigCanvas.getBoundingClientRect();
    // If modal is hidden, rect will be 0x0; skip to avoid collapsing canvas
    if(!rect.width || !rect.height) return;
    const tmp = document.createElement('canvas');
    tmp.width = podSigCanvas.width || rect.width;
    tmp.height = podSigCanvas.height || rect.height;
    const tctx = tmp.getContext('2d');
    if(tctx){ tctx.drawImage(podSigCanvas,0,0); }
    podSigCanvas.width = rect.width;
    podSigCanvas.height = rect.height;
    const ctx = podSigCanvas.getContext('2d');
    ctx.fillStyle = '#fff';
    ctx.fillRect(0,0,rect.width,rect.height);
    ctx.drawImage(tmp,0,0);
  }

  function bindSignature(){ if(!podSigCanvas) return; const ctx = podSigCanvas.getContext('2d'); ctx.lineWidth=2; ctx.lineCap='round';
    const pos = (e)=>{ const r=podSigCanvas.getBoundingClientRect(); const t = (e.touches? e.touches[0]: e); return {x: t.clientX - r.left, y: t.clientY - r.top}; };
    const start=(e)=>{ drawing=true; lastPt=pos(e); e.preventDefault(); };
    const move=(e)=>{ if(!drawing) return; const p=pos(e); ctx.beginPath(); ctx.moveTo(lastPt.x,lastPt.y); ctx.lineTo(p.x,p.y); ctx.stroke(); lastPt=p; e.preventDefault(); };
    const end=()=>{ drawing=false; };
    podSigCanvas.addEventListener('mousedown', start); podSigCanvas.addEventListener('mousemove', move); window.addEventListener('mouseup', end);
    podSigCanvas.addEventListener('touchstart', start, {passive:false}); podSigCanvas.addEventListener('touchmove', move, {passive:false}); podSigCanvas.addEventListener('touchend', end);
    clearBtn?.addEventListener('click', ()=>{ ctx.clearRect(0,0,podSigCanvas.width,podSigCanvas.height); ctx.fillStyle='#fff'; ctx.fillRect(0,0,podSigCanvas.width,podSigCanvas.height); });
    saveBtn?.addEventListener('click', ()=>{
      podSigCanvas.toBlob((blob)=>{ if(!blob) return; const file = new File([blob], 'signature.png', {type:'image/png'}); const dt = new DataTransfer(); dt.items.add(file); podSigFile.files = dt.files; toast('Signature saved','success'); });
    });
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();
  }

  function openPodModal(deliveryId, orderId){
    document.getElementById('podDeliveryId').value = deliveryId;
    document.getElementById('podOrderId').value = orderId || '';
    if(!podModal){ podModal = new bootstrap.Modal(podEl); }
    podModal.show();
    // init map and geolocation + resize signature canvas once modal is visible
    setTimeout(()=>{ initMapAndGPS(); resizeCanvas(); }, 80);
  }

  function initMapAndGPS(){
    const latEl = document.getElementById('podLat'); const lngEl = document.getElementById('podLng');
    const mapDiv = document.getElementById('podMap'); if(!mapDiv) return;
    if(!map){ map = L.map('podMap'); L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map); }
    if(navigator.geolocation){ navigator.geolocation.getCurrentPosition((pos)=>{
        const {latitude, longitude} = pos.coords; latEl.value = latitude; lngEl.value = longitude;
        const ll = [latitude, longitude]; map.setView(ll, 16); if(marker){ marker.setLatLng(ll); } else { marker = L.marker(ll).addTo(map); }
      }, ()=>{ map.setView([14.5995,120.9842], 12); /* Manila fallback */ }, { enableHighAccuracy:true, timeout:8000, maximumAge:30000 });
    } else { map.setView([14.5995,120.9842], 12); }
    setTimeout(()=>{ map.invalidateSize(); }, 250);
  }

  // photo preview
  podPhotoInput?.addEventListener('change', ()=>{
    const f = podPhotoInput.files?.[0]; if(!f){ podPhotoPreview.classList.add('d-none'); return; }
    const url = URL.createObjectURL(f); podPhotoPreview.src = url; podPhotoPreview.classList.remove('d-none');
  });

  // submit POD
  submitBtn?.addEventListener('click', async ()=>{
    if(!podForm.reportValidity()) return;
    // ensure signature file set if drawn
    if(podSigFile && podSigFile.files.length===0){ // auto-save if not saved
      podSigCanvas.toBlob((blob)=>{ if(blob){ const file = new File([blob], 'signature.png', {type:'image/png'}); const dt = new DataTransfer(); dt.items.add(file); podSigFile.files = dt.files; doSubmit(); } else { doSubmit(); } });
    } else { doSubmit(); }
  });

  async function doSubmit(){
    try{
      const fd = new FormData(podForm);
      const res = await postForm(fd);
      if(res.success){
        const id = document.getElementById('podDeliveryId').value;
        setRowStatus(id,'delivered'); toast('POD submitted, delivery completed','success'); podModal?.hide();
      } else { throw new Error(res.message||'Failed'); }
    } catch(e){ toast(e.message||'Failed to submit POD','danger'); }
  }

  // init
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      bindActionButtons();
      bindSignature();
    });
  } else {
    bindActionButtons();
    bindSignature();
  }
})();
