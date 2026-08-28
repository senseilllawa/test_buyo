export const round = (val: number) => Math.round(val * 100) / 100;

export const safeAvg = (sum: number, count: number) => count > 0 ? round(sum / count) : 0;

export const safePercentage = (count: number, all_count: number) => count > 0 ? round(count * 100 / all_count) : 0;

export const renderThreeFixed = (first?: any, second?: any, third?: any, suffix = "") => `${first.toFixed(2)}${second ? `/${second.toFixed(2)}` : ""}${third ? `/${third.toFixed(2)}` : ""}${suffix}`;
export const renderCRThreeFixed = (first?: any, first_cond?: any, second?: any,  third?: any, suffix = "") => `${first_cond ? first.toFixed(2) : "—"}${second ? `/${second.toFixed(2)}` : ""}${third ? `/${third.toFixed(2)}` : ""}${first_cond || second || third ? suffix : ""}`;
export const renderThree = (first?: any, second?: any, third?: any, suffix = "") => `${first}${second ? `/${second}` : ""}${third ? `/${third}` : ""}${suffix}`;

// Max allowed cost per approve, as a share of the average check.
export const FACT_MAX_KPI_RATE = 0.25;

// fact = spend / approves. No approves: Infinity if there's spend (worst case), else 0.
export const getFactPrice = (spend: number, approvesCount: number): number =>
  approvesCount > 0 ? spend / approvesCount : (spend > 0 ? Infinity : 0);

// max = avg check ($) * 25%.
export const getMaxPrice = (usdMedian: number): number => usdMedian * FACT_MAX_KPI_RATE;

// fact/max as a percentage. null = no data (both are zero).
export const getFactMaxRatio = (fact: number, max: number): number | null => {
  if (fact === 0 && max === 0) return null;
  if (max <= 0) return fact > 0 ? Infinity : 0;
  return (fact / max) * 100;
};

export type FactMaxColor = "green" | "yellow" | "red" | "gray";

// green < 80%, yellow 80-99.99%, red >= 100%.
export const getFactMaxColor = (ratio: number | null): FactMaxColor => {
  if (ratio === null) return "gray";
  if (ratio < 80) return "green";
  if (ratio < 100) return "yellow";
  return "red";
};

// Overspend beyond the max allowed price.
// approves > 0 and fact > max: (max - fact) * approves (negative).
// approves > 0 and fact <= max: 0.
// no approves but spend > 0: the whole spend is a loss.
export const getMinus = (fact: number, max: number, approvesCount: number, spend: number): number => {
  if (approvesCount > 0) {
    return fact > max ? round((max - fact) * approvesCount) : 0;
  }
  return spend > 0 ? -round(spend) : 0;
};

export const getFactMaxData = (spend: number, approvesCount: number, usdMedian: number) => {
  const fact = getFactPrice(spend, approvesCount);
  const max = getMaxPrice(usdMedian);
  const ratio = getFactMaxRatio(fact, max);
  const minus = getMinus(fact, max, approvesCount, spend);

  return { price_fact: fact, price_max: max, price_ratio: ratio, minus };
};

export const formatMoney = (val: number) => (val === Infinity ? "—" : `${val.toFixed(2)}$`);
