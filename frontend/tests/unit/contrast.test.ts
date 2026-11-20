import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

import { contrastRatio } from "@/lib/contrast";
import {
  allowedPairs,
  colors,
  forbiddenTextPairs,
  MIN_CONTRAST,
  type ColorPair,
} from "@/lib/design-tokens";

const hexOf = (token: ColorPair["foreground"]) => (token === "white" ? "#FFFFFF" : colors[token]);

describe("contrastRatio (fórmula WCAG 2.x)", () => {
  it("da 21:1 para negro sobre blanco y 1:1 para el mismo color", () => {
    expect(contrastRatio("#000000", "#FFFFFF")).toBeCloseTo(21, 5);
    expect(contrastRatio("#733F2D", "#733F2D")).toBeCloseTo(1, 5);
  });

  it("reproduce los contrastes documentados del prompt", () => {
    expect(contrastRatio(colors["cacao-700"], colors["crema-50"])).toBeCloseTo(7.57, 1);
    expect(contrastRatio(colors["tinta-900"], colors["ocre-400"])).toBeCloseTo(7.11, 1);
    expect(contrastRatio("#FFFFFF", colors["ocre-400"])).toBeCloseTo(2.32, 1);
    expect(contrastRatio(colors["ocre-400"], colors["crema-50"])).toBeCloseTo(2.07, 1);
    expect(contrastRatio(colors["terracota-500"], colors["crema-50"])).toBeCloseTo(3.67, 1);
  });

  it("rechaza colores mal formados", () => {
    expect(() => contrastRatio("red", "#FFFFFF")).toThrow(/no válido/);
  });
});

describe("pares de color de la interfaz", () => {
  it.each(allowedPairs)(
    "$foreground sobre $background cumple el mínimo para $usage ($note)",
    (pair) => {
      const ratio = contrastRatio(hexOf(pair.foreground), colors[pair.background]);
      expect(ratio).toBeGreaterThanOrEqual(MIN_CONTRAST[pair.usage]);
    },
  );

  it.each(forbiddenTextPairs)(
    "$foreground sobre $background está prohibido para texto ($note)",
    (pair) => {
      const ratio = contrastRatio(hexOf(pair.foreground), colors[pair.background]);
      expect(ratio).toBeLessThan(MIN_CONTRAST.text);
    },
  );
});

describe("tokens de Tailwind (@theme en globals.css)", () => {
  // Vitest se ejecuta desde frontend/ (raíz del proyecto Next).
  const css = readFileSync(resolve(process.cwd(), "app/globals.css"), "utf8");

  it.each(Object.entries(colors))("--color-%s coincide con design-tokens.ts", (token, hex) => {
    const match = new RegExp(`--color-${token}:\\s*(#[0-9a-fA-F]{6})`).exec(css);
    expect(match, `falta --color-${token} en globals.css`).not.toBeNull();
    expect(match?.[1].toUpperCase()).toBe(hex.toUpperCase());
  });
});
