import {useEffect, useRef, useState} from 'react';
import {getMenu} from './api';
import type {Dish, MenuResponse} from './types';
import {useNavigate} from 'react-router-dom';
import {DishCard} from './DishCard';
import {DishDetails} from './DishDetails';
import {MenuSkeleton} from './MenuSkeleton';


function initialSaved(): string[] {
  try {const value: unknown = JSON.parse(localStorage.getItem('grove-saved') || '[]'); return Array.isArray(value) ? [...new Set(value.filter((id): id is string => typeof id === 'string' && id.length > 0 && id.length <= 100))].slice(0,100) : [];} catch {return [];}
}

export default function MenuPage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [offset, setOffset] = useState(0);
  const [menu, setMenu] = useState<MenuResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [retry, setRetry] = useState(0);
  const [saved, setSaved] = useState(initialSaved);
  const [savedOnly, setSavedOnly] = useState(false);
  const [selected, setSelected] = useState<Dish | null>(null);
  const [toast, setToast] = useState('');
  const toastTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const savedFilter = savedOnly ? JSON.stringify(saved) : null;

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true); setError('');
    const timer = setTimeout(() => {
      getMenu(query, category, offset, controller.signal, savedFilter === null ? undefined : JSON.parse(savedFilter) as string[])
        .then(value => {if (!controller.signal.aborted) setMenu(value);})
        .catch((cause: unknown) => {if (!controller.signal.aborted) setError(cause instanceof Error ? cause.message : 'Unable to load menu.');})
        .finally(() => {if (!controller.signal.aborted) setLoading(false);});
    }, query ? 200 : 0);
    return () => {clearTimeout(timer); controller.abort();};
  }, [query, category, offset, retry, savedFilter]);

  useEffect(() => () => {clearTimeout(toastTimer.current);}, []);

  function toggleSave(id: string) {
    if (!saved.includes(id) && saved.length >= 100) {
      clearTimeout(toastTimer.current); setToast('You can save up to 100 dishes on this device.');
      toastTimer.current = setTimeout(() => setToast(''), 2600); return;
    }
    const next = saved.includes(id) ? saved.filter(value => value !== id) : [...saved, id];
    setSaved(next);
    let message = next.includes(id) ? 'Dish saved' : 'Dish removed from saved';
    try {localStorage.setItem('grove-saved', JSON.stringify(next));} catch {message += '. Saved for this visit only.';}
    clearTimeout(toastTimer.current); setToast(message);
    toastTimer.current = setTimeout(() => setToast(''), 2600);
  }
  function reset() {setQuery(''); setCategory(''); setOffset(0); setSavedOnly(false);}
  const visibleDishes = menu?.dishes.filter(dish => !savedOnly || saved.includes(dish.id)) || [];
  const hasFilters = !!query || !!category || savedOnly || offset > 0;
  const currency = menu?.restaurant.currency || 'PKR';

  return <>
    <main className="menu-page" id="main-content"><header className="page-heading"><p className="eyebrow">THE COCONUT GROVE MENU</p><h1>What sounds good?</h1><p>From the grill to something sweet. Find a familiar favorite, or try something new.</p><button className="saved-button" id="saved-toggle" aria-pressed={savedOnly} onClick={() => {setSavedOnly(!savedOnly); setOffset(0);}}>Saved dishes ({saved.length})</button></header>
      <section className="menu-section" id="menu" aria-labelledby="menu-title">
        <div className="section-heading"><h2 id="menu-title">Find your next favorite</h2><svg className="menu-flourish" viewBox="0 0 32 32" aria-hidden="true"><path d="M16 2v28M2 16h28M6 6l20 20M6 26 26 6" /></svg></div>
        <p className="section-intro">A little browsing before the first bite.</p>
        <div className="menu-tools"><label className="search-box" htmlFor="dish-search"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5" /><path d="m16 16 4.5 4.5" /></svg><input id="dish-search" type="search" placeholder="Search the menu" autoComplete="off" maxLength={100} value={query} onChange={event => {setQuery(event.target.value); setOffset(0);}} /><span className="sr-only">Search the menu</span></label>
          <label className="mobile-category">Browse by category<select value={category} onChange={event => {setCategory(event.target.value); setOffset(0);}}><option value="">All dishes</option>{menu?.categories.map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
          <div className="categories" role="group" aria-label="Menu categories" id="categories"><button className="category" data-category="All dishes" aria-pressed={!category} onClick={() => {setCategory(''); setOffset(0);}}>All dishes</button>{menu?.categories.map(item => <button className="category" key={item.id} data-category={item.name} aria-pressed={category === item.id} onClick={() => {setCategory(item.id); setOffset(0);}}>{item.name}</button>)}</div>
        </div>
        <div className="menu-notice"><span className="sample-label">Published menu reference</span><p>Original item names from <a href="https://www.menupak.com/m/coconut-grove-karachi" target="_blank" rel="noopener noreferrer">MenuPak</a>, checked 6 Nov 2026. Reference prices may change. Ingredients, timing and portions await restaurant confirmation.</p></div>
        <div className="results-line"><p id="results-count" role="status" aria-live="polite">{loading ? 'Loading menu…' : error ? 'Menu unavailable' : `${menu?.total || 0} ${menu?.total === 1 ? 'dish' : 'dishes'}${savedOnly ? ' saved' : ' to explore'}`}</p>{hasFilters && <button id="reset-filters" className="text-button" onClick={reset}>Clear filters</button>}</div>
        {error && <div className="empty-state" role="alert"><h3>We couldn’t load the menu</h3><p>{error}</p><button className="button" onClick={() => setRetry(value => value + 1)}>Try again</button></div>}
        <div id="dish-list" className="dish-list" aria-busy={loading}>{loading && <MenuSkeleton count={Math.max(1, Math.min(menu?.dishes.length ?? 3, 6))} />}{!loading && !error && visibleDishes.map(dish => <DishCard key={dish.id} dish={dish} currency={currency} saved={saved.includes(dish.id)} onSave={() => toggleSave(dish.id)} onOpen={() => setSelected(dish)} />)}</div>
        {!loading && !error && !visibleDishes.length && <div id="empty-state" className="empty-state"><h3>{savedOnly ? 'No saved dishes here' : 'No dishes found'}</h3><p>{savedOnly ? 'Save a dish with its heart button, or browse another page of the menu.' : 'Try another search or explore the full menu.'}</p><button className="button" id="empty-reset" onClick={reset}>Show all dishes</button></div>}
        {menu && !loading && !error && menu.total > menu.limit && <nav className="pagination" aria-label="Menu pages"><button className="text-button" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - menu.limit))}>Previous</button><span>Page {Math.floor(offset / menu.limit) + 1} of {Math.ceil(menu.total / menu.limit)}</span><button className="text-button" disabled={offset + menu.limit >= menu.total} onClick={() => setOffset(offset + menu.limit)}>Next</button></nav>}
      </section></main>
    {selected && <DishDetails key={selected.id} dish={selected} currency={currency} onClose={() => setSelected(null)} onAR={() => navigate('/preview?dish=' + encodeURIComponent(selected.id))} />}
    <div id="toast" className={`toast ${toast ? 'visible' : ''}`} role="status" aria-live="polite">{toast}</div>

  </>;
}
