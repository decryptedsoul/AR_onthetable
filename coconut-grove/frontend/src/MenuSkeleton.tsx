export function MenuSkeleton({count}: {count: number}) {
  return <div className="skeleton-list" aria-hidden="true">{Array.from({length: count}, (_, index) => <div className="dish-skeleton" key={index}>
    <span className="skeleton-photo" /><div><span className="skeleton-line skeleton-title" /><span className="skeleton-line" /><span className="skeleton-line skeleton-short" /><span className="skeleton-line skeleton-price" /></div>
  </div>)}</div>;
}
