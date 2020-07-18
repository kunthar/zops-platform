export interface CreateProjectResponse {
  meta: {
    params: {
      indent: number;
    }
  },
  content: {
    name: string,
    description: string,
    id: string,
    userLimit: string,
    userUsed: string
  }
}
