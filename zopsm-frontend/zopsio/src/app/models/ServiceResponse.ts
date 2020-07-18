export interface ServiceResponse {
  meta: {
    params: {
      indent: number;
    }
  },
  content: {
    id: string,
    itemLimit: number,
    itemUsed: number,
    name: string,
    description: string,
    serviceCatalogCode: string
  }
}
