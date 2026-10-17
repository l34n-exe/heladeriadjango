import { describe, expect, it } from "vitest";
import ApiService from "./ApiService";

describe("ApiService", () => {
  it("normaliza la URL del recurso sin barras duplicadas", () => {
    expect(ApiService.buildResourceUrl("clientes")).toBe("clientes");
    expect(ApiService.buildResourceUrl("clientes/")).toBe("clientes");
    expect(ApiService.buildResourceUrl("/clientes/")).toBe("clientes");
  });

  it("genera la ruta de un recurso individual sin duplicar segmentos", () => {
    expect(ApiService.buildResourceUrl("clientes", 42)).toBe("clientes/42");
    expect(ApiService.buildResourceUrl("clientes/", 42)).toBe("clientes/42");
  });
});
