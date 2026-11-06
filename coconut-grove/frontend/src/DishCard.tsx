import type {Dish} from './types';
import {money, spiceLabel} from './format';

export function Heart() {return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20s-8-4.6-8-10a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 5.4-8 10-8 10Z"/></svg>;}

export function DishCard({dish, currency, saved, onSave, onOpen}: {dish:Dish;currency:string;saved:boolean;onSave:()=>void;onOpen:()=>void}) {
  const price = dish.portions[0]?.price_minor;
  return <article className="dish-card sourced-dish"><div className="dish-info"><p className="dish-category">{dish.category}</p><div className="dish-top"><button className="dish-title-button" data-open={dish.id} onClick={onOpen}><h3>{dish.name}</h3></button><button className="favorite-button" data-save={dish.id} onClick={onSave} aria-label={`${saved ? 'Unsave' : 'Save'} ${dish.name}`} aria-pressed={saved}><Heart/></button></div>{dish.description && <p className="dish-description">{dish.description}</p>}<div className="dish-meta"><span>{dish.preparation_minutes ? dish.preparation_minutes.join('–')+' min' : 'Time pending'}</span><span>{dish.spice_level === null ? 'Spice pending' : spiceLabel(dish.spice_level)}</span></div><div className="dish-bottom"><span className="price">{price != null ? money(price,currency) : 'Price pending'}<small>{price != null ? 'Reference price' : 'Confirmation needed'}</small></span><button className="dish-detail-link" onClick={onOpen}>Explore dish ↗</button></div><p className="planned-inline">Ingredients, portion details &amp; dish AR · Planned</p></div></article>;
}
