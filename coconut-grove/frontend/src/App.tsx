import {lazy, Suspense, useEffect, useRef, useState} from 'react';
import {BrowserRouter, Link, NavLink, Route, Routes, useLocation, useNavigate} from 'react-router-dom';
import IntroPage from './IntroPage';
import {Info} from './Info';

const MenuPage = lazy(() => import('./MenuPage'));
const PreviewPage = lazy(() => import('./PreviewPage'));

function Site() {
  const location = useLocation();
  const navigate = useNavigate();
  const [credits, setCredits] = useState(false);
  const main = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const legacy = location.hash === '#menu' ? '/menu' : location.hash === '#preview' ? '/preview' : null;
    if (legacy) {navigate(legacy, {replace:true}); return;}
    window.scrollTo({top:0, behavior:'instant'});
    document.title = `Coconut Grove — ${location.pathname === '/menu' ? 'The menu' : location.pathname === '/preview' ? 'Table preview' : 'A place at your table'}`;
    main.current?.focus({preventScroll:true});
  }, [location.pathname, location.hash, navigate]);
  return <><a className="skip-link" href="#main-content">Skip to page content</a><header className="site-header fixed-header"><Link className="brand" to="/" aria-label="Coconut Grove introduction"><img src="/assets/palm.svg" width="42" height="48" alt=""/><span>COCONUT GROVE<small>Good food. Good company.</small></span></Link><nav className="page-navigation" aria-label="Main navigation"><NavLink to="/" end>Intro</NavLink><NavLink to="/menu">Menu</NavLink><NavLink to="/preview">Preview</NavLink></nav><span className="header-location">TIPU SULTAN ROAD · KARACHI</span></header>
    <div className="route-content" ref={main} tabIndex={-1}><Suspense fallback={<main id="main-content" className="page-loading" role="status">Opening the Grove…</main>}><Routes><Route path="/" element={<IntroPage/>}/><Route path="/menu" element={<MenuPage/>}/><Route path="/preview" element={<PreviewPage/>}/><Route path="*" element={<main id="main-content" className="page-heading"><h1>A little off the menu.</h1><Link className="button" to="/">Back to the Grove</Link></main>}/></Routes></Suspense></div>
    <footer className="page-footer"><Link className="footer-wordmark" to="/">Coconut Grove</Link><div className="footer-bottom"><span>Restaurant website concept · 2026</span><button className="text-button" onClick={() => setCredits(true)}>Sources &amp; project notes</button><Link to="/menu">Explore the menu ↗</Link></div></footer>{credits && <Info kind="credits" onClose={() => setCredits(false)}/>}</>;
}

export default function App() {return <BrowserRouter><Site/></BrowserRouter>;}
