import { instance as axios } from "../plugins/axios";

class ApiService {
  static buildResourceUrl(resource: string, id?: number | string): string {
    const cleanResource = String(resource ?? "")
      .trim()
      .replace(/^\/+|\/+$/g, "");

    if (!cleanResource) {
      return "";
    }

    if (id === undefined || id === null || id === "") {
      return cleanResource;
    }

    return `${cleanResource}/${String(id)}`;
  }

  static buildCollectionUrl(resource: string): string {
    const cleanResource = this.buildResourceUrl(resource);
    return cleanResource ? `${cleanResource}/` : "/";
  }

  static buildItemUrl(resource: string, id: number | string): string {
    const cleanResource = this.buildResourceUrl(resource, id);
    return cleanResource ? `${cleanResource}/` : "/";
  }

  static async getAll(url: string) {
    const response = await axios.get(this.buildCollectionUrl(url));
    return response.data;
  }

  static async getOne(url: string, id: number | string) {
    const response = await axios.get(this.buildItemUrl(url, id));
    return response.data;
  }

  static async create(url: string, data: object) {
    const response = await axios.post(this.buildCollectionUrl(url), data);
    return response.data;
  }

  static async update(url: string, id: number | string, data: object) {
    const response = await axios.put(this.buildItemUrl(url, id), data);
    return response.data;
  }

  static async destroy(url: string, id: number | string): Promise<void> {
    await axios.delete(this.buildItemUrl(url, id));
  }

  static async putAction(
    url: string,
    id: number | string,
    action: string,
    data: object = {},
  ) {
    const resourcePath = this.buildResourceUrl(url, id);
    const response = await axios.put(`${resourcePath}/${action}/`, data);
    return response.data;
  }
}

export default ApiService;
