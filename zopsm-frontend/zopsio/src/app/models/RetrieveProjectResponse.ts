export interface RetrieveProjectResponse {
  meta: {
    params: {
      indent: number
    }
  },
  content: {
    name: string,
    description: string,
    id: string,
    services: [string],
    userLimit: number,
    userUsed: number
  }
}
