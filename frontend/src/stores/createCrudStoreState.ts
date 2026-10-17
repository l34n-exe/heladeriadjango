import { ref, type Ref } from "vue";
import ApiService from "../services/ApiService";

export function createCrudStoreState<T extends Record<string, any>>(
  resource: string,
  defaultItem: T,
) {
  const items = ref([] as T[]) as Ref<T[]>;
  const selected = ref({ ...defaultItem } as T) as Ref<T>;

  function upsert(item: T) {
    const index = items.value.findIndex((current) => current.id === item.id);

    if (index === -1) {
      items.value.push(item);
      return;
    }

    items.value[index] = item;
  }

  async function getAll() {
    const data = (await ApiService.getAll(resource)) as T[] | null;
    if (data) {
      items.value = data;
    }
  }

  async function getOne(id: number | string) {
    const data = (await ApiService.getOne(resource, id)) as T | null;
    if (data) {
      selected.value = data;
    }
  }

  async function create(payload: T) {
    const data = (await ApiService.create(
      resource,
      payload as object,
    )) as T | null;

    if (data) {
      selected.value = data;
      upsert(data);
      return;
    }

    selected.value = payload;
    await getAll();
  }

  async function update(payload: T) {
    if (!payload.id) {
      return;
    }

    const data = (await ApiService.update(
      resource,
      payload.id,
      payload as object,
    )) as T | null;

    const nextItem = data ?? payload;
    selected.value = nextItem;
    upsert(nextItem);
  }

  async function destroy(id: number | string) {
    await ApiService.destroy(resource, id);
    items.value = items.value.filter((item) => item.id !== id);
  }

  return {
    items,
    selected,
    upsert,
    getAll,
    getOne,
    create,
    update,
    destroy,
  };
}
