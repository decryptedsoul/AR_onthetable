export const money = (minor: number, currency = 'PKR') => currency === 'PKR'
  ? `Rs. ${new Intl.NumberFormat('en-PK', {maximumFractionDigits: 2}).format(minor / 100)}`
  : new Intl.NumberFormat('en', {style: 'currency', currency}).format(minor / 100);

export const spiceLabel = (level: number) => ['No added heat', 'Mild', 'Medium', 'Hot', 'Very hot', 'Extra hot'][level] || 'Unknown';
