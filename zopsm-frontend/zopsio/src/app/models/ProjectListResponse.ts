export interface ProjectListResponse {
  meta: {
    params: {
      indent: number
    }
  },
  content: [
    {
      name: string,
      description: string,
      id: string,
      userLimit: null,
      userUsed: null
    }
    ]
}
