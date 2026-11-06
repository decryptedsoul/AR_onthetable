import {Modal} from './Modal';

export function Info({kind, dishName, onClose}: {kind: 'ar' | 'credits'; dishName?: string; onClose: () => void}) {
  return <Modal id="info-dialog" className="info-dialog" titleId="info-title" onClose={onClose}>
    {kind === 'ar' ? <>
      <span className="planned-label">Table preview · Planned</span><h2 id="info-title">{dishName ? `Preview ${dishName}` : 'A dish on your table'}</h2>
      <p>Table placement is not available in this concept yet. No camera access is requested.</p><p>Before it goes live, we need:</p>
      <ul><li>Restaurant-approved 3D models for each dish and portion.</li><li>Measured serving dimensions for a credible life-sized preview.</li><li>AR integration and testing on supported iPhone and Android devices.</li></ul>
      <p>Dish photos, ingredients and portion information remain available while AR is being prepared.</p><button className="button" id="info-done" onClick={onClose}>{dishName ? 'Back to dish' : 'Keep exploring'}</button>
    </> : <>
      <h2 id="info-title">About this concept</h2><p>A proposed website for Coconut Grove, Karachi. This concept is not an ordering or reservation service.</p>
      <p><strong>Menu reference:</strong> published dish names and reference prices come from the MenuPak listing, checked 6 November 2026. Current prices and availability need confirmation. Full ingredients, timing, portions and spice levels are pending. The review form is a local demonstration.</p>
      <p><strong>Planned:</strong> Restaurant dish models and calibrated AR, live availability, verified reviews, accounts, staff publishing and kitchen integrations.</p>
      <p><strong>Photography:</strong> restaurant reference image via <a href="https://foodoplanet.com/listing/coconut-grove/" target="_blank" rel="noopener noreferrer">FoodoPlanet</a>. Representative food photography via <a href="https://unsplash.com" target="_blank" rel="noopener noreferrer">Unsplash</a>. Food photos are illustrative, not verified Coconut Grove servings. Production needs approved restaurant photography and usage rights for the interior image.</p>
      <p><strong>Working demo:</strong> interactive 3D and supported-device AR use a CC0 avocado sample from Microsoft via Khronos. It is not a restaurant dish. The model is loaded only on the Preview page.</p><p><a href="https://www.menupak.com/m/coconut-grove-karachi" target="_blank" rel="noopener noreferrer">View published menu reference</a>. Visitor story and video sources are linked beside their content.</p><p>Brand reference: <a href="https://www.instagram.com/cgpakistanofficial/" target="_blank" rel="noopener noreferrer">@cgpakistanofficial</a>.</p>
    </>}
  </Modal>;
}
