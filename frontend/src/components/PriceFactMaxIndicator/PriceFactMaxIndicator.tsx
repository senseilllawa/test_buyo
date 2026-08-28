import { memo } from "react";
import { Tooltip } from "@mui/material";
import { formatMoney, getFactMaxColor } from "../../utils/math.ts";

// Scale is fact/max as a percentage, 0%..SCALE_CAP%. The "max" tick is fixed at 100%;
// the colored dot moves along the scale to the actual fact/max ratio.
const SCALE_CAP = 150;
const TRACK_WIDTH = 64;
const TRACK_X0 = 3;
const TRACK_Y = 10;

const COLORS: Record<string, string> = {
  green: "#2e7d32",
  yellow: "#f5a623",
  red: "#d32f2f",
  gray: "#bdbdbd",
};

const posOnTrack = (percentage: number) => {
  const capped = Math.min(Math.max(percentage, 0), SCALE_CAP);
  return TRACK_X0 + (capped / SCALE_CAP) * TRACK_WIDTH;
};

const PriceFactMaxIndicator = ({ fact, max, ratio }: { fact: number; max: number; ratio: number | null }) => {
  const color = COLORS[getFactMaxColor(ratio)];
  const dotX = posOnTrack(ratio ?? 0);
  const maxTickX = posOnTrack(100);

  const tooltip = ratio === null
    ? "Нет данных для расчёта"
    : `Цена fact: ${formatMoney(fact)} / Цена max: ${formatMoney(max)} (${ratio > 999 ? ">" : ""}${Math.min(ratio, 999).toFixed(0)}%)`;

  return (
    <Tooltip title={tooltip} arrow>
      <span style={{ display: "inline-flex", alignItems: "center", gap: 6, whiteSpace: "nowrap" }}>
        <span>{formatMoney(fact)}</span>
        <svg width={TRACK_X0 * 2 + TRACK_WIDTH} height={20} style={{ flexShrink: 0 }}>
          <line x1={TRACK_X0} y1={TRACK_Y} x2={TRACK_X0 + TRACK_WIDTH} y2={TRACK_Y} stroke="#333" strokeWidth={2} />
          <line x1={maxTickX} y1={TRACK_Y - 6} x2={maxTickX} y2={TRACK_Y + 6} stroke="#333" strokeWidth={2} />
          <circle cx={dotX} cy={TRACK_Y} r={5} fill={color} stroke="#333" strokeWidth={1} />
        </svg>
        <span>{formatMoney(max)}</span>
      </span>
    </Tooltip>
  );
};

export default memo(PriceFactMaxIndicator);
