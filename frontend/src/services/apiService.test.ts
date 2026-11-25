import { describe, expect, it, vi } from "vitest";

const { get, post } = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }));
vi.mock("../plugins/axios", () => ({ instance: { get, post } }));

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

  it("getAll junta todas las páginas de una respuesta paginada", async () => {
    get.mockReset();
    get
      .mockResolvedValueOnce({
        data: { count: 3, next: "http://api/ventas/?page=2", results: [{ id: 1 }, { id: 2 }] },
      })
      .mockResolvedValueOnce({
        data: { count: 3, next: null, results: [{ id: 3 }] },
      });

    const items = await ApiService.getAll("ventas");

    expect(get).toHaveBeenNthCalledWith(1, "ventas/");
    expect(get).toHaveBeenNthCalledWith(2, "http://api/ventas/?page=2");
    expect(items).toEqual([{ id: 1 }, { id: 2 }, { id: 3 }]);
  });

  it("getAll devuelve tal cual una respuesta no paginada", async () => {
    get.mockReset();
    get.mockResolvedValueOnce({ data: [{ id: 1 }] });

    expect(await ApiService.getAll("ventas")).toEqual([{ id: 1 }]);
  });

  it("postAction llama por POST a la acción del recurso", async () => {
    post.mockReset();
    post.mockResolvedValueOnce({ data: { id: 7, estado: "COMPLETADA" } });

    const data = await ApiService.postAction("ventas", 7, "completar");

    expect(post).toHaveBeenCalledWith("ventas/7/completar/", {});
    expect(data).toEqual({ id: 7, estado: "COMPLETADA" });
  });
});
