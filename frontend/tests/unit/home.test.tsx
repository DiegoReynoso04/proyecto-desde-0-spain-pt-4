import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Home from "@/app/page";

describe("Página de inicio (provisional)", () => {
  it("tiene un único h1 y los landmarks principales", () => {
    render(<Home />);
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
    expect(screen.getByRole("banner")).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: "Principal" })).toBeInTheDocument();
    expect(screen.getByRole("main")).toHaveAttribute("id", "contenido");
    expect(screen.getByRole("contentinfo")).toBeInTheDocument();
  });

  it("deja claro que los talleres son presenciales", () => {
    render(<Home />);
    expect(screen.getByText("presenciales")).toBeInTheDocument();
  });
});
