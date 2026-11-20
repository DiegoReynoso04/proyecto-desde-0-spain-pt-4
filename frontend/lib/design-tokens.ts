/**
 * Paleta de TallerYA. Debe coincidir con los tokens de `app/globals.css` (@theme).
 * Un test comprueba ambas cosas: que coinciden y que los pares cumplen WCAG 2.2 AA.
 */
export const colors = {
  "ocre-400": "#D99F59",
  "ocre-300": "#D99962",
  "terracota-500": "#A67153",
  "cacao-700": "#733F2D",
  "crema-50": "#F2F2F2",
  "tinta-900": "#1F1F1F",
} as const;

export type ColorToken = keyof typeof colors;

/** Uso de un par texto/fondo: determina el contraste mínimo exigido. */
export type ContrastUsage = "text" | "large-text-or-ui";

export const MIN_CONTRAST: Record<ContrastUsage, number> = {
  text: 4.5,
  "large-text-or-ui": 3,
};

export interface ColorPair {
  foreground: ColorToken | "white";
  background: ColorToken;
  usage: ContrastUsage;
  note: string;
}

/** Pares permitidos en la interfaz. Añade aquí cualquier combinación nueva. */
export const allowedPairs: ColorPair[] = [
  {
    foreground: "cacao-700",
    background: "crema-50",
    usage: "text",
    note: "texto principal, enlaces, encabezados",
  },
  {
    foreground: "tinta-900",
    background: "ocre-400",
    usage: "text",
    note: "texto de botones primarios",
  },
  {
    foreground: "tinta-900",
    background: "ocre-300",
    usage: "text",
    note: "texto de botones en hover",
  },
  {
    foreground: "tinta-900",
    background: "crema-50",
    usage: "text",
    note: "texto sobre fondo general",
  },
  {
    foreground: "terracota-500",
    background: "crema-50",
    usage: "large-text-or-ui",
    note: "texto grande, iconos y bordes",
  },
  {
    foreground: "cacao-700",
    background: "crema-50",
    usage: "large-text-or-ui",
    note: "anillo de foco",
  },
];

/** Pares prohibidos para texto (documentados para que nadie los use). */
export const forbiddenTextPairs: ColorPair[] = [
  { foreground: "white", background: "ocre-400", usage: "text", note: "blanco sobre ocre" },
  {
    foreground: "ocre-400",
    background: "crema-50",
    usage: "text",
    note: "ocre como color de texto",
  },
  {
    foreground: "terracota-500",
    background: "crema-50",
    usage: "text",
    note: "terracota en texto de párrafo",
  },
];
