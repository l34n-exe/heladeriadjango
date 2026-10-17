import { describe, expect, it, vi } from "vitest";
import ApiService from "../services/ApiService";
import { createCrudStoreState } from "./createCrudStoreState";

describe("createCrudStoreState", () => {
  it("actualiza la lista sin duplicados y elimina por id", async () => {
    const destroySpy = vi.spyOn(ApiService, "destroy").mockResolvedValue();
    const store = createCrudStoreState<{ id: number; nombre: string }>(
      "clientes",
      { id: 0, nombre: "" },
    );

    store.upsert({ id: 1, nombre: "Ana" });
    store.upsert({ id: 2, nombre: "Luis" });
    store.upsert({ id: 1, nombre: "Ana updated" });

    expect(store.items.value).toHaveLength(2);
    expect(store.items.value[0]).toEqual({ id: 1, nombre: "Ana updated" });

    await store.destroy(2);
    expect(destroySpy).toHaveBeenCalledWith("clientes", 2);
    expect(store.items.value).toHaveLength(1);
    expect(store.items.value[0].id).toBe(1);
  });
});
