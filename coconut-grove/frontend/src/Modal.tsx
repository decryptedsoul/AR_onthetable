import {useEffect, useRef} from 'react';
import type {ReactNode} from 'react';

export function Modal({id, className, titleId, onClose, children}: {
  id: string; className: string; titleId: string; onClose: () => void; children: ReactNode;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const dialog = ref.current!;
    const previous = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    dialog.showModal();
    return () => {dialog.close(); previous?.focus({preventScroll: true});};
  }, []);
  return <dialog ref={ref} id={id} className={className} aria-labelledby={titleId}
    onCancel={event => {event.preventDefault(); onClose();}}
    onClick={event => {
      if (event.target !== ref.current) return;
      const rect = ref.current.getBoundingClientRect();
      if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) onClose();
    }}>
    <button className="close-button" onClick={onClose} aria-label={id === 'dish-dialog' ? 'Close dish details' : 'Close information'}>×</button>
    {children}
  </dialog>;
}
