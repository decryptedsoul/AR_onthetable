import {useEffect, useRef, useState} from 'react';
import type {DetailedHTMLProps, HTMLAttributes} from 'react';
import {Link, useSearchParams} from 'react-router-dom';
import '@google/model-viewer';
import type {ModelViewerElement} from '@google/model-viewer';
import {getMenu} from './api';

type ViewerProps = DetailedHTMLProps<HTMLAttributes<ModelViewerElement>, ModelViewerElement> & {
  src: string; alt: string; ar?: boolean; 'ar-modes'?: string; 'camera-controls'?: boolean;
  'touch-action'?: string; 'shadow-intensity'?: string; 'camera-orbit'?: string;
};
declare module 'react' {
  namespace JSX { interface IntrinsicElements { 'model-viewer': ViewerProps; } }
}

export default function PreviewPage() {
  const viewer = useRef<ModelViewerElement>(null);
  const [status, setStatus] = useState<'loading'|'ready'|'error'>('loading');
  const [canAR, setCanAR] = useState(false);
  const [message, setMessage] = useState('');
  const [params] = useSearchParams();
  const dishId = params.get('dish');
  const [dishName, setDishName] = useState('');
  useEffect(() => {
    setDishName('');
    if (!dishId) return;
    const controller = new AbortController();
    getMenu('', '', 0, controller.signal, [dishId]).then(data => setDishName(data.dishes[0]?.name || '')).catch(() => {});
    return () => controller.abort();
  }, [dishId]);
  useEffect(() => {
    const model = viewer.current;
    if (!model) return;
    const loaded = () => {setStatus('ready'); setCanAR(model.canActivateAR);};
    const failed = () => setStatus('error');
    const arStatus = (event: Event) => {
      if ((event as CustomEvent).detail.status === 'failed') setMessage('Table placement could not start. You can still explore the 3D sample here.');
    };
    model.addEventListener('load', loaded); model.addEventListener('error', failed); model.addEventListener('ar-status', arStatus);
    if (model.loaded) loaded();
    return () => {model.removeEventListener('load', loaded); model.removeEventListener('error', failed); model.removeEventListener('ar-status', arStatus);};
  }, []);
  return <main id="main-content" className="preview-page"><header className="page-heading"><p className="eyebrow">A CLOSER LOOK</p><h1>A place at your table.</h1><p>Turn it around. Look a little closer. Explore what a future menu preview can feel like.</p></header>
    <div className="preview-workspace"><section className="model-stage" aria-label="Interactive sample model"><div className="model-caption"><span>LIVE 3D DEMO</span><span>01 / AVOCADO</span></div>
      <model-viewer ref={viewer} src="/models/avocado-mobile.glb" alt="Interactive cut avocado sample, not a Coconut Grove menu item" camera-controls ar ar-modes="webxr scene-viewer quick-look" touch-action="pan-y" shadow-intensity="1" camera-orbit="30deg 70deg 0.35m"><span slot="ar-button" hidden /></model-viewer>
      <p className="model-instruction" role="status">{status === 'loading' ? 'Loading the sample model…' : status === 'error' ? '3D preview unavailable. Check your connection and WebGL support, then reload.' : 'Drag to rotate · Pinch or scroll to zoom'}</p>
      <button className="text-button reset-model" disabled={status !== 'ready'} onClick={() => {if (viewer.current) {viewer.current.cameraOrbit='30deg 70deg 0.35m'; viewer.current.jumpCameraToGoal();}}}>Reset view ↺</button>
    </section><aside className="preview-guide"><p className="eyebrow">TRY THE EXPERIENCE</p><h2>From screen<br/>to your space.</h2><p>This working sample uses an avocado model. It is a technology demonstration, separate from the restaurant’s dishes.</p>
      <div className="preview-status"><span className="sample-label">{status === 'ready' ? 'Interactive 3D · Ready' : 'Interactive 3D · '+status}</span><p>{canAR ? 'Your browser reports support for AR. Use the button below, then follow your device’s placement instructions.' : 'Explore in 3D here. Table placement appears on compatible phones and browsers; camera access needs a secure connection.'}</p></div>
      {canAR && status === 'ready' && <button className="button" onClick={() => {setMessage(''); viewer.current?.activateAR().catch(() => setMessage('AR could not open on this device. The 3D viewer remains available.'));}}>View sample in your space ↗</button>}
      {message && <p role="status">{message}</p>}
      <div className="dish-pending"><span className="sample-label">Restaurant dish previews · Planned</span><h3>{dishName || 'Your favorite dish, next.'}</h3><p>To preview an actual serving, we need an approved 3D model, measured plate and portion sizes, and testing on iPhone and Android. This sample does not demonstrate a verified serving size.</p><Link to="/menu">Back to the menu →</Link></div>
    </aside></div><p className="model-credit">Sample: Avocado, Microsoft · CC0, via <a href="https://github.com/KhronosGroup/glTF-Sample-Assets/tree/main/Models/Avocado" target="_blank" rel="noopener noreferrer">Khronos glTF Sample Assets</a>. Textures resized for mobile. Camera access is requested only when starting supported AR; the website does not record video.</p>
  </main>;
}
