export interface CreateServiceResponse {
  meta: {
    params: {
      indent: number;
    }
  },
  content: {
    id: string,
    itemLimit: number,
    name: string,
    description: string,
    serviceCatalogCode: string
  }
}
